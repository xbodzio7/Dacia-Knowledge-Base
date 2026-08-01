#!/usr/bin/env python3
"""Import exact Spring brochure technical observations dated 2026-02-19."""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sys
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPEC = ROOT / "data" / "imports" / "spring_technical_20260219.csv"
VALUE_OUTPUT = MASTER / "configuration_attribute_values.csv"
RANGE_OUTPUT = MASTER / "configuration_attribute_value_ranges.csv"
CONTEXT_OUTPUT = MASTER / "configuration_cargo_volume_contexts.csv"
SOURCE = ROOT / "PDF" / "Broszury" / "DACIA SPRING broszura 20260219.pdf"
SOURCE_CODE = "src_pl_spring_brochure_20260219"
SOURCE_SHA256 = "73a4c568ce273bc095f6ecf1cfa4f5f2a92324bb2f0bbc171ba45bb4a4cf3c8d"
OBSERVATION_DATE = "2026-02-19"
CONFIGURATIONS = (
    "spring_essential_electric70_automatic",
    "spring_expression_electric70_automatic",
    "spring_extreme_electric100_automatic",
)
SPEC_FIELDS = (
    "record_type", "configuration_code", "attribute_code", "value",
    "minimum_value", "maximum_value", "source_page", "source_label",
    "normalization_notes",
)
VALUE_FIELDS = (
    "id", "code", "configuration_code", "attribute_code", "fuel_type_code",
    "gear_number", "value", "observation_date", "source_code", "notes",
)
RANGE_FIELDS = (
    "id", "code", "configuration_code", "attribute_code", "fuel_type_code",
    "minimum_value", "maximum_value", "lower_inclusive", "upper_inclusive",
    "observation_date", "source_code", "notes",
)
EXPECTED_VALUE_FIRST_ID = 3499
EXPECTED_VALUE_LAST_ID = 3552
EXPECTED_RANGE_FIRST_ID = 299
EXPECTED_RANGE_LAST_ID = 301
EXPECTED_CONTEXT_FIRST_ID = 318
EXPECTED_CONTEXT_LAST_ID = 320
CONTEXT_FIELDS = (
    "id", "code", "configuration_attribute_value_code", "measurement_basis_code",
    "second_row_state_code", "third_row_state_code", "compartment_code",
    "spare_wheel_state_code", "tyre_repair_kit_state_code",
    "double_floor_state_code", "notes",
)
EXCLUDED_ATTRIBUTES = {
    "engine_torque", "max_torque_rpm", "battery_capacity_gross",
    "battery_capacity_net", "energy_consumption_combined", "city_range",
    "dc_charging_time", "dc_charging_supported", "overall_length",
    "overall_width", "overall_height",
}


class ContractError(RuntimeError):
    """Raised when the exact Spring import contract cannot be reproduced."""


def read_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ContractError(f"missing CSV header: {path}")
            return [dict(row) for row in reader]
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise ContractError(f"cannot read {path}: {exc}") from exc


