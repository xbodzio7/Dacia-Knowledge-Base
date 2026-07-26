#!/usr/bin/env python3
"""Build a temporary inventory for Bigster and Duster brochure towing masses."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
ATTRIBUTES = {"gross_train_weight", "unbraked_trailer_weight"}
SOURCES = {
    "src_pl_bigster_brochure_20251210",
    "src_pl_duster_mini_brochure_20251020",
}


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    configurations = {
        row["code"]: row
        for row in rows("configurations.csv")
        if row.get("status") == "active"
        and row.get("code", "").startswith(("bigster_", "duster_iii_"))
    }
    values = rows("configuration_attribute_values.csv")
    relationships = rows("source_configurations.csv")
    attributes = {row["code"]: row for row in rows("attributes.csv")}

    print("=== ATTRIBUTE CONTRACTS ===")
    for code in sorted(ATTRIBUTES):
        print(json.dumps(attributes[code], ensure_ascii=False, sort_keys=True))

    print("\n=== ACTIVE CONFIGURATIONS ===")
    for code, row in sorted(configurations.items()):
        print(json.dumps(row, ensure_ascii=False, sort_keys=True))

    print("\n=== EXISTING TARGET ATTRIBUTE VALUES ===")
    for row in values:
        if (
            row.get("configuration_code") in configurations
            and row.get("attribute_code") in ATTRIBUTES
        ):
            print(json.dumps(row, ensure_ascii=False, sort_keys=True))

    print("\n=== BROCHURE SOURCE RELATIONSHIPS ===")
    for row in relationships:
        if (
            row.get("source_code") in SOURCES
            and row.get("configuration_code") in configurations
        ):
            print(json.dumps(row, ensure_ascii=False, sort_keys=True))

    print("\n=== EXACT REVIEW CANDIDATES ===")
    bigster = sorted(code for code in configurations if code.startswith("bigster_"))
    duster = sorted(
        code
        for code, row in configurations.items()
        if code.startswith("duster_iii_")
        and (
            (
                row.get("powertrain_label") == "Eco-G 120 4x2"
                and row.get("transmission_type") == "manual"
            )
            or row.get("powertrain_label")
            in {"mild hybrid 140 4x2", "hybrid 155 4x2"}
        )
    )
    print(json.dumps({"bigster": bigster, "duster": duster}, ensure_ascii=False, indent=2))
    print(f"bigster_count={len(bigster)}")
    print(f"duster_count={len(duster)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
