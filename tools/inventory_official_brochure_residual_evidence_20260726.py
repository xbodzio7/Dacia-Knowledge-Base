#!/usr/bin/env python3
"""Inventory residual official brochure evidence and current dimension coverage."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORTING = ROOT / "data" / "reporting"

SOURCES = {
    "src_pl_sandero_brochure_20260202": "sandero_iii",
    "src_pl_sandero_stepway_brochure_20260202": "sandero_stepway_iii",
    "src_pl_jogger_brochure_20251217": "jogger",
    "src_pl_bigster_brochure_20251210": "bigster",
    "src_pl_duster_mini_brochure_20251020": "duster_iii",
}
DIMENSION_KEYWORDS = (
    "length",
    "width",
    "height",
    "wheelbase",
    "track",
    "clearance",
    "overhang",
    "approach",
    "departure",
    "breakover",
    "angle",
    "wading",
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def print_json(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))


def main() -> int:
    review = json.loads((REPORTING / "official_brochure_technical_gap_review.json").read_text(encoding="utf-8"))
    closure = json.loads((REPORTING / "official_brochure_technical_gap_resolution_closure_review.json").read_text(encoding="utf-8"))
    residual_codes = set(closure["residual_evidence"]["classification_codes"])
    classifications = [item for item in review["classifications"] if item["code"] in residual_codes]

    print("=== RESIDUAL CLASSIFICATIONS ===")
    for item in classifications:
        print_json(item)

    attributes = rows(MASTER / "attributes.csv")
    dimension_attributes = [
        row
        for row in attributes
        if row.get("status") == "active"
        and (
            row.get("category", "").lower() in {"dimensions", "off-road"}
            or any(keyword in row.get("code", "").lower() for keyword in DIMENSION_KEYWORDS)
        )
    ]
    print("\n=== ACTIVE DIMENSION-LIKE ATTRIBUTES ===")
    for row in dimension_attributes:
        print_json({key: row.get(key, "") for key in ("id", "code", "name", "category", "data_type", "unit", "description")})

    configurations = rows(MASTER / "configurations.csv")
    versions = {row["code"]: row for row in rows(MASTER / "versions.csv")}
    active_by_model: dict[str, list[dict[str, str]]] = {model: [] for model in SOURCES.values()}
    for row in configurations:
        if row.get("status") != "active":
            continue
        version = versions.get(row.get("version_code", ""), {})
        model = version.get("model_code", "")
        if model in active_by_model:
            active_by_model[model].append(row)

    print("\n=== ACTIVE CONFIGURATION PROJECTION SCOPES ===")
    for source, model in SOURCES.items():
        selected = active_by_model[model]
        print_json(
            {
                "source_code": source,
                "model_code": model,
                "configurations": len(selected),
                "powertrains": dict(Counter(row.get("powertrain_label", "") for row in selected)),
                "transmissions": dict(Counter(row.get("transmission_type", "") for row in selected)),
                "drive_types": dict(Counter(row.get("drive_type_code", "") for row in selected)),
                "codes": sorted(row["code"] for row in selected),
            }
        )

    values = rows(MASTER / "configuration_attribute_values.csv")
    dimension_codes = {row["code"] for row in dimension_attributes}
    print("\n=== CURRENT BROCHURE DIMENSION VALUES ===")
    current = [
        row
        for row in values
        if row.get("source_code") in SOURCES and row.get("attribute_code") in dimension_codes
    ]
    for row in current:
        print_json(row)
    print_json(
        {
            "rows": len(current),
            "attributes": dict(Counter(row.get("attribute_code", "") for row in current)),
            "sources": dict(Counter(row.get("source_code", "") for row in current)),
        }
    )

    print("\n=== EXISTING DIMENSION VALUES BY ACTIVE MODEL ===")
    configuration_model = {
        row["code"]: versions.get(row.get("version_code", ""), {}).get("model_code", "")
        for row in configurations
    }
    for model in active_by_model:
        selected = [
            row
            for row in values
            if configuration_model.get(row.get("configuration_code", "")) == model
            and row.get("attribute_code") in dimension_codes
        ]
        print_json(
            {
                "model_code": model,
                "rows": len(selected),
                "attributes": dict(Counter(row.get("attribute_code", "") for row in selected)),
                "sources": dict(Counter(row.get("source_code", "") for row in selected)),
            }
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
