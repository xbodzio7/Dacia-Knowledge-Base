#!/usr/bin/env python3
"""Import exact Bigster brochure chassis observations."""

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
SPEC_PATH = ROOT / "data" / "imports" / "brochure_technical_values" / "bigster-chassis-20251210.json"
VALUE_PATH = MASTER / "configuration_attribute_values.csv"
SOURCE_CODE = "src_pl_bigster_brochure_20251210"
SOURCE_PATH = ROOT / "PDF" / "Broszury" / "DACIA BIGSTER broszura 20251210.pdf"
SOURCE_SHA = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"
VALUE_FIELDS = (
    "id", "code", "configuration_code", "attribute_code", "fuel_type_code",
    "gear_number", "value", "observation_date", "source_code", "notes",
)
ATTRIBUTE_CONTRACTS = {
    "turning_circle_between_kerbs": ("decimal", "m", "active"),
    "maximum_kerb_weight": ("integer", "kg", "active"),
    "steering_type": ("string", "", "active"),
    "front_brake_type": ("string", "", "active"),
    "rear_brake_type": ("string", "", "active"),
    "standard_tyre_specification": ("string", "", "active"),
}
EXPECTED_GROUPS = {
    "mildhybridg140_4x2_manual": (4, "mild hybrid-G 140 4x2", "manual"),
    "mildhybrid140_4x2_manual": (4, "mild hybrid 140 4x2", "manual"),
    "hybridg150_4x4_automatic": (3, "hybrid-G 150 4x4", "automatic"),
    "hybrid155_4x2_automatic": (3, "hybrid 155 4x2", "automatic"),
}
EXPECTED_CONFIGURATIONS = {
    "bigster_essential_mildhybrid140_4x2_manual",
    "bigster_expression_mildhybrid140_4x2_manual",
    "bigster_extreme_mildhybrid140_4x2_manual",
    "bigster_journey_mildhybrid140_4x2_manual",
    "bigster_essential_mildhybridg140_4x2_manual",
    "bigster_expression_mildhybridg140_4x2_manual",
    "bigster_extreme_mildhybridg140_4x2_manual",
    "bigster_journey_mildhybridg140_4x2_manual",
    "bigster_expression_hybrid155_4x2_automatic",
    "bigster_extreme_hybrid155_4x2_automatic",
    "bigster_journey_hybrid155_4x2_automatic",
    "bigster_expression_hybridg150_4x4_automatic",
    "bigster_extreme_hybridg150_4x4_automatic",
    "bigster_journey_hybridg150_4x4_automatic",
}


class ImportContractError(RuntimeError):
    pass


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_value(data_type: str, value: str, label: str) -> None:
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
        ensure(value.strip() == value, f"noncanonical string: {label}")
    else:
        raise ImportContractError(f"unsupported type: {data_type}")


def load_spec() -> dict[str, Any]:
    payload = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    ensure(payload.get("version") == 1, "unsupported spec version")
    ensure(payload.get("kind") == "bigster_chassis_observations", "unexpected spec kind")
    ensure(payload.get("reviewed_on") == "2026-07-26", "review date differs")
    ensure(payload.get("observation_date") == "2025-12-10", "observation date differs")
    ensure(payload.get("source_code") == SOURCE_CODE, "source code differs")
    ensure(payload.get("source_page") == 20, "source page differs")
    ensure(payload.get("value_id_start") == 2336, "ID start differs")
    groups = payload.get("groups")
    ensure(isinstance(groups, list) and len(groups) == 4, "expected four groups")
    configurations: set[str] = set()
    for group in groups:
        ensure(isinstance(group, dict), "group must be an object")
        code = str(group.get("code", ""))
        ensure(code in EXPECTED_GROUPS, f"unexpected group: {code}")
        expected_count, _, _ = EXPECTED_GROUPS[code]
        targets = group.get("configurations")
        ensure(isinstance(targets, list) and len(targets) == expected_count, f"configuration count differs: {code}")
        for target in targets:
            ensure(isinstance(target, str) and target not in configurations, f"duplicate configuration: {target}")
            configurations.add(target)
        observations = group.get("observations")
        ensure(isinstance(observations, list) and len(observations) == 6, f"observation count differs: {code}")
        ensure({str(item.get("attribute_code", "")) for item in observations if isinstance(item, dict)} == set(ATTRIBUTE_CONTRACTS), f"attribute set differs: {code}")
        for item in observations:
            ensure(isinstance(item, dict) and set(item) == {"attribute_code", "value", "source_text"}, f"observation fields differ: {code}")
            attribute = str(item["attribute_code"])
            validate_value(ATTRIBUTE_CONTRACTS[attribute][0], str(item["value"]), f"{code}.{attribute}")
            ensure(str(item["source_text"]).strip(), f"source text missing: {code}.{attribute}")
    ensure(configurations == EXPECTED_CONFIGURATIONS, "configuration set differs")
    excluded = payload.get("excluded_evidence")
    ensure(isinstance(excluded, list) and {str(item.get("code", "")) for item in excluded if isinstance(item, dict)} == {
        "cargo_rows_out_of_scope", "payload_range_follow_up", "legacy_turning_circle_not_rewritten", "later_my26_values_remain_current"
    }, "exclusion set differs")
    return payload