def require_header(path: Path, fields: Sequence[str]) -> None:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            header = next(csv.reader(handle), None)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise ContractError(f"cannot inspect {path}: {exc}") from exc
    if header != list(fields):
        raise ContractError(f"unexpected header in {path}: {header!r}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise ContractError(f"cannot read source {path}: {exc}") from exc
    return digest.hexdigest()


def verify_repository_contract() -> None:
    if sha256(SOURCE) != SOURCE_SHA256:
        raise ContractError(f"Spring brochure SHA-256 mismatch: {SOURCE}")
    configurations = {row["code"]: row for row in read_rows(MASTER / "configurations.csv")}
    for code in CONFIGURATIONS:
        row = configurations.get(code)
        if row is None or row.get("status") != "active":
            raise ContractError(f"missing active Spring configuration: {code}")
    links = {
        (row["source_code"], row["configuration_code"])
        for row in read_rows(MASTER / "source_configurations.csv")
    }
    for code in CONFIGURATIONS:
        if (SOURCE_CODE, code) not in links:
            raise ContractError(f"Spring brochure does not document configuration: {code}")
    attributes = {row["code"]: row for row in read_rows(MASTER / "attributes.csv")}
    for row in load_spec(validate_repository=False):
        attribute = attributes.get(row["attribute_code"])
        if attribute is None or attribute.get("status") != "active":
            raise ContractError(f"missing active attribute: {row['attribute_code']}")


def load_spec(*, validate_repository: bool = True) -> list[dict[str, str]]:
    require_header(SPEC, SPEC_FIELDS)
    rows = read_rows(SPEC)
    if len(rows) != 57:
        raise ContractError(f"expected 57 specification rows, found {len(rows)}")
    values = [row for row in rows if row["record_type"] == "value"]
    ranges = [row for row in rows if row["record_type"] == "range"]
    if len(values) != 54 or len(ranges) != 3:
        raise ContractError(f"expected 54 values and 3 ranges, found {len(values)} and {len(ranges)}")
    counts = {code: 0 for code in CONFIGURATIONS}
    range_counts = {code: 0 for code in CONFIGURATIONS}
    identities: set[tuple[str, str, str]] = set()
    for row in rows:
        if row["configuration_code"] not in counts:
            raise ContractError(f"out-of-scope configuration: {row['configuration_code']}")
        identity = (row["record_type"], row["configuration_code"], row["attribute_code"])
        if identity in identities:
            raise ContractError(f"duplicate specification identity: {identity}")
        identities.add(identity)
        if not row["source_page"].isdigit() or not row["source_label"].strip():
            raise ContractError(f"missing exact page or label: {identity}")
        if row["attribute_code"] in EXCLUDED_ATTRIBUTES:
            raise ContractError(f"excluded ambiguous attribute entered the specification: {identity}")
        if row["record_type"] == "value":
            counts[row["configuration_code"]] += 1
            if not row["value"] or row["minimum_value"] or row["maximum_value"]:
                raise ContractError(f"invalid scalar row: {identity}")
        elif row["record_type"] == "range":
            range_counts[row["configuration_code"]] += 1
            if row["attribute_code"] != "max_power_rpm":
                raise ContractError(f"unexpected range attribute: {identity}")
            if row["value"] or not row["minimum_value"] or not row["maximum_value"]:
                raise ContractError(f"invalid range row: {identity}")
            if float(row["minimum_value"]) > float(row["maximum_value"]):
                raise ContractError(f"reversed range: {identity}")
        else:
            raise ContractError(f"unknown record type: {row['record_type']}")
    if set(counts.values()) != {18} or set(range_counts.values()) != {1}:
        raise ContractError(f"per-configuration contract differs: {counts}, {range_counts}")
    if validate_repository:
        verify_repository_contract()
    return rows


def note(row: dict[str, str]) -> str:
    suffix = row["normalization_notes"].strip()
    text = f"Source page {row['source_page']}: {row['source_label']}."
    if row["attribute_code"] == "boot_capacity":
        text += " Context is stored in configuration_cargo_volume_contexts.csv."
    return f"{text} {suffix}" if suffix else text


def generated_value_rows(spec_rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "code": f"{row['configuration_code']}_{row['attribute_code']}_20260219",
            "configuration_code": row["configuration_code"],
            "attribute_code": row["attribute_code"],
            "fuel_type_code": "",
            "gear_number": "",
            "value": row["value"],
            "observation_date": OBSERVATION_DATE,
            "source_code": SOURCE_CODE,
            "notes": note(row),
        }
        for row in spec_rows if row["record_type"] == "value"
    ]


def generated_range_rows(spec_rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "code": f"{row['configuration_code']}_{row['attribute_code']}_range_20260219",
            "configuration_code": row["configuration_code"],
            "attribute_code": row["attribute_code"],
            "fuel_type_code": "",
            "minimum_value": row["minimum_value"],
            "maximum_value": row["maximum_value"],
            "lower_inclusive": "true",
            "upper_inclusive": "true",
            "observation_date": OBSERVATION_DATE,
            "source_code": SOURCE_CODE,
            "notes": note(row),
        }
        for row in spec_rows if row["record_type"] == "range"
    ]


def generated_context_rows(value_rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "code": f"cargo_context_{row['code']}",
            "configuration_attribute_value_code": row["code"],
            "measurement_basis_code": "vda_iso_3832",
            "second_row_state_code": "upright",
            "third_row_state_code": "",
            "compartment_code": "main_luggage_compartment",
            "spare_wheel_state_code": "",
            "tyre_repair_kit_state_code": "",
            "double_floor_state_code": "",
            "notes": "Official Spring brochure page 21; exact ISO 3832 minimum luggage context. Empty optional fields mean not stated.",
        }
        for row in value_rows if row["attribute_code"] == "boot_capacity"
    ]


def selected(rows: Iterable[dict[str, str]], *, ranges: bool) -> list[dict[str, str]]:
    codes = set(CONFIGURATIONS)
    allowed = {"max_power_rpm"} if ranges else None
    return [
        row for row in rows
        if row.get("source_code") == SOURCE_CODE
        and row.get("observation_date") == OBSERVATION_DATE
        and row.get("configuration_code") in codes
        and (allowed is None or row.get("attribute_code") in allowed)
    ]


def semantic(rows: Iterable[dict[str, str]], fields: Sequence[str]) -> list[tuple[str, ...]]:
    return sorted(tuple(row.get(field, "") for field in fields) for row in rows)


