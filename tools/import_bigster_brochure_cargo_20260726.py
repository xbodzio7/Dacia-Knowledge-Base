#!/usr/bin/env python3
"""Import exact context-aware Bigster brochure cargo values."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPEC_PATH = (
    ROOT
    / "data"
    / "imports"
    / "configuration_cargo_values"
    / "bigster-brochure-cargo-20251210.json"
)
VALUE_PATH = MASTER / "configuration_attribute_values.csv"
CONTEXT_PATH = MASTER / "configuration_cargo_volume_contexts.csv"
SOURCE_CONFIGURATION_PATH = MASTER / "source_configurations.csv"

VALUE_FIELDS = (
    "id",
    "code",
    "configuration_code",
    "attribute_code",
    "fuel_type_code",
    "value",
    "observation_date",
    "source_code",
    "notes",
)
CONTEXT_FIELDS = (
    "id",
    "code",
    "configuration_attribute_value_code",
    "measurement_basis_code",
    "second_row_state_code",
    "third_row_state_code",
    "compartment_code",
    "spare_wheel_state_code",
    "tyre_repair_kit_state_code",
    "double_floor_state_code",
    "notes",
)
SOURCE_CONFIGURATION_FIELDS = (
    "id",
    "source_code",
    "configuration_code",
    "relationship",
    "notes",
)
CONTEXT_FIELDS_FROM_SPEC = CONTEXT_FIELDS[3:-1]
RELATIONSHIP = "brochure_technical_data_for"
SOURCE_CODE = "src_pl_bigster_brochure_20251210"
SOURCE_FILE = "PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf"
SOURCE_SHA256 = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"
EXPECTED_GROUPS = {
    "mild_hybrid_g_140": {
        "powertrain_label": "mild hybrid-G 140 4x2",
        "configurations": 4,
        "repair": 4,
        "spare": 0,
        "values": {"609", "1877", "660", "1960"},
    },
    "mild_hybrid_140": {
        "powertrain_label": "mild hybrid 140 4x2",
        "configurations": 4,
        "repair": 4,
        "spare": 3,
        "values": {"667", "1937", "702", "2002", "624", "1894", "681", "1981"},
    },
    "hybrid_155": {
        "powertrain_label": "hybrid 155 4x2",
        "configurations": 3,
        "repair": 3,
        "spare": 3,
        "values": {"546", "1851", "612", "1912", "488", "1791", "566", "1866"},
    },
}
DEFERRED_4X4_CONFIGURATIONS = {
    "bigster_expression_hybridg150_4x4_automatic",
    "bigster_extreme_hybridg150_4x4_automatic",
    "bigster_journey_hybridg150_4x4_automatic",
}
DEFERRED_4X4_VALUES = {"444", "1712", "556", "1856"}


class ContractError(RuntimeError):
    """Raised when the reviewed Bigster brochure contract cannot be reproduced."""


def _ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        _ensure(reader.fieldnames is not None, f"missing CSV header: {path}")
        return list(reader)


def _require_header(path: Path, fields: Sequence[str]) -> None:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        header = next(csv.reader(handle), None)
    _ensure(header == list(fields), f"unexpected header in {path}: {header!r}")


def _write_rows_atomic(
    path: Path,
    fields: Sequence[str],
    rows: Iterable[Mapping[str, str]],
) -> None:
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_spec() -> dict[str, Any]:
    payload = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    _ensure(isinstance(payload, dict), "cargo import spec must be an object")
    _ensure(payload.get("version") == 1, "unsupported cargo import spec version")
    _ensure(payload.get("kind") == "configuration_cargo_values", "unsupported spec kind")
    _ensure(payload.get("value_id_start") == 1987, "unexpected value id start")
    _ensure(payload.get("context_id_start") == 156, "unexpected context id start")
    _ensure(payload.get("observation_date") == "2025-12-10", "unexpected date")
    _ensure(payload.get("source_page") == 20, "unexpected source page")
    _ensure(payload.get("source_code") == SOURCE_CODE, "unexpected source code")
    _ensure(payload.get("attribute_code") == "boot_capacity", "unexpected attribute")
    _ensure(
        payload.get("attribute_contract")
        == {"data_type": "integer", "unit": "L", "status": "active"},
        "unexpected boot_capacity contract",
    )

    groups = payload.get("groups")
    _ensure(isinstance(groups, list) and len(groups) == 3, "expected three import groups")
    seen_groups: set[str] = set()
    seen_configurations: set[str] = set()
    for group in groups:
        _ensure(isinstance(group, dict), "group must be an object")
        group_code = str(group.get("group_code", ""))
        expected = EXPECTED_GROUPS.get(group_code)
        _ensure(expected is not None and group_code not in seen_groups, f"invalid group: {group_code}")
        seen_groups.add(group_code)
        _ensure(group.get("powertrain_label") == expected["powertrain_label"], f"powertrain mismatch: {group_code}")
        configurations = group.get("configurations")
        repair = group.get("repair_kit_configurations")
        spare = group.get("spare_wheel_configurations")
        repair_observations = group.get("repair_kit_observations")
        spare_observations = group.get("spare_wheel_observations")
        for name, value in (
            ("configurations", configurations),
            ("repair_kit_configurations", repair),
            ("spare_wheel_configurations", spare),
            ("repair_kit_observations", repair_observations),
            ("spare_wheel_observations", spare_observations),
        ):
            _ensure(isinstance(value, list), f"{group_code}.{name} must be a list")
        _ensure(len(configurations) == expected["configurations"], f"configuration count mismatch: {group_code}")
        _ensure(len(repair) == expected["repair"], f"repair-kit scope mismatch: {group_code}")
        _ensure(len(spare) == expected["spare"], f"spare-wheel scope mismatch: {group_code}")
        _ensure(set(repair) <= set(configurations), f"repair-kit target outside group: {group_code}")
        _ensure(set(spare) <= set(configurations), f"spare-wheel target outside group: {group_code}")
        _ensure(len(repair_observations) == 4, f"repair-kit observation count mismatch: {group_code}")
        _ensure(len(spare_observations) == (4 if spare else 0), f"spare observation count mismatch: {group_code}")
        values = {str(item.get("value", "")) for item in [*repair_observations, *spare_observations]}
        _ensure(values == expected["values"], f"source values differ: {group_code}")
        for observation in [*repair_observations, *spare_observations]:
            _ensure(
                set(observation)
                == {"context_code", "value", "source_text", *CONTEXT_FIELDS_FROM_SPEC},
                f"unexpected observation fields: {group_code}",
            )
            _ensure(str(observation.get("source_text", "")).strip() != "", "empty source text")
            _ensure(observation.get("double_floor_state_code") == "", "page-20 double-floor state inferred")
        overlap = seen_configurations & set(configurations)
        _ensure(not overlap, f"configuration appears in more than one group: {sorted(overlap)}")
        seen_configurations.update(str(code) for code in configurations)

    _ensure(seen_groups == set(EXPECTED_GROUPS), "import group set differs")
    _ensure(len(seen_configurations) == 11, "expected eleven imported configurations")
    deferred = payload.get("deferred_groups")
    _ensure(isinstance(deferred, list) and len(deferred) == 2, "expected two deferred groups")
    four_by_four = next((item for item in deferred if item.get("group_code") == "hybrid_g_150_4x4"), None)
    _ensure(isinstance(four_by_four, dict), "hybrid-G 150 4x4 deferral missing")
    _ensure(set(four_by_four.get("configurations", [])) == DEFERRED_4X4_CONFIGURATIONS, "4x4 deferred scope changed")
    _ensure(set(four_by_four.get("source_values", [])) == DEFERRED_4X4_VALUES, "4x4 deferred values changed")
    _ensure("contradict" in str(four_by_four.get("reason", "")).casefold(), "4x4 contradiction reason missing")
    generic = next((item for item in deferred if item.get("group_code") == "generic_dimensions_double_floor"), None)
    _ensure(isinstance(generic, dict), "generic dimensions deferral missing")
    _ensure("powertrain" in str(generic.get("reason", "")).casefold(), "generic projection reason missing")
    return payload


def _source_row() -> dict[str, str]:
    sources = {row.get("code", ""): row for row in _read_rows(MASTER / "sources.csv")}
    row = sources.get(SOURCE_CODE)
    _ensure(row is not None, f"registered source missing: {SOURCE_CODE}")
    _ensure(row.get("status") == "active", "Bigster brochure source is not active")
    _ensure(row.get("publisher") == "Dacia", "unexpected publisher")
    _ensure(row.get("market") == "PL", "unexpected market")
    _ensure(row.get("document_date") == "2025-12-10", "unexpected source date")
    _ensure(row.get("file_path") == SOURCE_FILE, "source file path mismatch")
    _ensure(row.get("sha256") == SOURCE_SHA256, "source hash registry mismatch")
    path = ROOT / SOURCE_FILE
    _ensure(path.is_file(), f"registered brochure missing: {path}")
    _ensure(_file_sha256(path) == SOURCE_SHA256, "archived Bigster PDF hash mismatch")
    return row


def _configuration_codes(spec: Mapping[str, Any]) -> list[str]:
    result = [str(code) for group in spec["groups"] for code in group["configurations"]]
    _ensure(len(result) == 11 and len(result) == len(set(result)), "expected eleven configurations")
    return result


def _entries(spec: Mapping[str, Any]) -> list[tuple[str, Mapping[str, Any]]]:
    result: list[tuple[str, Mapping[str, Any]]] = []
    for group in spec["groups"]:
        for configuration_code in group["repair_kit_configurations"]:
            for observation in group["repair_kit_observations"]:
                result.append((str(configuration_code), observation))
        for configuration_code in group["spare_wheel_configurations"]:
            for observation in group["spare_wheel_observations"]:
                result.append((str(configuration_code), observation))
    _ensure(len(result) == 68, "expected 68 Bigster cargo observations")
    return result


def _verify_configurations(spec: Mapping[str, Any]) -> None:
    configurations = {
        row.get("code", ""): row
        for row in _read_rows(MASTER / "configurations.csv")
        if row.get("status") == "active"
    }
    expected_counts = Counter()
    for group in spec["groups"]:
        powertrain = str(group["powertrain_label"])
        for code in group["configurations"]:
            row = configurations.get(str(code))
            _ensure(row is not None, f"active configuration missing: {code}")
            _ensure(str(code).startswith("bigster_"), f"not a Bigster configuration: {code}")
            _ensure(row.get("powertrain_label") == powertrain, f"powertrain mismatch: {code}")
            _ensure("_4x2_" in str(code), f"drive mismatch: {code}")
            expected_transmission = "automatic" if group["group_code"] == "hybrid_155" else "manual"
            _ensure(row.get("transmission_type") == expected_transmission, f"transmission mismatch: {code}")
            expected_counts[str(code)] = 8 if code in group["spare_wheel_configurations"] else 4
    _ensure(expected_counts == Counter(code for code, _ in _entries(spec)), "configuration observation counts differ")
    _ensure(
        DEFERRED_4X4_CONFIGURATIONS <= set(configurations),
        "one or more deferred 4x4 configurations are not active",
    )


def _verify_attribute(spec: Mapping[str, Any]) -> None:
    matches = [row for row in _read_rows(MASTER / "attributes.csv") if row.get("code") == "boot_capacity"]
    _ensure(len(matches) == 1, "expected one boot_capacity attribute")
    contract = spec["attribute_contract"]
    _ensure({key: matches[0].get(key, "") for key in contract} == contract, "boot_capacity contract differs")


def _expected_value_rows(spec: Mapping[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    next_id = int(spec["value_id_start"])
    date_slug = str(spec["observation_date"]).replace("-", "")
    for configuration_code, observation in _entries(spec):
        context_code = str(observation["context_code"])
        code = f"{configuration_code}_boot_capacity_{context_code}_{date_slug}"
        rows.append(
            {
                "id": str(next_id),
                "code": code,
                "configuration_code": configuration_code,
                "attribute_code": "boot_capacity",
                "fuel_type_code": "",
                "value": str(observation["value"]),
                "observation_date": str(spec["observation_date"]),
                "source_code": SOURCE_CODE,
                "notes": (
                    f"Source page {spec['source_page']}, section {spec['source_section']}: "
                    f"{observation['source_text']}. Context is stored in "
                    "configuration_cargo_volume_contexts.csv."
                ),
            }
        )
        next_id += 1
    return rows


def _expected_context_rows(spec: Mapping[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    values = _expected_value_rows(spec)
    entries = _entries(spec)
    next_id = int(spec["context_id_start"])
    for value, (_configuration_code, observation) in zip(values, entries):
        rows.append(
            {
                "id": str(next_id),
                "code": f"cargo_context_{value['code']}",
                "configuration_attribute_value_code": value["code"],
                **{field: str(observation[field]) for field in CONTEXT_FIELDS_FROM_SPEC},
                "notes": (
                    f"Official Bigster brochure page {spec['source_page']}; exact context "
                    f"for {observation['source_text']}. Empty double-floor and third-row "
                    "fields mean not stated."
                ),
            }
        )
        next_id += 1
    return rows


def _expected_source_configuration_rows(spec: Mapping[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "source_code": SOURCE_CODE,
            "configuration_code": code,
            "relationship": RELATIONSHIP,
            "notes": (
                "The official Bigster brochure page-20 technical table identifies the "
                "powertrain-specific cargo column; page-21 equipment notes define the "
                "repair-kit and optional spare-wheel boundary used by this import."
            ),
        }
        for code in _configuration_codes(spec)
    ]


def _semantic(rows: Iterable[Mapping[str, str]], fields: Sequence[str]) -> list[tuple[str, ...]]:
    payload = [field for field in fields if field != "id"]
    return sorted(tuple(str(row.get(field, "")) for field in payload) for row in rows)


def _apply_owned_rows(
    path: Path,
    fields: Sequence[str],
    expected: list[dict[str, str]],
    owned_codes: set[str],
) -> None:
    _require_header(path, fields)
    existing = _read_rows(path)
    retained = [row for row in existing if row.get("code", "") not in owned_codes]
    expected_ids = {row["id"] for row in expected}
    _ensure(not any(row.get("id", "") in expected_ids for row in retained), f"reserved ID collision in {path}")
    _write_rows_atomic(path, fields, [*retained, *expected])


def _apply_source_configurations(spec: Mapping[str, Any]) -> None:
    _require_header(SOURCE_CONFIGURATION_PATH, SOURCE_CONFIGURATION_FIELDS)
    rows = _read_rows(SOURCE_CONFIGURATION_PATH)
    configurations = set(_configuration_codes(spec))
    retained = [
        row
        for row in rows
        if not (
            row.get("source_code") == SOURCE_CODE
            and row.get("configuration_code") in configurations
            and row.get("relationship") == RELATIONSHIP
        )
    ]
    expected = _expected_source_configuration_rows(spec)
    next_id = max((int(row["id"]) for row in retained), default=0) + 1
    generated = [{"id": str(next_id + index), **row} for index, row in enumerate(expected)]
    _write_rows_atomic(SOURCE_CONFIGURATION_PATH, SOURCE_CONFIGURATION_FIELDS, [*retained, *generated])


def _verify_materialized(spec: Mapping[str, Any]) -> None:
    expected_values = _expected_value_rows(spec)
    expected_contexts = _expected_context_rows(spec)
    expected_relations = _expected_source_configuration_rows(spec)
    value_codes = {row["code"] for row in expected_values}
    context_codes = {row["code"] for row in expected_contexts}
    configurations = set(_configuration_codes(spec))
    actual_values = [row for row in _read_rows(VALUE_PATH) if row.get("code", "") in value_codes]
    actual_contexts = [row for row in _read_rows(CONTEXT_PATH) if row.get("code", "") in context_codes]
    actual_relations = [
        row
        for row in _read_rows(SOURCE_CONFIGURATION_PATH)
        if row.get("source_code") == SOURCE_CODE
        and row.get("configuration_code") in configurations
        and row.get("relationship") == RELATIONSHIP
    ]
    _ensure(_semantic(actual_values, VALUE_FIELDS) == _semantic(expected_values, VALUE_FIELDS), "materialized Bigster cargo values differ")
    _ensure(_semantic(actual_contexts, CONTEXT_FIELDS) == _semantic(expected_contexts, CONTEXT_FIELDS), "materialized Bigster cargo contexts differ")
    _ensure(_semantic(actual_relations, SOURCE_CONFIGURATION_FIELDS) == _semantic(expected_relations, SOURCE_CONFIGURATION_FIELDS), "Bigster source relationships differ")
    _ensure(len(actual_values) == 68 and len(actual_contexts) == 68, "expected 68 values and contexts")


def _verify_non_inference(spec: Mapping[str, Any]) -> None:
    imported = _expected_value_rows(spec)
    imported_codes = {row["code"] for row in imported}
    rows = [row for row in _read_rows(VALUE_PATH) if row.get("code", "") in imported_codes]
    _ensure(not {row["value"] for row in rows} & DEFERRED_4X4_VALUES, "deferred 4x4 value imported")
    _ensure(not {row["configuration_code"] for row in rows} & DEFERRED_4X4_CONFIGURATIONS, "deferred 4x4 configuration imported")
    contexts = {
        row["configuration_attribute_value_code"]: row
        for row in _read_rows(CONTEXT_PATH)
        if row.get("configuration_attribute_value_code", "") in imported_codes
    }
    _ensure(set(contexts) == imported_codes, "Bigster cargo value lacks context")
    for value in rows:
        context = contexts[value["code"]]
        _ensure(context.get("double_floor_state_code", "") == "", "double-floor state inferred")
        _ensure(context.get("third_row_state_code", "") == "", "third-row state inferred")
        equipment = (
            context.get("spare_wheel_state_code", ""),
            context.get("tyre_repair_kit_state_code", ""),
        )
        _ensure(equipment in {("absent", "present"), ("present", "absent")}, "invalid equipment context")
        if "_essential_mildhybrid140_" in value["configuration_code"] or "_mildhybridg140_" in value["configuration_code"]:
            _ensure(equipment == ("absent", "present"), "spare wheel projected into unsupported configuration")


def check() -> None:
    spec = _load_spec()
    _source_row()
    _verify_attribute(spec)
    _verify_configurations(spec)
    _verify_materialized(spec)
    _verify_non_inference(spec)


def apply() -> None:
    spec = _load_spec()
    _source_row()
    _verify_attribute(spec)
    _verify_configurations(spec)
    expected_values = _expected_value_rows(spec)
    expected_contexts = _expected_context_rows(spec)
    _apply_owned_rows(VALUE_PATH, VALUE_FIELDS, expected_values, {row["code"] for row in expected_values})
    _apply_owned_rows(CONTEXT_PATH, CONTEXT_FIELDS, expected_contexts, {row["code"] for row in expected_contexts})
    _apply_source_configurations(spec)
    check()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        apply() if args.apply else check()
    except (ContractError, OSError, csv.Error, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        return 1
    print("PASS: Bigster official brochure cargo import contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
