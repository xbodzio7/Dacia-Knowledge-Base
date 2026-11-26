#!/usr/bin/env python3
"""Import exact historical Jogger brochure hybrid-performance evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPEC = ROOT / "data" / "imports" / "brochure_technical_values" / "jogger-hybrid-performance-completion-20251217.json"
VALUES = MASTER / "configuration_attribute_values.csv"
RANGES = MASTER / "configuration_attribute_value_ranges.csv"
SOURCE_CODE = "src_pl_jogger_brochure_20251217"
SOURCE_FILE = "PDF/Broszury/DACIA JOGGER broszura 20251217.pdf"
SOURCE_SHA256 = "eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6"
VALUE_FIELDS = (
    "id", "code", "configuration_code", "attribute_code",
    "fuel_type_code", "gear_number", "value", "observation_date",
    "source_code", "notes",
)
RANGE_FIELDS = (
    "id", "code", "configuration_code", "attribute_code",
    "fuel_type_code", "minimum_value", "maximum_value",
    "lower_inclusive", "upper_inclusive", "observation_date",
    "source_code", "notes",
)
ATTRIBUTE_CONTRACTS = {
    "acceleration_0_100": ("decimal", "s", "active"),
    "hybrid_battery_capacity_source_stated": ("decimal", "kWh", "active"),
    "max_power_rpm": ("integer", "rpm", "active"),
    "max_torque_rpm": ("integer", "rpm", "active"),
}
EXPECTED_SCALAR_COUNTS = Counter({
    "acceleration_0_100": 6,
    "hybrid_battery_capacity_source_stated": 6,
    "max_power_rpm": 6,
})
EXPECTED_RANGE_COUNTS = Counter({"max_power_rpm": 26, "max_torque_rpm": 32})
EXPECTED_RANGE_FUELS = Counter({"petrol": 32, "lpg": 20, "": 6})


class ImportContractError(RuntimeError):
    """Raised when reviewed source evidence or repository state drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ImportContractError(message)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        ensure(reader.fieldnames is not None, f"missing CSV header: {path}")
        return list(reader)


def require_header(path: Path, fields: Sequence[str]) -> None:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        header = next(csv.reader(handle), None)
    ensure(header == list(fields), f"unexpected header in {path}: {header!r}")


