from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "project/tmp/sandero-page17-reconciliation-diagnostic.json"
SOURCE = "src_pl_sandero_brochure_20260202"


def read_csv(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> None:
    configurations = [
        row
        for row in read_csv("data/master/configurations.csv")
        if row["code"].startswith("sandero_iii_") and row["status"] == "active"
    ]
    config_codes = {row["code"] for row in configurations}
    values = [
        row
        for row in read_csv("data/master/configuration_attribute_values.csv")
        if row["configuration_code"] in config_codes
    ]
    ranges = [
        row
        for row in read_csv("data/master/configuration_attribute_value_ranges.csv")
        if row["configuration_code"] in config_codes
    ]

    latest_values: dict[tuple[str, str, str, str], dict[str, str]] = {}
    for row in values:
        key = (
            row["configuration_code"],
            row["attribute_code"],
            row["fuel_type_code"],
            row["gear_number"],
        )
        previous = latest_values.get(key)
        if previous is None or (row["observation_date"], int(row["id"])) > (
            previous["observation_date"],
            int(previous["id"]),
        ):
            latest_values[key] = row

    latest_ranges: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in ranges:
        key = (row["configuration_code"], row["attribute_code"], row["fuel_type_code"])
        previous = latest_ranges.get(key)
        if previous is None or (row["observation_date"], int(row["id"])) > (
            previous["observation_date"],
            int(previous["id"]),
        ):
            latest_ranges[key] = row

    same_source_values = [row for row in values if row["source_code"] == SOURCE]
    same_source_ranges = [row for row in ranges if row["source_code"] == SOURCE]

    by_attribute: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in latest_values.values():
        by_attribute[row["attribute_code"]].append(row)
    range_by_attribute: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in latest_ranges.values():
        range_by_attribute[row["attribute_code"]].append(row)

    reviews = {
        "ambiguity": read_json("data/reporting/sandero_technical_page17_ambiguity_review.json"),
        "unresolved_chunk_1": read_json("data/reporting/sandero_technical_page17_unresolved_review_chunk1.json"),
        "unresolved_chunk_2": read_json("data/reporting/sandero_technical_page17_unresolved_review_chunk2.json"),
    }

    payload = {
        "source_code": SOURCE,
        "configurations": sorted(configurations, key=lambda row: row["code"]),
        "same_source_scalar_count": len(same_source_values),
        "same_source_range_count": len(same_source_ranges),
        "same_source_values": sorted(
            same_source_values,
            key=lambda row: (
                row["attribute_code"],
                row["configuration_code"],
                row["fuel_type_code"],
                row["gear_number"],
                row["id"],
            ),
        ),
        "same_source_ranges": sorted(
            same_source_ranges,
            key=lambda row: (
                row["attribute_code"],
                row["configuration_code"],
                row["fuel_type_code"],
                row["id"],
            ),
        ),
        "latest_values_by_attribute": {
            attribute: sorted(
                rows,
                key=lambda row: (
                    row["configuration_code"],
                    row["fuel_type_code"],
                    row["gear_number"],
                ),
            )
            for attribute, rows in sorted(by_attribute.items())
        },
        "latest_ranges_by_attribute": {
            attribute: sorted(
                rows,
                key=lambda row: (row["configuration_code"], row["fuel_type_code"]),
            )
            for attribute, rows in sorted(range_by_attribute.items())
        },
        "review_summaries": {
            "ambiguity": reviews["ambiguity"]["summary"],
            "unresolved_chunk_1": reviews["unresolved_chunk_1"]["summary"],
            "unresolved_chunk_2": reviews["unresolved_chunk_2"]["summary"],
        },
        "ambiguity_source_facts": [
            {
                "candidate_id": decision["candidate_id"],
                "exact_text": decision["exact_text"],
                "source_facts": decision.get("source_facts", []),
                "selected_evidence_signatures": decision.get("selected_evidence_signatures", []),
            }
            for decision in reviews["ambiguity"]["decisions"]
        ],
        "unresolved_key_source_boundaries": reviews["unresolved_chunk_1"]["key_source_boundaries"],
        "unresolved_final_context": reviews["unresolved_chunk_2"]["key_source_boundaries"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
