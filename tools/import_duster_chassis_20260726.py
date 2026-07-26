#!/usr/bin/env python3
"""Import exact Duster brochure chassis scalar and payload-range observations."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPEC_PATH = ROOT / "data" / "imports" / "brochure_technical_values" / "duster-chassis-20251020.json"
VALUE_PATH = MASTER / "configuration_attribute_values.csv"
RANGE_PATH = MASTER / "configuration_attribute_value_ranges.csv"
SOURCE_CODE = "src_pl_duster_mini_brochure_20251020"
SOURCE_PATH = ROOT / "PDF" / "Broszury" / "DACIA DUSTER mini broszura 20251020.pdf"
SOURCE_SHA = "84040b64bd67391cce4a99ada3021b0ad1a493f9430a666783e4632dd6ce85e8"
VALUE_FIELDS = (
    "id", "code", "configuration_code", "attribute_code", "fuel_type_code",
    "gear_number", "value", "observation_date", "source_code", "notes",
)
RANGE_FIELDS = (
    "id", "code", "configuration_code", "attribute_code", "fuel_type_code",
    "minimum_value", "maximum_value", "lower_inclusive", "upper_inclusive",
    "observation_date", "source_code", "notes",
)
SCALAR_CONTRACTS = {
    "turning_circle_wheel_track": ("decimal", "m", "active"),
    "maximum_kerb_weight": ("integer", "kg", "active"),
    "steering_type": ("string", "", "active"),
    "front_brake_type": ("string", "", "active"),
    "rear_brake_type": ("string", "", "active"),
    "standard_tyre_specification": ("string", "", "active"),
}
RANGE_CONTRACT = ("payload", "integer", "kg", "active")
EXPECTED_GROUPS = {
    "ecog120_4x2_manual": (4, "Eco-G 120 4x2", "manual", 20),
    "mildhybrid140_4x2_manual": (3, "mild hybrid 140 4x2", "manual", 20),
    "hybrid155_4x2_automatic": (3, "hybrid 155 4x2", "automatic", 21),
}
EXPECTED_CONFIGURATIONS = {
    "duster_iii_essential_ecog120_4x2_manual",
    "duster_iii_expression_ecog120_4x2_manual",
    "duster_iii_extreme_ecog120_4x2_manual",
    "duster_iii_journey_ecog120_4x2_manual",
    "duster_iii_expression_mildhybrid140_4x2_manual",
    "duster_iii_extreme_mildhybrid140_4x2_manual",
    "duster_iii_journey_mildhybrid140_4x2_manual",
    "duster_iii_expression_hybrid155_4x2_automatic",
    "duster_iii_extreme_hybrid155_4x2_automatic",
    "duster_iii_journey_hybrid155_4x2_automatic",
}
EXPECTED_EXCLUSIONS = {
    "hybridg150_without_exact_configuration",
    "automatic_ecog120_not_projected",
    "source_order_not_semantically_reassigned",
    "legacy_contexts_unchanged",
    "unrepresented_historical_powertrains",
    "cargo_rows_out_of_scope",
}


class ImportContractError(RuntimeError):
    """Raised when the reviewed Duster chassis import contract drifts."""


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


def write_rows_atomic(path: Path, fields: Sequence[str], rows: Iterable[Mapping[str, str]]) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
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


def validate_scalar(data_type: str, value: str, label: str) -> None:
    ensure(value != "", f"empty value: {label}")
    if data_type == "integer":
        ensure(re.fullmatch(r"(?:0|[1-9][0-9]*)", value) is not None, f"noncanonical integer: {label}")
    elif data_type == "decimal":
        try:
            parsed = Decimal(value)
        except InvalidOperation as exc:
            raise ImportContractError(f"invalid decimal: {label}") from exc
        ensure(parsed.is_finite(), f"nonfinite decimal: {label}")
    elif data_type == "string":
        ensure(value.strip() == value and value != "", f"invalid string: {label}")
    else:
        raise ImportContractError(f"unsupported data type: {data_type}")


def validate_integer_endpoint(value: str, label: str) -> int:
    ensure(re.fullmatch(r"(?:0|[1-9][0-9]*)", value) is not None, f"noncanonical integer endpoint: {label}")
    return int(value)


def load_spec() -> dict[str, Any]:
    payload = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    ensure(payload.get("version") == 1, "unsupported spec version")
    ensure(payload.get("kind") == "duster_chassis_observations", "unexpected spec kind")
    ensure(payload.get("reviewed_on") == "2026-07-26", "review date differs")
    ensure(payload.get("observation_date") == "2025-10-20", "observation date differs")
    ensure(payload.get("source_code") == SOURCE_CODE, "source code differs")
    ensure(payload.get("source_pages") == [20, 21], "source pages differ")
    ensure(payload.get("value_id_start") == 2420, "value ID start differs")
    ensure(payload.get("range_id_start") == 235, "range ID start differs")

    groups = payload.get("groups")
    ensure(isinstance(groups, list) and len(groups) == 3, "expected three represented powertrain groups")
    seen: set[str] = set()
    for group in groups:
        ensure(isinstance(group, dict), "group must be an object")
        code = str(group.get("code", ""))
        ensure(code in EXPECTED_GROUPS, f"unexpected group: {code}")
        expected_count, _, _, expected_page = EXPECTED_GROUPS[code]
        ensure(group.get("source_page") == expected_page, f"source page differs: {code}")
        configurations = group.get("configurations")
        ensure(isinstance(configurations, list) and len(configurations) == expected_count, f"configuration count differs: {code}")
        for configuration in configurations:
            ensure(isinstance(configuration, str) and configuration not in seen, f"duplicate configuration: {configuration}")
            seen.add(configuration)

        scalars = group.get("scalar_observations")
        ensure(isinstance(scalars, list) and len(scalars) == 6, f"scalar observation count differs: {code}")
        ensure({str(item.get("attribute_code", "")) for item in scalars if isinstance(item, dict)} == set(SCALAR_CONTRACTS), f"scalar attribute set differs: {code}")
        for item in scalars:
            ensure(isinstance(item, dict) and set(item) == {"attribute_code", "value", "source_text"}, f"scalar fields differ: {code}")
            attribute = str(item["attribute_code"])
            validate_scalar(SCALAR_CONTRACTS[attribute][0], str(item["value"]), f"{code}.{attribute}")
            ensure(str(item["source_text"]).strip(), f"empty source text: {code}.{attribute}")

        payload_range = group.get("payload_range")
        ensure(isinstance(payload_range, dict), f"payload range missing: {code}")
        ensure(set(payload_range) == {
            "attribute_code", "minimum_value", "maximum_value", "lower_inclusive",
            "upper_inclusive", "source_order_text", "source_text", "interpretation",
        }, f"payload range fields differ: {code}")
        ensure(payload_range.get("attribute_code") == "payload", f"payload attribute differs: {code}")
        minimum = validate_integer_endpoint(str(payload_range["minimum_value"]), f"{code}.payload.minimum")
        maximum = validate_integer_endpoint(str(payload_range["maximum_value"]), f"{code}.payload.maximum")
        ensure(minimum < maximum, f"payload interval is not increasing: {code}")
        ensure(payload_range.get("lower_inclusive") is True and payload_range.get("upper_inclusive") is True, f"payload range must be closed: {code}")
        ensure(payload_range.get("source_order_text") == f"{minimum}/{maximum}", f"source order text differs: {code}")
        ensure("without assigning maximum/minimum meaning" in str(payload_range.get("interpretation", "")), f"range interpretation differs: {code}")
        ensure(str(payload_range.get("source_text", "")).strip(), f"range source text missing: {code}")

    ensure(seen == EXPECTED_CONFIGURATIONS, "target configuration set differs")
    exclusions = payload.get("excluded_evidence")
    ensure(isinstance(exclusions, list), "excluded evidence is missing")
    ensure({str(item.get("code", "")) for item in exclusions if isinstance(item, dict)} == EXPECTED_EXCLUSIONS, "exclusion boundary set differs")
    return payload


def verify_source() -> None:
    registry = {row["code"]: row for row in read_rows(MASTER / "sources.csv")}
    row = registry.get(SOURCE_CODE)
    ensure(row is not None and row.get("status") == "active", "active source missing")
    ensure(row.get("source_type") == "brochure_pdf", "source type differs")
    ensure(row.get("publisher") == "Dacia" and row.get("market") == "PL", "source identity differs")
    ensure(row.get("document_date") == "2025-10-20", "source date differs")
    ensure(row.get("file_path") == "PDF/Broszury/DACIA DUSTER mini broszura 20251020.pdf", "source path differs")
    ensure(row.get("sha256") == SOURCE_SHA, "source registry hash differs")
    ensure(SOURCE_PATH.is_file() and file_sha256(SOURCE_PATH) == SOURCE_SHA, "archived source hash differs")


def verify_references(spec: Mapping[str, Any]) -> None:
    attributes = {row["code"]: row for row in read_rows(MASTER / "attributes.csv")}
    for code, contract in SCALAR_CONTRACTS.items():
        row = attributes.get(code)
        ensure(row is not None, f"attribute missing: {code}")
        ensure((row.get("data_type"), row.get("unit"), row.get("status")) == contract, f"attribute contract differs: {code}")
    payload_code, data_type, unit, status = RANGE_CONTRACT
    payload_attribute = attributes.get(payload_code)
    ensure(payload_attribute is not None, "payload attribute missing")
    ensure((payload_attribute.get("data_type"), payload_attribute.get("unit"), payload_attribute.get("status")) == (data_type, unit, status), "payload attribute contract differs")

    configurations = {row["code"]: row for row in read_rows(MASTER / "configurations.csv")}
    group_by_configuration = {
        str(configuration): str(group["code"])
        for group in spec["groups"]
        for configuration in group["configurations"]
    }
    for code in EXPECTED_CONFIGURATIONS:
        row = configurations.get(code)
        ensure(row is not None and row.get("status") == "active", f"active configuration missing: {code}")
        _, powertrain, transmission, _ = EXPECTED_GROUPS[group_by_configuration[code]]
        ensure(row.get("powertrain_label") == powertrain, f"powertrain differs: {code}")
        ensure(row.get("transmission_type") == transmission, f"transmission differs: {code}")

    relationships = {
        (row.get("source_code", ""), row.get("configuration_code", ""), row.get("relationship", ""))
        for row in read_rows(MASTER / "source_configurations.csv")
    }
    for code in EXPECTED_CONFIGURATIONS:
        ensure((SOURCE_CODE, code, "brochure_technical_data_for") in relationships, f"source relationship missing: {code}")

    automatic_ecog = {
        row["code"] for row in configurations.values()
        if row.get("status") == "active"
        and row.get("powertrain_label") == "Eco-G 120 4x2"
        and row.get("transmission_type") == "automatic"
    }
    ensure(len(automatic_ecog) == 3 and not (automatic_ecog & EXPECTED_CONFIGURATIONS), "automatic Eco-G boundary differs")
    ensure(
        not any(
            row.get("status") == "active"
            and row.get("code", "").startswith("duster_")
            and row.get("powertrain_label") == "hybrid-G 150 4x4"
            for row in configurations.values()
        ),
        "unexpected active exact hybrid-G 150 configuration",
    )


def expected_scalar_rows(spec: Mapping[str, Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for group in spec["groups"]:
        page = str(group["source_page"])
        for configuration in group["configurations"]:
            for observation in group["scalar_observations"]:
                attribute = str(observation["attribute_code"])
                result.append({
                    "id": str(int(spec["value_id_start"]) + len(result)),
                    "code": f"{configuration}_{attribute}_20251020",
                    "configuration_code": str(configuration),
                    "attribute_code": attribute,
                    "fuel_type_code": "",
                    "gear_number": "",
                    "value": str(observation["value"]),
                    "observation_date": str(spec["observation_date"]),
                    "source_code": SOURCE_CODE,
                    "notes": f"Source page {page}, section {spec['source_section']}: {observation['source_text']}",
                })
    ensure(len(result) == 60, "expected 60 scalar values")
    ensure([int(row["id"]) for row in result] == list(range(2420, 2480)), "scalar IDs differ")
    ensure(len({row["code"] for row in result}) == 60, "scalar codes are not unique")
    ensure(Counter(row["attribute_code"] for row in result) == Counter({code: 10 for code in SCALAR_CONTRACTS}), "scalar attribute distribution differs")
    return result


def expected_range_rows(spec: Mapping[str, Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for group in spec["groups"]:
        page = str(group["source_page"])
        payload_range = group["payload_range"]
        for configuration in group["configurations"]:
            result.append({
                "id": str(int(spec["range_id_start"]) + len(result)),
                "code": f"{configuration}_payload_20251020_range",
                "configuration_code": str(configuration),
                "attribute_code": "payload",
                "fuel_type_code": "",
                "minimum_value": str(payload_range["minimum_value"]),
                "maximum_value": str(payload_range["maximum_value"]),
                "lower_inclusive": "true",
                "upper_inclusive": "true",
                "observation_date": str(spec["observation_date"]),
                "source_code": SOURCE_CODE,
                "notes": (
                    f"Source page {page}, section {spec['source_section']}: {payload_range['source_text']}. "
                    f"Source order {payload_range['source_order_text']} is retained in provenance; "
                    "numeric endpoints are stored as a closed interval without semantic reassignment."
                ),
            })
    ensure(len(result) == 10, "expected 10 payload ranges")
    ensure([int(row["id"]) for row in result] == list(range(235, 245)), "range IDs differ")
    ensure(len({row["code"] for row in result}) == 10, "range codes are not unique")
    return result


def plan_rows(path: Path, fields: Sequence[str], expected: Sequence[Mapping[str, str]], *, range_table: bool) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    require_header(path, fields)
    current = read_rows(path)
    by_id = {row["id"]: row for row in current}
    by_code = {row["code"]: row for row in current}
    if range_table:
        identities = {
            (row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["observation_date"]): row
            for row in current
        }
    else:
        identities = {
            (row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["gear_number"], row["observation_date"]): row
            for row in current
        }
    missing: list[dict[str, str]] = []
    existing: list[dict[str, str]] = []
    for expected_row in expected:
        row = dict(expected_row)
        matched = by_code.get(row["code"])
        if matched is not None:
            ensure(matched == row, f"existing row differs: {row['code']}")
            existing.append(row)
            continue
        if range_table:
            identity = (row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["observation_date"])
        else:
            identity = (row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["gear_number"], row["observation_date"])
        ensure(row["id"] not in by_id, f"ID already used: {row['id']}")
        ensure(identity not in identities, f"observation identity already used: {identity}")
        missing.append(row)
    return missing, existing


def apply_rows(path: Path, fields: Sequence[str], expected: Sequence[Mapping[str, str]], *, range_table: bool) -> None:
    missing, _ = plan_rows(path, fields, expected, range_table=range_table)
    if missing:
        write_rows_atomic(path, fields, [*read_rows(path), *missing])


def verify_package(scalars: Sequence[Mapping[str, str]], ranges: Sequence[Mapping[str, str]]) -> None:
    missing_scalar, existing_scalar = plan_rows(VALUE_PATH, VALUE_FIELDS, scalars, range_table=False)
    ensure(not missing_scalar and len(existing_scalar) == 60, f"scalar package incomplete: missing={len(missing_scalar)}, existing={len(existing_scalar)}")
    missing_range, existing_range = plan_rows(RANGE_PATH, RANGE_FIELDS, ranges, range_table=True)
    ensure(not missing_range and len(existing_range) == 10, f"range package incomplete: missing={len(missing_range)}, existing={len(existing_range)}")
    scalar_slice = [row for row in read_rows(VALUE_PATH) if 2420 <= int(row["id"]) <= 2479]
    range_slice = [row for row in read_rows(RANGE_PATH) if 235 <= int(row["id"]) <= 244]
    ensure(scalar_slice == [dict(row) for row in scalars], "scalar ID slice differs")
    ensure(range_slice == [dict(row) for row in ranges], "range ID slice differs")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        spec = load_spec()
        verify_source()
        verify_references(spec)
        scalars = expected_scalar_rows(spec)
        ranges = expected_range_rows(spec)
        if args.apply:
            apply_rows(VALUE_PATH, VALUE_FIELDS, scalars, range_table=False)
            apply_rows(RANGE_PATH, RANGE_FIELDS, ranges, range_table=True)
        verify_package(scalars, ranges)
    except (ImportContractError, OSError, ValueError, KeyError, TypeError) as error:
        print(f"ERROR: {error}")
        return 1
    print("PASS: Duster brochure chassis observations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
