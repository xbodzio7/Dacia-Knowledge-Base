#!/usr/bin/env python3
"""Materialize D-024 selected-gear schema and reporting support."""

from __future__ import annotations

import csv
import json
import os
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALUES = ROOT / "data" / "master" / "configuration_attribute_values.csv"


class PatchError(RuntimeError):
    pass


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise PatchError(f"anchor missing in {path}: {old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_all(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        return
    path.write_text(text.replace(old, new), encoding="utf-8")


def migrate_master_values() -> None:
    with VALUES.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    expected_old = [
        "id", "code", "configuration_code", "attribute_code",
        "fuel_type_code", "value", "observation_date", "source_code", "notes",
    ]
    expected_new = [
        "id", "code", "configuration_code", "attribute_code",
        "fuel_type_code", "gear_number", "value", "observation_date",
        "source_code", "notes",
    ]
    if fields == expected_old:
        for row in rows:
            row["gear_number"] = ""
    elif fields == expected_new:
        for row in rows:
            row.setdefault("gear_number", "")
    else:
        raise PatchError(f"unexpected configuration value header: {fields!r}")
    descriptor, temporary = tempfile.mkstemp(prefix=".configuration-values.", suffix=".csv", dir=VALUES.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=expected_new, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, VALUES)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def patch_value_field_sequences() -> None:
    roots = [ROOT / "tools", ROOT / "tests", ROOT / "scripts"]
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            if path.name == Path(__file__).name:
                continue
            text = path.read_text(encoding="utf-8")
            updated = re.sub(
                r'("fuel_type_code",\n(?P<indent>\s*))"value",',
                r'\1"gear_number",\n\g<indent>"value",',
                text,
            )
            updated = updated.replace(
                '"fuel_type_code", "value"',
                '"fuel_type_code", "gear_number", "value"',
            )
            updated = re.sub(
                r'(?P<indent>\s*)"fuel_type_code": (?P<expr>[^\n]+),\n(?P=indent)"value":',
                r'\g<indent>"fuel_type_code": \g<expr>,\n\g<indent>"gear_number": "",\n\g<indent>"value":',
                updated,
            )
            if updated != text:
                path.write_text(updated, encoding="utf-8")


def patch_importer() -> None:
    path = ROOT / "tools" / "import_configuration_values.py"
    replace_once(path, 'ROW_OPTIONAL_KEYS = {"fuel_type_code"}', 'ROW_OPTIONAL_KEYS = {"fuel_type_code", "gear_number"}')
    replace_once(path, '    "fuel_type_code",\n}', '    "fuel_type_code",\n    "gear_number",\n}')
    replace_once(path, '    fuel_type_code: str | None = None\n', '    fuel_type_code: str | None = None\n    gear_number: str | None = None\n')
    replace_once(path, '    fuel_type_code: str\n    source_page: int\n', '    fuel_type_code: str\n    gear_number: str\n    source_page: int\n')
    replace_once(
        path,
        'SPEC_KIND = "configuration_attribute_values"\n',
        'SPEC_KIND = "configuration_attribute_values"\nGEAR_ELIGIBLE_ATTRIBUTES = frozenset({"elasticity_80_120"})\nGEAR_PATTERN = re.compile(r"[1-9][0-9]*")\n',
    )
    replace_once(
        path,
        'def _validate_iso_date(value: str, label: str) -> str:\n',
        'def _validate_gear_number(value: str, label: str) -> str:\n    _ensure(\n        value == "" or GEAR_PATTERN.fullmatch(value) is not None,\n        f"{label} must be empty or a canonical positive integer",\n    )\n    return value\n\n\ndef _validate_iso_date(value: str, label: str) -> str:\n',
    )
    replace_once(path, '_strict_keys(payload, TOP_LEVEL_KEYS, label="spec")', '_strict_keys(payload, TOP_LEVEL_KEYS, label="spec", optional={"gear_number"})')
    replace_once(
        path,
        '        row_fuel = item.get("fuel_type_code")\n        if row_fuel is not None:\n            row_fuel = _require_string(\n                row_fuel,\n                f"{label}.fuel_type_code",\n                allow_empty=True,\n            )\n        semantic_key = (\n            configuration_code,\n            "" if row_fuel is None else row_fuel,\n        )\n',
        '        row_fuel = item.get("fuel_type_code")\n        if row_fuel is not None:\n            row_fuel = _require_string(\n                row_fuel,\n                f"{label}.fuel_type_code",\n                allow_empty=True,\n            )\n        row_gear = item.get("gear_number")\n        if row_gear is not None:\n            row_gear = _validate_gear_number(\n                _require_string(\n                    row_gear,\n                    f"{label}.gear_number",\n                    allow_empty=True,\n                ),\n                f"{label}.gear_number",\n            )\n        semantic_key = (\n            configuration_code,\n            "" if row_fuel is None else row_fuel,\n            "" if row_gear is None else row_gear,\n        )\n',
    )
    replace_once(path, '    seen_configurations: set[tuple[str, str]] = set()', '    seen_configurations: set[tuple[str, str, str]] = set()')
    replace_once(path, '                fuel_type_code=row_fuel,\n            )', '                fuel_type_code=row_fuel,\n                gear_number=row_gear,\n            )')
    replace_once(
        path,
        '        fuel_type_code=_require_string(\n            payload["fuel_type_code"],\n            "fuel_type_code",\n            allow_empty=True,\n        ),\n        source_page=',
        '        fuel_type_code=_require_string(\n            payload["fuel_type_code"],\n            "fuel_type_code",\n            allow_empty=True,\n        ),\n        gear_number=_validate_gear_number(\n            _require_string(\n                payload.get("gear_number", ""),\n                "gear_number",\n                allow_empty=True,\n            ),\n            "gear_number",\n        ),\n        source_page=',
    )
    replace_once(path, '            fuel_type_code="",\n        )', '            fuel_type_code="",\n            gear_number="",\n        )')
    replace_once(
        path,
        'def _row_code(\n    configuration_code: str,\n    attribute_code: str,\n    fuel_type_code: str,\n    observation_date: str,\n) -> str:\n    parts = [configuration_code, attribute_code]\n    if fuel_type_code:\n        parts.append(fuel_type_code)\n    parts.append(observation_date.replace("-", ""))\n',
        'def _row_code(\n    configuration_code: str,\n    attribute_code: str,\n    fuel_type_code: str,\n    gear_number: str,\n    observation_date: str,\n) -> str:\n    parts = [configuration_code, attribute_code]\n    if fuel_type_code:\n        parts.append(fuel_type_code)\n    if gear_number:\n        parts.append(f"gear{gear_number}")\n    parts.append(observation_date.replace("-", ""))\n',
    )
    replace_once(
        path,
        '        fuel = spec.fuel_type_code if row.fuel_type_code is None else row.fuel_type_code\n        if fuel:\n',
        '        fuel = spec.fuel_type_code if row.fuel_type_code is None else row.fuel_type_code\n        gear = spec.gear_number if row.gear_number is None else row.gear_number\n        if gear:\n            _ensure(\n                spec.attribute_code in GEAR_ELIGIBLE_ATTRIBUTES,\n                f"{label} uses gear_number for ineligible attribute {spec.attribute_code!r}",\n            )\n        if fuel:\n',
    )
    replace_once(path, '            fuel_type_code=fuel,\n        )', '            fuel_type_code=fuel,\n            gear_number=gear,\n        )')
    replace_once(path, '                    fuel,\n                    spec.observation_date,', '                    fuel,\n                    gear,\n                    spec.observation_date,')
    replace_once(path, '                "fuel_type_code": fuel,\n                "gear_number": "",\n                "value": row.value,', '                "fuel_type_code": fuel,\n                "gear_number": gear,\n                "value": row.value,')
    replace_all(path, '            row["fuel_type_code"],\n            row["observation_date"],', '            row["fuel_type_code"],\n            row["gear_number"],\n            row["observation_date"],')
    replace_all(path, '            row["fuel_type_code"],\n            row["observation_date"],\n        ): row', '            row["fuel_type_code"],\n            row["gear_number"],\n            row["observation_date"],\n        ): row')


def patch_context_reporting() -> None:
    path = ROOT / "tools" / "reporting" / "cargo_context.py"
    replace_once(
        path,
        'def technical_context(\n    fuel_type_code: str,\n    cargo_context: Mapping[str, str] | None = None,\n) -> str:\n    """Return the exact filter/export context for one technical observation."""\n\n    fuel = f"fuel_type_code={fuel_type_code}"\n    cargo = semantic_signature(cargo_context)\n    return fuel if not cargo else f"{fuel};{cargo}"\n',
        'def observation_signature(\n    gear_number: str = "",\n    cargo_context_signature: str = "",\n) -> str:\n    """Return the non-lossy context signature beyond attribute and fuel."""\n\n    parts: list[str] = []\n    if gear_number:\n        parts.append(f"gear_number={gear_number}")\n    if cargo_context_signature:\n        parts.append(cargo_context_signature)\n    return ";".join(parts)\n\n\ndef technical_context(\n    fuel_type_code: str,\n    cargo_context: Mapping[str, str] | None = None,\n    gear_number: str = "",\n) -> str:\n    """Return the exact filter/export context for one technical observation."""\n\n    parts = [f"fuel_type_code={fuel_type_code}"]\n    if gear_number:\n        parts.append(f"gear_number={gear_number}")\n    cargo = semantic_signature(cargo_context)\n    if cargo:\n        parts.append(cargo)\n    return ";".join(parts)\n',
    )
    replace_once(path, '                "fuel_type_code": str(row.get("fuel_type_code", "")),\n                "observation_date":', '                "fuel_type_code": str(row.get("fuel_type_code", "")),\n                "gear_number": str(row.get("gear_number", "")),\n                "observation_date":')
    replace_once(path, '                    context if isinstance(context, Mapping) else None,\n                ),', '                    context if isinstance(context, Mapping) else None,\n                    str(row.get("gear_number", "")),\n                ),')


def patch_comparison() -> None:
    path = ROOT / "tools" / "_configuration_comparison_base.py"
    replace_once(path, '    read_context_rows,\n    technical_context,', '    read_context_rows,\n    observation_signature,\n    technical_context,')
    replace_once(path, 'field not in {"fuel_type_code", "_cargo_context_signature"}', 'field not in {"fuel_type_code", "gear_number", "_cargo_context_signature"}')
    replace_once(path, '{**row, "_cargo_context_signature": "", "_cargo_context": None}', '{**row, "gear_number": "", "_cargo_context_signature": "", "_cargo_context": None}')
    replace_all(path, '            "fuel_type_code",\n            "_cargo_context_signature",', '            "fuel_type_code",\n            "gear_number",\n            "_cargo_context_signature",')
    replace_once(
        path,
        '    for key, row in current_values.items():\n        base_key = (key[0], key[1], key[2])\n        current_value_groups.setdefault(base_key, {})[key[3]] = row\n',
        '    for key, row in current_values.items():\n        base_key = (key[0], key[1], key[2])\n        signature = observation_signature(key[3], key[4])\n        current_value_groups.setdefault(base_key, {})[signature] = row\n',
    )
    replace_once(
        path,
        '                cargo_context = (\n                    dict(raw_context)\n                    if isinstance(raw_context, Mapping)\n                    else None\n                )\n\n                if left_key',
        '                cargo_context = (\n                    dict(raw_context)\n                    if isinstance(raw_context, Mapping)\n                    else None\n                )\n                gear_number = (\n                    str(context_row.get("gear_number", ""))\n                    if context_row is not None\n                    else ""\n                )\n                cargo_signature = (\n                    str(context_row.get("_cargo_context_signature", ""))\n                    if context_row is not None\n                    else ""\n                )\n\n                if left_key',
    )
    replace_all(path, 'left_state["cargo_context_signature"] = signature', 'left_state["cargo_context_signature"] = cargo_signature')
    replace_all(path, 'right_state["cargo_context_signature"] = signature', 'right_state["cargo_context_signature"] = cargo_signature')
    replace_once(
        path,
        '                if cargo_context is not None:\n                    technical_item["cargo_context"] = dict(cargo_context)\n                    technical_item["context"] = technical_context(\n                        fuel, cargo_context\n                    )\n',
        '                if gear_number:\n                    technical_item["gear_number"] = gear_number\n                    if left_state.get("state") == "recorded":\n                        left_state["gear_number"] = gear_number\n                    if right_state.get("state") == "recorded":\n                        right_state["gear_number"] = gear_number\n                if cargo_context is not None:\n                    technical_item["cargo_context"] = dict(cargo_context)\n                if cargo_context is not None or gear_number:\n                    technical_item["context"] = technical_context(\n                        fuel, cargo_context, gear_number\n                    )\n',
    )


def patch_context_consumers() -> None:
    path = ROOT / "tools" / "configuration_comparison_context.py"
    replace_once(path, '            cargo_context if isinstance(cargo_context, Mapping) else None,\n        )', '            cargo_context if isinstance(cargo_context, Mapping) else None,\n            str(item.get("gear_number", "")),\n        )')

    path = ROOT / "tools" / "configuration_comparison_item_catalog.py"
    replace_once(path, '                cargo_context if isinstance(cargo_context, Mapping) else None,\n            ),', '                cargo_context if isinstance(cargo_context, Mapping) else None,\n                str(item.get("gear_number", "")),\n            ),')

    path = ROOT / "tools" / "reporting" / "configuration_shortlist_html.py"
    replace_once(
        path,
        'def _comparison_key(\n    attribute_code: str,\n    fuel_type_code: str,\n    cargo_context_signature: str = "",\n) -> str:\n    base = f"{attribute_code}::{fuel_type_code or \'all\'}"\n    return (\n        base\n        if not cargo_context_signature\n        else f"{base}::cargo::{cargo_context_signature}"\n    )\n',
        'def _comparison_key(\n    attribute_code: str,\n    fuel_type_code: str,\n    cargo_context_signature: str = "",\n    gear_number: str = "",\n) -> str:\n    base = f"{attribute_code}::{fuel_type_code or \'all\'}"\n    if gear_number:\n        base = f"{base}::gear::{gear_number}"\n    return (\n        base\n        if not cargo_context_signature\n        else f"{base}::cargo::{cargo_context_signature}"\n    )\n',
    )
    replace_once(path, '    signature = str(row.get("_cargo_context_signature", ""))\n    return {\n        "key": _comparison_key(attribute_code, fuel_type_code, signature),', '    signature = str(row.get("_cargo_context_signature", ""))\n    gear_number = str(row.get("gear_number", ""))\n    return {\n        "key": _comparison_key(attribute_code, fuel_type_code, signature, gear_number),')
    replace_once(path, '        "fuel_type_label": _FUEL_LABELS_PL.get(fuel_type_code, fuel_type_code),\n        "cargo_context":', '        "fuel_type_label": _FUEL_LABELS_PL.get(fuel_type_code, fuel_type_code),\n        "gear_number": gear_number,\n        "cargo_context":')
    replace_once(path, '        "context": technical_context(fuel_type_code, context_payload),', '        "context": technical_context(fuel_type_code, context_payload, gear_number),')
    replace_once(path, '            "fuel_type_code",\n            "_cargo_context_signature",', '            "fuel_type_code",\n            "gear_number",\n            "_cargo_context_signature",')
    replace_once(path, '    for (configuration_code, attribute_code, _, _), row in latest_values.items():', '    for (configuration_code, attribute_code, _, _, _), row in latest_values.items():')
    replace_once(path, '            "fuel_type_code", "fuel_type_label", "cargo_context",', '            "fuel_type_code", "fuel_type_label", "gear_number", "cargo_context",')


def patch_gap_plan() -> None:
    path = ROOT / "tools" / "configuration_gap_resolution_plan.py"
    replace_all(path, 'tuple[str, str, str, str, str]', 'tuple[str, str, str, str, str, str]')
    replace_all(path, '            row.get("fuel_type_code", ""),\n            cargo_signatures.get(row.get("code", ""), ""),\n            row.get("observation_date", ""),', '            row.get("fuel_type_code", ""),\n            row.get("gear_number", ""),\n            cargo_signatures.get(row.get("code", ""), ""),\n            row.get("observation_date", ""),')
    replace_all(path, '                fuel_type_code,\n                "",\n                observation_date,', '                fuel_type_code,\n                "",\n                "",\n                observation_date,')


def patch_validation_pipeline() -> None:
    path = ROOT / "tools" / "validate_dkb.py"
    replace_once(path, 'from validators.csv_validator import validate_csv\n', 'from validators.csv_validator import validate_csv\nfrom validators.gear_contexts import validate_gear_contexts\n')
    replace_once(
        path,
        '    print("\\n5. Walidacja zakresów lat")\n',
        '    print("\\n5. Walidacja kontekstu wybranego biegu")\n    checked_gear_records, gear_context_errors = validate_gear_contexts(root)\n    gear_contexts_ok = not gear_context_errors\n    if gear_contexts_ok:\n        print(f"   ✅ OK ({checked_gear_records} rekordów)")\n    else:\n        print(f"   ❌ Wykryto {len(gear_context_errors)} problemów:")\n        for error in gear_context_errors:\n            print(f"      • {error}")\n\n    print("\\n6. Walidacja zakresów lat")\n',
    )
    for before, after in (("\\n6. Walidacja statusów", "\\n7. Walidacja statusów"), ("\\n7. Walidacja okresów", "\\n8. Walidacja okresów"), ("\\n8. Walidacja nakładających", "\\n9. Walidacja nakładających"), ("\\n9. Walidacja kontraktu", "\\n10. Walidacja kontraktu"), ("\\n10. Wykonywanie", "\\n11. Wykonywanie"), ("\\n11. Zbieranie", "\\n12. Zbieranie"), ("\\n12. Generowanie", "\\n13. Generowanie")):
        replace_once(path, before, after)
    replace_once(path, '        and year_ranges_ok\n', '        and gear_contexts_ok\n        and year_ranges_ok\n')

    report = ROOT / "tools" / "reporting" / "markdown_report.py"
    replace_once(report, '    references_ok: bool = True,\n    reference_errors: Sequence[str] = (),\n', '    references_ok: bool = True,\n    reference_errors: Sequence[str] = (),\n    gear_contexts_ok: bool = True,\n    gear_context_errors: Sequence[str] = (),\n')
    replace_once(report, '        and references_ok\n        and year_ranges_ok', '        and references_ok\n        and gear_contexts_ok\n        and year_ranges_ok')
    replace_once(report, '        handle.write(\n            f"- Year ranges: "', '        handle.write(\n            f"- Selected-gear context: "\n            f"**{\'PASS\' if gear_contexts_ok else \'FAIL\'}**\\n"\n        )\n        handle.write(\n            f"- Year ranges: "')
    replace_once(report, '        if year_range_errors:\n', '        if gear_context_errors:\n            handle.write("## Selected-gear context errors\\n\\n")\n            for error in gear_context_errors:\n                handle.write(f"- {error}\\n")\n            handle.write("\\n")\n\n        if year_range_errors:\n')
    replace_once(path, '        reference_errors=reference_errors,\n        year_ranges_ok=', '        reference_errors=reference_errors,\n        gear_contexts_ok=gear_contexts_ok,\n        gear_context_errors=gear_context_errors,\n        year_ranges_ok=')


def patch_historical_contracts() -> None:
    path = ROOT / "tests" / "test_brochure_gear_performance_context_model.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace('            "fuel_type_code",\n            "value",', '            "fuel_type_code",\n            "gear_number",\n            "value",')
    text = text.replace('        self.assertEqual(row_count, 2118)', '        self.assertEqual(row_count, 2118)\n        self.assertEqual({row.get("gear_number", "") for row in csv.DictReader(VALUES_PATH.open(encoding="utf-8-sig", newline=""))}, {""})')
    text = text.replace('        self.assertEqual(state["phase"], "Brochure Gear-Specific Performance Context Modeling")', '        self.assertEqual(state["current_package"]["status"], "complete")')
    text = text.replace('        self.assertEqual(state["baseline"]["tests"], 813)', '        self.assertGreaterEqual(state["baseline"]["tests"], 813)')
    path.write_text(text, encoding="utf-8")


def update_state() -> None:
    path = ROOT / "project" / "state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-26"
    state["phase"] = "Brochure Gear-Specific Performance Schema Foundation"
    state["baseline"]["tests"] = 821
    state["current_package"] = {
        "name": "Brochure Gear-Specific Performance Schema Foundation",
        "status": "complete",
        "goal": "Add the optional gear_number scalar-observation qualifier, validation, import-spec, SQLite, data-dictionary and reporting-key support without importing brochure elasticity values.",
    }
    state["next_package"] = {
        "name": "Brochure Gear-Specific Performance Value Import",
        "status": "planned",
        "goal": "Import exact Sandero, Stepway and Jogger 80-120 km/h elasticity observations with selected-gear, fuel and exact-configuration context.",
    }
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    migrate_master_values()
    patch_value_field_sequences()
    patch_importer()
    patch_context_reporting()
    patch_comparison()
    patch_context_consumers()
    patch_gap_plan()
    patch_validation_pipeline()
    patch_historical_contracts()
    update_state()
    print("PASS: selected-gear performance schema foundation materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
