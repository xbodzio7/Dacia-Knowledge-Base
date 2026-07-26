#!/usr/bin/env python3
"""Build a temporary inventory for Bigster brochure chassis evidence."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SOURCE = "src_pl_bigster_brochure_20251210"
ATTRIBUTES = {
    "turning_circle",
    "turning_circle_between_kerbs",
    "maximum_kerb_weight",
    "steering_type",
    "front_brake_type",
    "rear_brake_type",
    "standard_tyre_specification",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def emit(title: str, items: list[dict[str, object]]) -> None:
    print(f"\n=== {title} ===")
    for item in items:
        print(json.dumps(item, ensure_ascii=False, sort_keys=True))


def main() -> int:
    configurations = [
        row for row in rows(MASTER / "configurations.csv")
        if row.get("status") == "active" and row.get("code", "").startswith("bigster_")
    ]
    codes = {row["code"] for row in configurations}
    emit("ACTIVE BIGSTER CONFIGURATIONS", [
        {
            "id": row["id"],
            "code": row["code"],
            "version_code": row["version_code"],
            "powertrain_label": row["powertrain_label"],
            "transmission_type": row["transmission_type"],
            "notes": row.get("notes", ""),
        }
        for row in configurations
    ])

    relationships = [
        row for row in rows(MASTER / "source_configurations.csv")
        if row.get("source_code") == SOURCE and row.get("configuration_code") in codes
    ]
    emit("SOURCE RELATIONSHIPS", relationships)

    values = [
        row for row in rows(MASTER / "configuration_attribute_values.csv")
        if row.get("configuration_code") in codes and row.get("attribute_code") in ATTRIBUTES
    ]
    emit("CURRENT CHASSIS VALUES", values)

    contracts = [
        row for row in rows(MASTER / "attributes.csv")
        if row.get("code") in ATTRIBUTES
    ]
    emit("ATTRIBUTE CONTRACTS", contracts)

    scalar = rows(MASTER / "configuration_attribute_values.csv")
    ranges = rows(MASTER / "configuration_attribute_value_ranges.csv")
    links = rows(MASTER / "source_configurations.csv")
    print("\n=== ID BOUNDARIES ===")
    print(json.dumps({
        "configuration_attribute_values_max_id": max(int(row["id"]) for row in scalar),
        "configuration_attribute_value_ranges_max_id": max(int(row["id"]) for row in ranges),
        "source_configurations_max_id": max(int(row["id"]) for row in links),
    }, sort_keys=True))

    print("\n=== SUMMARY ===")
    print(json.dumps({
        "configurations": len(configurations),
        "powertrains": Counter(row["powertrain_label"] for row in configurations),
        "relationships": len(relationships),
        "relationship_types": Counter(row["relationship"] for row in relationships),
        "current_values": len(values),
        "current_attributes": Counter(row["attribute_code"] for row in values),
    }, default=dict, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