def verify_materialized() -> None:
    require_header(VALUE_OUTPUT, VALUE_FIELDS)
    require_header(RANGE_OUTPUT, RANGE_FIELDS)
    spec = load_spec()
    require_header(CONTEXT_OUTPUT, CONTEXT_FIELDS)
    values = selected(read_rows(VALUE_OUTPUT), ranges=False)
    ranges = selected(read_rows(RANGE_OUTPUT), ranges=True)
    expected_values = generated_value_rows(spec)
    expected_ranges = generated_range_rows(spec)
    expected_contexts = generated_context_rows(expected_values)
    context_codes = {row["code"] for row in expected_contexts}
    contexts = [row for row in read_rows(CONTEXT_OUTPUT) if row.get("code") in context_codes]
    if semantic(values, VALUE_FIELDS[1:]) != semantic(expected_values, VALUE_FIELDS[1:]):
        raise ContractError("stored Spring scalar rows differ from generated contract")
    if semantic(ranges, RANGE_FIELDS[1:]) != semantic(expected_ranges, RANGE_FIELDS[1:]):
        raise ContractError("stored Spring range rows differ from generated contract")
    if semantic(contexts, CONTEXT_FIELDS[1:]) != semantic(expected_contexts, CONTEXT_FIELDS[1:]):
        raise ContractError("stored Spring cargo contexts differ from generated contract")
    value_ids = sorted(int(row["id"]) for row in values)
    range_ids = sorted(int(row["id"]) for row in ranges)
    if value_ids != list(range(EXPECTED_VALUE_FIRST_ID, EXPECTED_VALUE_LAST_ID + 1)):
        raise ContractError("Spring scalar IDs are not the exact contiguous suffix 3499-3552")
    if range_ids != list(range(EXPECTED_RANGE_FIRST_ID, EXPECTED_RANGE_LAST_ID + 1)):
        raise ContractError("Spring range IDs are not the exact contiguous suffix 299-301")
    context_ids = sorted(int(row["id"]) for row in contexts)
    if context_ids != list(range(EXPECTED_CONTEXT_FIRST_ID, EXPECTED_CONTEXT_LAST_ID + 1)):
        raise ContractError("Spring cargo-context IDs are not the exact contiguous suffix 318-320")
    print("Spring brochure technical observations: PASS (54 values + 3 ranges + 3 cargo contexts)")


def write_csv(path: Path, rows: list[dict[str, str]], fields: Sequence[str]) -> None:
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def append_exact(
    path: Path,
    fields: Sequence[str],
    generated: list[dict[str, str]],
    expected_first_id: int,
    *,
    ranges: bool,
) -> None:
    require_header(path, fields)
    current = read_rows(path)
    actual = selected(current, ranges=ranges)
    if actual:
        if semantic(actual, fields[1:]) != semantic(generated, fields[1:]):
            raise ContractError(f"partial or conflicting Spring observations already exist in {path}")
        return
    try:
        maximum_id = max(int(row["id"]) for row in current)
    except (KeyError, ValueError) as exc:
        raise ContractError(f"non-integer IDs in {path}") from exc
    if maximum_id != expected_first_id - 1:
        raise ContractError(f"expected suffix after {expected_first_id - 1} in {path}, found {maximum_id}")
    output = current + [
        {"id": str(maximum_id + offset), **row}
        for offset, row in enumerate(generated, start=1)
    ]
    write_csv(path, output, fields)


def apply() -> None:
    spec = load_spec()
    append_exact(
        VALUE_OUTPUT, VALUE_FIELDS, generated_value_rows(spec), EXPECTED_VALUE_FIRST_ID,
        ranges=False,
    )
    value_rows = generated_value_rows(spec)
    append_exact(
        RANGE_OUTPUT, RANGE_FIELDS, generated_range_rows(spec), EXPECTED_RANGE_FIRST_ID,
        ranges=True,
    )
    contexts = generated_context_rows(value_rows)
    require_header(CONTEXT_OUTPUT, CONTEXT_FIELDS)
    current_contexts = read_rows(CONTEXT_OUTPUT)
    existing = [row for row in current_contexts if row.get("code") in {item["code"] for item in contexts}]
    if existing:
        if semantic(existing, CONTEXT_FIELDS[1:]) != semantic(contexts, CONTEXT_FIELDS[1:]):
            raise ContractError("partial or conflicting Spring cargo contexts already exist")
    else:
        maximum_id = max(int(row["id"]) for row in current_contexts)
        if maximum_id != EXPECTED_CONTEXT_FIRST_ID - 1:
            raise ContractError(f"expected cargo-context suffix after {EXPECTED_CONTEXT_FIRST_ID - 1}, found {maximum_id}")
        write_csv(
            CONTEXT_OUTPUT,
            current_contexts + [{"id": str(maximum_id + offset), **row} for offset, row in enumerate(contexts, start=1)],
            CONTEXT_FIELDS,
        )
    verify_materialized()


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.apply:
            apply()
        else:
            verify_materialized()
        return 0
    except ContractError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
