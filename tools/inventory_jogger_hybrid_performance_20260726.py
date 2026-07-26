#!/usr/bin/env python3
"""Build a concise temporary inventory for Jogger brochure performance completion."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORTING = ROOT / "data" / "reporting"
SOURCE = "src_pl_jogger_brochure_20251217"
ATTRIBUTES = {
    "acceleration_0_100",
    "hybrid_battery_capacity_source_stated",
    "max_power_rpm",
    "max_torque_rpm",
}


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def strings(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        result: set[str] = set()
        for item in value:
            result.update(strings(item))
        return result
    if isinstance(value, dict):
        result = set()
        for item in value.values():
            result.update(strings(item))
        return result
    return set()


def main() -> int:
    configurations = {
        row["code"]: row
        for row in rows("configurations.csv")
        if row.get("status") == "active" and row.get("code", "").startswith("jogger_")
    }
    values = rows("configuration_attribute_values.csv")
    ranges = rows("configuration_attribute_value_ranges.csv")
    relationships = rows("source_configurations.csv")
    attributes = {row["code"]: row for row in rows("attributes.csv")}
    seats = {
        row["configuration_code"]: row["value"]
        for row in values
        if row.get("configuration_code") in configurations
        and row.get("attribute_code") == "number_of_seats"
    }

    print("=== ATTRIBUTE CONTRACTS ===")
    for code in sorted(ATTRIBUTES):
        print(json.dumps(attributes.get(code), ensure_ascii=False, sort_keys=True))

    print("\n=== CONFIGURATION DISTRIBUTION ===")
    distribution = Counter(
        (
            row["powertrain_label"],
            row["transmission_type"],
            seats.get(code, ""),
        )
        for code, row in configurations.items()
    )
    for key, count in sorted(distribution.items()):
        print(json.dumps({
            "powertrain_label": key[0],
            "transmission_type": key[1],
            "number_of_seats": key[2],
            "configurations": count,
        }, ensure_ascii=False, sort_keys=True))

    scalar = [
        row for row in values
        if row.get("configuration_code") in configurations
        and row.get("attribute_code") in ATTRIBUTES
    ]
    range_rows = [
        row for row in ranges
        if row.get("configuration_code") in configurations
        and row.get("attribute_code") in ATTRIBUTES
    ]

    print("\n=== CURRENT SCALAR SUMMARY ===")
    print(json.dumps({
        "count": len(scalar),
        "attributes": Counter(row["attribute_code"] for row in scalar),
        "sources": Counter(row["source_code"] for row in scalar),
        "dates": Counter(row["observation_date"] for row in scalar),
    }, ensure_ascii=False, sort_keys=True))
    scalar_patterns: dict[tuple[str, ...], set[str]] = defaultdict(set)
    for row in scalar:
        configuration = configurations[row["configuration_code"]]
        key = (
            configuration["powertrain_label"],
            configuration["transmission_type"],
            seats.get(row["configuration_code"], ""),
            row["attribute_code"],
            row.get("fuel_type_code", ""),
            row["observation_date"],
            row["source_code"],
            row["value"],
        )
        scalar_patterns[key].add(row["configuration_code"])
    for key, codes in sorted(scalar_patterns.items()):
        print(json.dumps({
            "powertrain_label": key[0],
            "transmission_type": key[1],
            "number_of_seats": key[2],
            "attribute_code": key[3],
            "fuel_type_code": key[4],
            "observation_date": key[5],
            "source_code": key[6],
            "value": key[7],
            "configuration_count": len(codes),
        }, ensure_ascii=False, sort_keys=True))

    print("\n=== CURRENT RANGE SUMMARY ===")
    print(json.dumps({
        "count": len(range_rows),
        "attributes": Counter(row["attribute_code"] for row in range_rows),
        "sources": Counter(row["source_code"] for row in range_rows),
        "dates": Counter(row["observation_date"] for row in range_rows),
    }, ensure_ascii=False, sort_keys=True))
    range_patterns: dict[tuple[str, ...], set[str]] = defaultdict(set)
    for row in range_rows:
        configuration = configurations[row["configuration_code"]]
        key = (
            configuration["powertrain_label"],
            configuration["transmission_type"],
            seats.get(row["configuration_code"], ""),
            row["attribute_code"],
            row.get("fuel_type_code", ""),
            row["observation_date"],
            row["source_code"],
            row["minimum_value"],
            row["maximum_value"],
        )
        range_patterns[key].add(row["configuration_code"])
    for key, codes in sorted(range_patterns.items()):
        print(json.dumps({
            "powertrain_label": key[0],
            "transmission_type": key[1],
            "number_of_seats": key[2],
            "attribute_code": key[3],
            "fuel_type_code": key[4],
            "observation_date": key[5],
            "source_code": key[6],
            "minimum_value": key[7],
            "maximum_value": key[8],
            "configuration_count": len(codes),
        }, ensure_ascii=False, sort_keys=True))

    print("\n=== SOURCE RELATIONSHIP COVERAGE ===")
    source_relationships = [
        row for row in relationships
        if row.get("source_code") == SOURCE
        and row.get("configuration_code") in configurations
    ]
    covered = {row["configuration_code"] for row in source_relationships}
    print(json.dumps({
        "relationships": len(source_relationships),
        "covered_configurations": len(covered),
        "missing": sorted(set(configurations) - covered),
        "relationship_types": Counter(row["relationship"] for row in source_relationships),
    }, ensure_ascii=False, sort_keys=True))

    print("\n=== MASTER ID BOUNDARIES ===")
    print(json.dumps({
        "configuration_attribute_values_max_id": max(int(row["id"]) for row in values),
        "configuration_attribute_value_ranges_max_id": max(int(row["id"]) for row in ranges),
        "source_configurations_max_id": max(int(row["id"]) for row in relationships),
    }, ensure_ascii=False, sort_keys=True))

    print("\n=== REPORTING INTEGRATION ===")
    configuration_codes = set(configurations)
    for path in sorted(REPORTING.glob("*")):
        if path.suffix not in {".json", ".spec"}:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        payload_strings = strings(payload)
        target_refs = sorted(configuration_codes & payload_strings)
        attribute_refs = sorted(ATTRIBUTES & payload_strings)
        if not target_refs and not attribute_refs:
            continue
        technical_slots = []
        if isinstance(payload, dict) and isinstance(payload.get("technical_slots"), list):
            technical_slots = [
                item for item in payload["technical_slots"]
                if isinstance(item, dict) and item.get("attribute_code") in ATTRIBUTES
            ]
        relevant_decisions = []
        if isinstance(payload, dict) and isinstance(payload.get("decisions"), list):
            relevant_decisions = [
                item for item in payload["decisions"]
                if isinstance(item, dict)
                and item.get("configuration_code") in configuration_codes
                and item.get("attribute_code") in ATTRIBUTES
            ]
        print(json.dumps({
            "path": path.relative_to(ROOT).as_posix(),
            "target_ref_count": len(target_refs),
            "attribute_refs": attribute_refs,
            "technical_slots": technical_slots,
            "relevant_decision_count": len(relevant_decisions),
        }, ensure_ascii=False, sort_keys=True))

    print("\n=== RANGE IMPORT TOOLING ===")
    directory = ROOT / "data" / "imports" / "configuration_value_ranges"
    examples = sorted(path.name for path in directory.glob("*.json")) if directory.is_dir() else []
    print(json.dumps({
        "directory": directory.relative_to(ROOT).as_posix(),
        "spec_count": len(examples),
        "examples": examples[:8],
        "importer_exists": (ROOT / "tools" / "import_configuration_value_ranges.py").is_file(),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
