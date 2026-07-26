#!/usr/bin/env python3
"""Build a temporary inventory for Jogger brochure hybrid performance completion."""

from __future__ import annotations

import csv
import json
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

    seat_values = {
        row["configuration_code"]: row["value"]
        for row in values
        if row.get("configuration_code") in configurations
        and row.get("attribute_code") == "number_of_seats"
    }

    print("=== ATTRIBUTE CONTRACTS ===")
    for code in sorted(ATTRIBUTES):
        print(json.dumps(attributes.get(code), ensure_ascii=False, sort_keys=True))

    print("\n=== ACTIVE JOGGER CONFIGURATIONS ===")
    for code, row in sorted(configurations.items()):
        print(json.dumps({
            **row,
            "number_of_seats": seat_values.get(code, ""),
        }, ensure_ascii=False, sort_keys=True))

    print("\n=== CURRENT SCALAR VALUES ===")
    for row in values:
        if (
            row.get("configuration_code") in configurations
            and row.get("attribute_code") in ATTRIBUTES
        ):
            print(json.dumps(row, ensure_ascii=False, sort_keys=True))

    print("\n=== CURRENT RANGE VALUES ===")
    for row in ranges:
        if (
            row.get("configuration_code") in configurations
            and row.get("attribute_code") in ATTRIBUTES
        ):
            print(json.dumps(row, ensure_ascii=False, sort_keys=True))

    print("\n=== SOURCE RELATIONSHIPS ===")
    for row in relationships:
        if row.get("source_code") == SOURCE and row.get("configuration_code") in configurations:
            print(json.dumps(row, ensure_ascii=False, sort_keys=True))

    print("\n=== MASTER ID BOUNDARIES ===")
    print(json.dumps({
        "configuration_attribute_values_max_id": max(int(row["id"]) for row in values),
        "configuration_attribute_value_ranges_max_id": max(int(row["id"]) for row in ranges),
        "source_configurations_max_id": max(int(row["id"]) for row in relationships),
    }, ensure_ascii=False, sort_keys=True))

    print("\n=== REPORTING SPECS REFERENCING JOGGER TARGETS OR ATTRIBUTES ===")
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
                item
                for item in payload["technical_slots"]
                if isinstance(item, dict) and item.get("attribute_code") in ATTRIBUTES
            ]
        relevant_decisions = []
        if isinstance(payload, dict) and isinstance(payload.get("decisions"), list):
            relevant_decisions = [
                item
                for item in payload["decisions"]
                if isinstance(item, dict)
                and item.get("configuration_code") in configuration_codes
                and item.get("attribute_code") in ATTRIBUTES
            ]
        print(json.dumps({
            "path": path.relative_to(ROOT).as_posix(),
            "target_refs": target_refs,
            "attribute_refs": attribute_refs,
            "technical_slots": technical_slots,
            "relevant_decisions": relevant_decisions,
        }, ensure_ascii=False, sort_keys=True))

    print("\n=== DECLARATIVE RANGE IMPORT EXAMPLES ===")
    range_spec_roots = (
        ROOT / "data" / "imports" / "configuration_value_ranges",
        ROOT / "data" / "imports" / "configuration_attribute_value_ranges",
        ROOT / "data" / "imports" / "configuration_ranges",
    )
    found = 0
    for directory in range_spec_roots:
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.json")):
            print(path.relative_to(ROOT).as_posix())
            print(path.read_text(encoding="utf-8"))
            found += 1
            if found >= 4:
                break
        if found >= 4:
            break
    print(f"range_spec_examples={found}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
