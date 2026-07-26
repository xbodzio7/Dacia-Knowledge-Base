#!/usr/bin/env python3
"""Build a temporary inventory for Sandero and Stepway brochure chassis evidence."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORTING = ROOT / "data" / "reporting"
SOURCES = {
    "src_pl_sandero_brochure_20260202",
    "src_pl_sandero_stepway_brochure_20260202",
}
ATTRIBUTES = {
    "turning_circle",
    "turning_circle_between_kerbs",
    "maximum_kerb_weight",
    "standard_tyre_specification",
    "front_suspension",
    "rear_suspension",
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
        if row.get("status") == "active"
        and (
            row.get("code", "").startswith("sandero_iii_")
            or row.get("code", "").startswith("sandero_stepway_iii_")
        )
    ]
    emit("ACTIVE CONFIGURATIONS", [
        {
            "id": row["id"],
            "code": row["code"],
            "version_code": row["version_code"],
            "powertrain_label": row["powertrain_label"],
            "transmission_type": row["transmission_type"],
            "number_of_seats": row["number_of_seats"],
        }
        for row in configurations
    ])

    relationships = [
        row for row in rows(MASTER / "source_configurations.csv")
        if row.get("source_code") in SOURCES
        and row.get("configuration_code") in {item["code"] for item in configurations}
    ]
    emit("SOURCE RELATIONSHIPS", relationships)

    values = [
        row for row in rows(MASTER / "configuration_attribute_values.csv")
        if row.get("configuration_code") in {item["code"] for item in configurations}
        and row.get("attribute_code") in ATTRIBUTES
    ]
    emit("CURRENT CHASSIS VALUES", values)

    attributes = {
        row["code"]: row for row in rows(MASTER / "attributes.csv")
        if row.get("code") in ATTRIBUTES
    }
    emit("ATTRIBUTE CONTRACTS", [attributes[code] for code in sorted(attributes)])

    reporting: list[dict[str, object]] = []
    for path in sorted(REPORTING.glob("*.json")):
        text = path.read_text(encoding="utf-8")
        refs = sorted(code for code in ATTRIBUTES if code in text)
        if refs:
            reporting.append({"path": str(path.relative_to(ROOT)), "attribute_refs": refs})
    emit("REPORTING REFERENCES", reporting)

    scalar = rows(MASTER / "configuration_attribute_values.csv")
    ranges = rows(MASTER / "configuration_attribute_value_ranges.csv")
    source_links = rows(MASTER / "source_configurations.csv")
    print("\n=== ID BOUNDARIES ===")
    print(json.dumps({
        "configuration_attribute_values_max_id": max(int(row["id"]) for row in scalar),
        "configuration_attribute_value_ranges_max_id": max(int(row["id"]) for row in ranges),
        "source_configurations_max_id": max(int(row["id"]) for row in source_links),
    }, sort_keys=True))

    print("\n=== SUMMARY ===")
    print(json.dumps({
        "configurations": len(configurations),
        "by_model_prefix": Counter(
            "stepway" if row["code"].startswith("sandero_stepway_") else "sandero"
            for row in configurations
        ),
        "relationships": len(relationships),
        "relationship_types": Counter(row["relationship"] for row in relationships),
        "current_values": len(values),
        "current_value_attributes": Counter(row["attribute_code"] for row in values),
    }, default=dict, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
