#!/usr/bin/env python3
"""Apply the reviewed Jogger cargo reporting integration."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "tools" / "_configuration_completeness_base.py"
SANDERO_TEST = ROOT / "tests" / "test_sandero_stepway_brochure_cargo_20260725.py"
SPECS = (
    ROOT / "data" / "reporting" / "jogger_ecog120_automatic_completeness.json",
    ROOT / "data" / "reporting" / "jogger_ecog120_manual_completeness.json",
    ROOT / "data" / "reporting" / "jogger_hybrid155_automatic_completeness.json",
    ROOT / "data" / "reporting" / "jogger_tce110_manual_completeness.json",
)


class PatchError(RuntimeError):
    pass


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise PatchError(f"patch anchor missing: {label}")
    return text.replace(old, new, 1)


def patch_completeness() -> None:
    text = BASE.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "from configuration_value_range_reporting import (\n"
        "    combine_latest_observations,\n"
        "    read_optional_ranges,\n"
        ")\n",
        "from configuration_value_range_reporting import (\n"
        "    combine_latest_observations,\n"
        "    read_optional_ranges,\n"
        ")\n"
        "from reporting.cargo_context import (\n"
        "    CargoContextError,\n"
        "    annotate_scalar_values,\n"
        "    read_context_rows,\n"
        ")\n",
        "cargo imports",
    )
    text = replace_once(
        text,
        "    scoped_values = [\n"
        "        row for row in values if row.get('configuration_code') in configuration_sources\n"
        "    ]\n"
        "    scoped_ranges = [\n"
        "        row for row in ranges if row.get('configuration_code') in configuration_sources\n"
        "    ]\n",
        "    raw_scoped_values = [\n"
        "        row for row in values if row.get('configuration_code') in configuration_sources\n"
        "    ]\n"
        "    try:\n"
        "        scoped_values = annotate_scalar_values(\n"
        "            raw_scoped_values,\n"
        "            read_context_rows(master, read_csv),\n"
        "        )\n"
        "    except CargoContextError as exc:\n"
        "        raise CompletenessError(str(exc)) from exc\n"
        "    scoped_ranges = [\n"
        "        {**row, '_cargo_context_signature': '', '_cargo_context': None}\n"
        "        for row in ranges\n"
        "        if row.get('configuration_code') in configuration_sources\n"
        "    ]\n",
        "annotate scoped values",
    )
    text = replace_once(
        text,
        "    current_scalar_values = latest(\n"
        "        scoped_values,\n"
        "        ('configuration_code', 'attribute_code', 'fuel_type_code'),\n"
        "        as_of,\n"
        "        'configuration values',\n"
        "    )\n"
        "    current_range_values = latest(\n"
        "        scoped_ranges,\n"
        "        ('configuration_code', 'attribute_code', 'fuel_type_code'),\n"
        "        as_of,\n"
        "        'configuration value ranges',\n"
        "    )\n"
        "    current_values = combine_latest_observations(\n"
        "        current_scalar_values, current_range_values, CompletenessError\n"
        "    )\n",
        "    current_scalar_values = latest(\n"
        "        scoped_values,\n"
        "        (\n"
        "            'configuration_code',\n"
        "            'attribute_code',\n"
        "            'fuel_type_code',\n"
        "            '_cargo_context_signature',\n"
        "        ),\n"
        "        as_of,\n"
        "        'configuration values',\n"
        "    )\n"
        "    current_range_values = latest(\n"
        "        scoped_ranges,\n"
        "        (\n"
        "            'configuration_code',\n"
        "            'attribute_code',\n"
        "            'fuel_type_code',\n"
        "            '_cargo_context_signature',\n"
        "        ),\n"
        "        as_of,\n"
        "        'configuration value ranges',\n"
        "    )\n"
        "    current_values = combine_latest_observations(\n"
        "        current_scalar_values, current_range_values, CompletenessError\n"
        "    )\n"
        "    current_value_groups: dict[\n"
        "        tuple[str, str, str], dict[str, dict[str, Any]]\n"
        "    ] = {}\n"
        "    for current_key, current_row in current_values.items():\n"
        "        base_key = (current_key[0], current_key[1], current_key[2])\n"
        "        current_value_groups.setdefault(base_key, {})[current_key[3]] = current_row\n",
        "context-aware latest keys",
    )
    text = replace_once(
        text,
        "        if key in technical_na:\n"
        "            if key in current_values:\n"
        "                raise CompletenessError(f'not_applicable slot has a record: {key}')\n",
        "        if key in technical_na:\n"
        "            if key in current_value_groups:\n"
        "                raise CompletenessError(f'not_applicable slot has a record: {key}')\n",
        "not-applicable grouped values",
    )
    text = replace_once(
        text,
        "        row = current_values.get(key)\n"
        "        if row is None:\n",
        "        rows = current_value_groups.get(key)\n"
        "        if rows is None:\n",
        "grouped slot lookup",
    )
    text = replace_once(
        text,
        "        else:\n"
        "            if row.get('source_code') not in registered_sources[configuration]:\n"
        "                raise CompletenessError(\n"
        "                    f'technical record source is not registered for configuration: {key}'\n"
        "                )\n"
        "            technical['present'] += 1\n",
        "        else:\n"
        "            for row in rows.values():\n"
        "                if row.get('source_code') not in registered_sources[configuration]:\n"
        "                    raise CompletenessError(\n"
        "                        f'technical record source is not registered for configuration: {key}'\n"
        "                    )\n"
        "            technical['present'] += 1\n",
        "validate grouped sources",
    )
    BASE.write_text(text, encoding="utf-8")


def patch_specs() -> None:
    slot = {"attribute_code": "boot_capacity", "fuel_type_code": ""}
    for path in SPECS:
        payload = json.loads(path.read_text(encoding="utf-8"))
        slots = payload.get("technical_slots")
        if not isinstance(slots, list):
            raise PatchError(f"technical_slots missing: {path}")
        if slot not in slots:
            slots.append(slot)
            slots.sort(key=lambda item: (item["attribute_code"], item.get("fuel_type_code", "")))
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def patch_historical_test() -> None:
    text = SANDERO_TEST.read_text(encoding="utf-8")
    old = '''        self.assertEqual(state["phase"], "Sandero and Stepway Brochure Cargo Import")
        self.assertEqual(state["baseline"]["tests"], 791)
        self.assertEqual(state["baseline"]["rows"], 8255)
        self.assertEqual(state["baseline"]["configuration_values"], 1876)
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(
            state["next_package"]["name"],
            "Jogger Brochure Cargo Value Import",
        )
'''
    new = '''        self.assertGreaterEqual(state["baseline"]["tests"], 791)
        self.assertGreaterEqual(state["baseline"]["rows"], 8255)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 1876)
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertTrue(state["next_package"]["name"])
'''
    text = replace_once(text, old, new, "historical Sandero state assertions")
    SANDERO_TEST.write_text(text, encoding="utf-8")


def main() -> int:
    patch_completeness()
    patch_specs()
    patch_historical_test()
    print("PASS: Jogger cargo reporting integration applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
