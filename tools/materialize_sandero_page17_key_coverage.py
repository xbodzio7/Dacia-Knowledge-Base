from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "project/tmp/sandero-page17-key-coverage.json"
SOURCE = "src_pl_sandero_brochure_20260202"
ATTRIBUTES = {
    "fuel_type",
    "engine_power",
    "engine_torque",
    "injection_type",
    "cylinder_count",
    "valves_per_cylinder",
    "total_valve_count",
    "acceleration_0_100",
    "elasticity_80_120",
    "maximum_kerb_weight",
    "gross_vehicle_weight",
    "gross_train_weight",
    "braked_trailer_weight",
    "unbraked_trailer_weight",
    "maximum_speed",
    "engine_displacement",
    "fuel_tank_capacity",
    "lpg_vessel_capacity_total",
    "lpg_vessel_filling_capacity",
}
RANGE_ATTRIBUTES = {
    "max_power_rpm",
    "max_torque_rpm",
    "engine_power_rpm",
    "engine_torque_rpm",
}


def rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def latest(records: list[dict[str, str]], key_fields: tuple[str, ...]) -> list[dict[str, str]]:
    selected: dict[tuple[str, ...], dict[str, str]] = {}
    for row in records:
        key = tuple(row[field] for field in key_fields)
        previous = selected.get(key)
        marker = (row["observation_date"], int(row["id"]))
        if previous is None or marker > (previous["observation_date"], int(previous["id"])):
            selected[key] = row
    return sorted(selected.values(), key=lambda row: tuple(row[field] for field in key_fields))


def slim(row: dict[str, str], range_row: bool = False) -> dict[str, str]:
    keys = [
        "configuration_code",
        "attribute_code",
        "fuel_type_code",
    ]
    if range_row:
        keys += ["minimum_value", "maximum_value"]
    else:
        keys += ["gear_number", "value"]
    keys += ["observation_date", "source_code", "code", "notes"]
    return {key: row.get(key, "") for key in keys}


def main() -> None:
    configs = [
        row for row in rows("data/master/configurations.csv")
        if row["status"] == "active" and row["code"].startswith("sandero_iii_")
    ]
    codes = {row["code"] for row in configs}
    values = [row for row in rows("data/master/configuration_attribute_values.csv") if row["configuration_code"] in codes]
    ranges = [row for row in rows("data/master/configuration_attribute_value_ranges.csv") if row["configuration_code"] in codes]

    same_page = [
        row for row in values
        if row["source_code"] == SOURCE and "page 17" in row["notes"].lower()
    ]
    same_page_ranges = [
        row for row in ranges
        if row["source_code"] == SOURCE and "page 17" in row["notes"].lower()
    ]
    key_values = [row for row in values if row["attribute_code"] in ATTRIBUTES]
    key_ranges = [row for row in ranges if row["attribute_code"] in RANGE_ATTRIBUTES or "rpm" in row["attribute_code"]]

    grouped_same: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in same_page:
        grouped_same[row["attribute_code"]].append(slim(row))
    grouped_latest: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in latest(key_values, ("configuration_code", "attribute_code", "fuel_type_code", "gear_number")):
        grouped_latest[row["attribute_code"]].append(slim(row))
    grouped_ranges: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in latest(key_ranges, ("configuration_code", "attribute_code", "fuel_type_code")):
        grouped_ranges[row["attribute_code"]].append(slim(row, range_row=True))

    payload = {
        "configurations": [
            {
                "code": row["code"],
                "powertrain_label": row["powertrain_label"],
                "transmission_type": row["transmission_type"],
            }
            for row in sorted(configs, key=lambda row: row["code"])
        ],
        "same_source_page17_scalar_count": len(same_page),
        "same_source_page17_range_count": len(same_page_ranges),
        "same_source_page17_by_attribute": dict(sorted(grouped_same.items())),
        "latest_key_values_by_attribute": dict(sorted(grouped_latest.items())),
        "latest_rpm_ranges_by_attribute": dict(sorted(grouped_ranges.items())),
        "configuration_identity": {
            row["code"]: {
                "powertrain_label": row["powertrain_label"],
                "transmission_type": row["transmission_type"],
            }
            for row in sorted(configs, key=lambda row: row["code"])
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