def verify_source() -> None:
    registry = {row["code"]: row for row in read_rows(MASTER / "sources.csv")}
    row = registry.get(SOURCE_CODE)
    ensure(row is not None and row.get("status") == "active", "active source missing")
    ensure(row.get("source_type") == "brochure_pdf", "source type differs")
    ensure(row.get("document_date") == "2025-12-10", "source date differs")
    ensure(row.get("file_path") == "PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf", "source path differs")
    ensure(row.get("sha256") == SOURCE_SHA, "source registry hash differs")
    ensure(SOURCE_PATH.is_file() and sha256(SOURCE_PATH) == SOURCE_SHA, "archived source hash differs")


def verify_references(spec: Mapping[str, Any]) -> None:
    attributes = {row["code"]: row for row in read_rows(MASTER / "attributes.csv")}
    for code, contract in ATTRIBUTE_CONTRACTS.items():
        row = attributes.get(code)
        ensure(row is not None, f"attribute missing: {code}")
        ensure((row.get("data_type"), row.get("unit"), row.get("status")) == contract, f"attribute contract differs: {code}")

    configurations = {row["code"]: row for row in read_rows(MASTER / "configurations.csv")}
    group_by_configuration = {
        str(configuration): str(group["code"])
        for group in spec["groups"]
        for configuration in group["configurations"]
    }
    for code in EXPECTED_CONFIGURATIONS:
        row = configurations.get(code)
        ensure(row is not None and row.get("status") == "active", f"active configuration missing: {code}")
        _, powertrain, transmission = EXPECTED_GROUPS[group_by_configuration[code]]
        ensure(row.get("powertrain_label") == powertrain, f"powertrain differs: {code}")
        ensure(row.get("transmission_type") == transmission, f"transmission differs: {code}")

    relationships = {
        (row.get("source_code", ""), row.get("configuration_code", ""), row.get("relationship", ""))
        for row in read_rows(MASTER / "source_configurations.csv")
    }
    for code in EXPECTED_CONFIGURATIONS:
        ensure((SOURCE_CODE, code, "brochure_technical_data_for") in relationships, f"relationship missing: {code}")


def expected_rows(spec: Mapping[str, Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for group in spec["groups"]:
        for configuration in group["configurations"]:
            for observation in group["observations"]:
                attribute = str(observation["attribute_code"])
                result.append({
                    "id": str(int(spec["value_id_start"]) + len(result)),
                    "code": f"{configuration}_{attribute}_20251210",
                    "configuration_code": str(configuration),
                    "attribute_code": attribute,
                    "fuel_type_code": "",
                    "gear_number": "",
                    "value": str(observation["value"]),
                    "observation_date": str(spec["observation_date"]),
                    "source_code": SOURCE_CODE,
                    "notes": f"Source page {spec['source_page']}, section {spec['source_section']}: {observation['source_text']}",
                })
    ensure(len(result) == 84, "expected 84 generated values")
    ensure([int(row["id"]) for row in result] == list(range(2336, 2420)), "generated IDs differ")
    ensure(len({row["code"] for row in result}) == 84, "generated codes are not unique")
    ensure(Counter(row["attribute_code"] for row in result) == Counter({code: 14 for code in ATTRIBUTE_CONTRACTS}), "attribute distribution differs")
    return result


def plan(expected: Sequence[Mapping[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    require_header(VALUE_PATH, VALUE_FIELDS)
    current = read_rows(VALUE_PATH)
    by_id = {row["id"]: row for row in current}
    by_code = {row["code"]: row for row in current}
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
        identity = (row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["gear_number"], row["observation_date"])
        ensure(row["id"] not in by_id, f"ID already used: {row['id']}")
        ensure(identity not in identities, f"identity already used: {identity}")
        missing.append(row)
    return missing, existing


def apply(expected: Sequence[Mapping[str, str]]) -> None:
    missing, _ = plan(expected)
    if not missing:
        return
    write_rows_atomic(VALUE_PATH, VALUE_FIELDS, [*read_rows(VALUE_PATH), *missing])


def verify_package(expected: Sequence[Mapping[str, str]]) -> None:
    missing, existing = plan(expected)
    ensure(not missing and len(existing) == 84, f"package incomplete: missing={len(missing)}, existing={len(existing)}")
    package = [row for row in read_rows(VALUE_PATH) if 2336 <= int(row["id"]) <= 2419]
    ensure(package == [dict(row) for row in expected], "package ID slice differs")


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
        expected = expected_rows(spec)
        if args.apply:
            apply(expected)
        verify_package(expected)
    except (ImportContractError, OSError, ValueError, KeyError, TypeError) as error:
        print(f"ERROR: {error}")
        return 1
    print("PASS: Bigster brochure chassis observations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