def write_rows_atomic(
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


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decimal_value(value: str, label: str) -> Decimal:
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ImportContractError(f"{label} is not decimal: {value!r}") from exc
    ensure(parsed.is_finite(), f"{label} is not finite")
    return parsed


def load_spec() -> dict[str, Any]:
    payload = json.loads(SPEC.read_text(encoding="utf-8"))
    ensure(payload.get("version") == 1, "unsupported package version")
    ensure(payload.get("kind") == "jogger_brochure_hybrid_performance_completion", "unexpected package kind")
    ensure(payload.get("reviewed_on") == "2026-07-26", "unexpected review date")
    ensure(payload.get("source_code") == SOURCE_CODE, "unexpected source code")
    ensure(payload.get("observation_date") == "2025-12-17", "unexpected observation date")
    ensure(payload.get("source_page") == 19, "unexpected source page")
    ensure(payload.get("scalar_id_start") == 2273, "unexpected scalar ID start")
    ensure(payload.get("range_id_start") == 177, "unexpected range ID start")

    scalar_groups = payload.get("scalar_groups")
    range_groups = payload.get("range_groups")
    ensure(isinstance(scalar_groups, list) and len(scalar_groups) == 4, "expected four scalar groups")
    ensure(isinstance(range_groups, list) and len(range_groups) == 7, "expected seven range groups")

    scalar_configurations = []
    for group in scalar_groups:
        ensure(isinstance(group, dict), "scalar group must be an object")
        ensure(set(group) == {"attribute_code", "fuel_type_code", "value", "source_text", "configurations"}, "unexpected scalar group fields")
        attribute = str(group["attribute_code"])
        ensure(attribute in EXPECTED_SCALAR_COUNTS, f"unexpected scalar attribute: {attribute}")
        ensure(str(group["fuel_type_code"]) == "", f"scalar fuel context must be neutral: {attribute}")
        ensure(str(group["source_text"]).strip(), f"scalar source text missing: {attribute}")
        configurations = group["configurations"]
        ensure(isinstance(configurations, list) and configurations, f"scalar configurations missing: {attribute}")
        scalar_configurations.extend(str(code) for code in configurations)
        parsed = decimal_value(str(group["value"]), attribute)
        if ATTRIBUTE_CONTRACTS[attribute][0] == "integer":
            ensure(parsed == parsed.to_integral(), f"integer scalar is not integral: {attribute}")

    range_configurations = []
    for group in range_groups:
        ensure(isinstance(group, dict), "range group must be an object")
        ensure(set(group) == {
            "attribute_code", "fuel_type_code", "minimum_value",
            "maximum_value", "source_text", "configurations",
        }, "unexpected range group fields")
        attribute = str(group["attribute_code"])
        ensure(attribute in EXPECTED_RANGE_COUNTS, f"unexpected range attribute: {attribute}")
        fuel = str(group["fuel_type_code"])
        ensure(fuel in {"", "lpg", "petrol"}, f"unexpected range fuel: {fuel}")
        minimum = decimal_value(str(group["minimum_value"]), f"{attribute}.minimum")
        maximum = decimal_value(str(group["maximum_value"]), f"{attribute}.maximum")
        ensure(minimum <= maximum, f"reversed range: {attribute}")
        ensure(minimum == minimum.to_integral() and maximum == maximum.to_integral(), f"rpm range is not integral: {attribute}")
        configurations = group["configurations"]
        ensure(isinstance(configurations, list) and configurations, f"range configurations missing: {attribute}")
        range_configurations.extend(str(code) for code in configurations)
        ensure(str(group["source_text"]).strip(), f"range source text missing: {attribute}")

    ensure(len(scalar_configurations) == 18, "expected 18 scalar assignments")
    ensure(len(range_configurations) == 58, "expected 58 range assignments")
    ensure(len(set(scalar_configurations + range_configurations)) == 22, "expected all 22 Jogger configurations")

    historical = payload.get("historical_precedence")
    excluded = payload.get("excluded_evidence")
    ensure(isinstance(historical, list) and len(historical) == 3, "expected three precedence rules")
    ensure(isinstance(excluded, list) and len(excluded) == 4, "expected four exclusion rules")
    ensure(
        {str(item.get("code", "")) for item in historical if isinstance(item, dict)}
        == {
            "newer_my26_values_remain_current",
            "ecog_petrol_power_range_differs_from_newer_source",
            "hybrid_acceleration_exact_by_seat_layout",
        },
        "historical precedence set differs",
    )
    ensure(
        {str(item.get("code", "")) for item in excluded if isinstance(item, dict)}
        == {
            "electric_motor_torque_has_no_engine_speed",
            "battery_capacity_semantics_remain_source_stated",
            "no_cross_seat_projection_for_acceleration",
            "no_range_flattening",
        },
        "exclusion boundary set differs",
    )
    return payload


def verify_source() -> None:
    sources = {row.get("code", ""): row for row in read_rows(MASTER / "sources.csv")}
    source = sources.get(SOURCE_CODE)
    ensure(source is not None and source.get("status") == "active", "active Jogger brochure source missing")
    ensure(source.get("source_type") == "brochure_pdf", "source type differs")
    ensure(source.get("document_date") == "2025-12-17", "source date differs")
    ensure(source.get("file_path") == SOURCE_FILE, "source path differs")
    ensure(source.get("sha256") == SOURCE_SHA256, "source registry hash differs")
    archived = ROOT / SOURCE_FILE
    ensure(archived.is_file() and file_sha256(archived) == SOURCE_SHA256, "archived source hash differs")


def all_group_configurations(spec: Mapping[str, Any]) -> set[str]:
    return {
        str(code)
        for section in ("scalar_groups", "range_groups")
        for group in spec[section]
        for code in group["configurations"]
    }


def verify_references(spec: Mapping[str, Any]) -> None:
    attributes = {row.get("code", ""): row for row in read_rows(MASTER / "attributes.csv")}
    for code, contract in ATTRIBUTE_CONTRACTS.items():
        row = attributes.get(code)
        ensure(row is not None, f"attribute missing: {code}")
        ensure((row.get("data_type"), row.get("unit"), row.get("status")) == contract, f"attribute contract differs: {code}")

    configurations = {row.get("code", ""): row for row in read_rows(MASTER / "configurations.csv")}
    values = read_rows(VALUES)
    seats = {
        row["configuration_code"]: row["value"]
        for row in values
        if row.get("attribute_code") == "number_of_seats"
    }
    target = all_group_configurations(spec)
    ensure(len(target) == 22, "target configuration set differs")
    for code in target:
        row = configurations.get(code)
        ensure(row is not None and row.get("status") == "active", f"active configuration missing: {code}")
        ensure(seats.get(code) in {"5", "7"}, f"seat layout missing: {code}")

    for group in spec["scalar_groups"]:
        attribute = group["attribute_code"]
        for code in group["configurations"]:
            row = configurations[code]
            ensure(row.get("powertrain_label") == "hybrid 155", f"scalar group targets non-hybrid configuration: {code}")
            ensure(row.get("transmission_type") == "automatic", f"hybrid transmission differs: {code}")
            if attribute == "acceleration_0_100":
                expected_seats = "5" if str(group["value"]) == "8.9" else "7"
                ensure(seats.get(code) == expected_seats, f"acceleration seat layout differs: {code}")

    relationships = {
        (row.get("source_code", ""), row.get("configuration_code", ""), row.get("relationship", ""))
        for row in read_rows(MASTER / "source_configurations.csv")
    }
    for code in target:
        ensure((SOURCE_CODE, code, "brochure_technical_data_for") in relationships, f"source relationship missing: {code}")


def row_code(configuration: str, attribute: str, fuel: str, kind: str) -> str:
    parts = [configuration, attribute]
    if fuel:
        parts.append(fuel)
    if kind == "range":
        parts.append("range")
    parts.append("20251217")
    return "_".join(parts)


def expected_scalars(spec: Mapping[str, Any]) -> list[dict[str, str]]:
    result = []
    start = int(spec["scalar_id_start"])
    for group in spec["scalar_groups"]:
        for configuration in group["configurations"]:
            result.append({
                "id": str(start + len(result)),
                "code": row_code(str(configuration), str(group["attribute_code"]), str(group["fuel_type_code"]), "scalar"),
                "configuration_code": str(configuration),
                "attribute_code": str(group["attribute_code"]),
                "fuel_type_code": str(group["fuel_type_code"]),
                "gear_number": "",
                "value": str(group["value"]),
                "observation_date": str(spec["observation_date"]),
                "source_code": SOURCE_CODE,
                "notes": f"Official brochure page {spec['source_page']}: {group['source_text']}",
            })
    ensure(len(result) == 18, "expected 18 scalar rows")
    ensure([int(row["id"]) for row in result] == list(range(2273, 2291)), "scalar IDs differ")
    ensure(Counter(row["attribute_code"] for row in result) == EXPECTED_SCALAR_COUNTS, "scalar attribute counts differ")
    ensure({row["fuel_type_code"] for row in result} == {""}, "scalar fuel context differs")
    ensure(len({row["code"] for row in result}) == 18, "scalar codes are not unique")
    return result


def expected_ranges(spec: Mapping[str, Any]) -> list[dict[str, str]]:
    result = []
    start = int(spec["range_id_start"])
    for group in spec["range_groups"]:
        for configuration in group["configurations"]:
            result.append({
                "id": str(start + len(result)),
                "code": row_code(str(configuration), str(group["attribute_code"]), str(group["fuel_type_code"]), "range"),
                "configuration_code": str(configuration),
                "attribute_code": str(group["attribute_code"]),
                "fuel_type_code": str(group["fuel_type_code"]),
                "minimum_value": str(group["minimum_value"]),
                "maximum_value": str(group["maximum_value"]),
                "lower_inclusive": "true",
                "upper_inclusive": "true",
                "observation_date": str(spec["observation_date"]),
                "source_code": SOURCE_CODE,
                "notes": f"Official brochure page {spec['source_page']}: {group['source_text']}",
            })
    ensure(len(result) == 58, "expected 58 range rows")
    ensure([int(row["id"]) for row in result] == list(range(177, 235)), "range IDs differ")
    ensure(Counter(row["attribute_code"] for row in result) == EXPECTED_RANGE_COUNTS, "range attribute counts differ")
    ensure(Counter(row["fuel_type_code"] for row in result) == EXPECTED_RANGE_FUELS, "range fuel counts differ")
    ensure(len({row["code"] for row in result}) == 58, "range codes are not unique")
    return result


def merge_rows(
    existing: list[dict[str, str]],
    expected: list[dict[str, str]],
    semantic_fields: Sequence[str],
) -> list[dict[str, str]]:
    by_id = {row.get("id", ""): row for row in existing}
    by_code = {row.get("code", "").casefold(): row for row in existing}
    by_semantic = {
        tuple(row.get(field, "") for field in semantic_fields): row
        for row in existing
    }
    additions = []
    for row in expected:
        candidates = [
            by_id.get(row["id"]),
            by_code.get(row["code"].casefold()),
            by_semantic.get(tuple(row.get(field, "") for field in semantic_fields)),
        ]
        present = [item for item in candidates if item is not None]
        if present:
            ensure(all(item == row for item in present), f"existing row differs: {row['code']}")
        else:
            additions.append(row)
    if additions:
        current_max = max((int(row["id"]) for row in existing), default=0)
        ensure(int(additions[0]["id"]) == current_max + 1, "append-only ID boundary differs")
        ensure([int(row["id"]) for row in additions] == list(range(current_max + 1, current_max + 1 + len(additions))), "added IDs are not contiguous")
    return [*existing, *additions]


def apply(spec: Mapping[str, Any]) -> None:
    require_header(VALUES, VALUE_FIELDS)
    require_header(RANGES, RANGE_FIELDS)
    scalar_rows = read_rows(VALUES)
    range_rows = read_rows(RANGES)
    merged_scalars = merge_rows(
        scalar_rows,
        expected_scalars(spec),
        ("configuration_code", "attribute_code", "fuel_type_code", "gear_number", "observation_date"),
    )
    merged_ranges = merge_rows(
        range_rows,
        expected_ranges(spec),
        ("configuration_code", "attribute_code", "fuel_type_code", "observation_date"),
    )
    if merged_scalars != scalar_rows:
        write_rows_atomic(VALUES, VALUE_FIELDS, merged_scalars)
    if merged_ranges != range_rows:
        write_rows_atomic(RANGES, RANGE_FIELDS, merged_ranges)


def verify_newer_precedence() -> None:
    values = read_rows(VALUES)
    ranges = read_rows(RANGES)
    hybrid_acceleration = [
        row for row in ranges
        if row.get("attribute_code") == "acceleration_0_100"
        and row.get("configuration_code", "").startswith("jogger_")
        and "hybrid155" in row.get("configuration_code", "")
        and row.get("observation_date") == "2026-04-01"
    ]
    ensure(len(hybrid_acceleration) == 6, "newer hybrid acceleration ranges changed")
    ensure({(row["minimum_value"], row["maximum_value"]) for row in hybrid_acceleration} == {("8.9", "9")}, "newer hybrid acceleration range values changed")

    newer_petrol_power = [
        row for row in ranges
        if row.get("attribute_code") == "max_power_rpm"
        and row.get("configuration_code", "").startswith("jogger_")
        and "ecog120" in row.get("configuration_code", "")
        and row.get("fuel_type_code") == "petrol"
        and row.get("observation_date") == "2026-04-01"
    ]
    ensure(len(newer_petrol_power) == 10, "newer Eco-G petrol power ranges changed")
    ensure({(row["minimum_value"], row["maximum_value"]) for row in newer_petrol_power} == {("4500", "5750")}, "newer Eco-G petrol power range values changed")

    hybrid_torque = [
        row for row in values
        if row.get("attribute_code") == "max_torque_rpm"
        and "hybrid155" in row.get("configuration_code", "")
        and row.get("observation_date") == "2026-04-01"
    ]
    ensure(len(hybrid_torque) == 6 and {row["value"] for row in hybrid_torque} == {"3000"}, "newer hybrid torque points changed")


def check(spec: Mapping[str, Any]) -> None:
    expected_value_rows = expected_scalars(spec)
    expected_range_rows = expected_ranges(spec)
    all_values = read_rows(VALUES)
    all_ranges = read_rows(RANGES)
    actual_values = {row["code"]: row for row in all_values if row.get("code") in {item["code"] for item in expected_value_rows}}
    actual_ranges = {row["code"]: row for row in all_ranges if row.get("code") in {item["code"] for item in expected_range_rows}}
    ensure(actual_values == {row["code"]: row for row in expected_value_rows}, "master scalar package differs")
    ensure(actual_ranges == {row["code"]: row for row in expected_range_rows}, "master range package differs")
    verify_newer_precedence()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        verify_source()
        spec = load_spec()
        verify_references(spec)
        if args.apply:
            apply(spec)
        check(spec)
    except (ImportContractError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print("PASS: Jogger brochure hybrid performance completion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
