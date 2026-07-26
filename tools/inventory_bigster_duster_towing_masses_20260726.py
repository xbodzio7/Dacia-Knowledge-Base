#!/usr/bin/env python3
"""Build a temporary inventory for Bigster and Duster brochure towing masses."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORTING = ROOT / "data" / "reporting"
ATTRIBUTES = {"gross_train_weight", "unbraked_trailer_weight"}
SOURCES = {
    "src_pl_bigster_brochure_20251210",
    "src_pl_duster_mini_brochure_20251020",
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
        if row.get("status") == "active"
        and row.get("code", "").startswith(("bigster_", "duster_iii_"))
    }
    values = rows("configuration_attribute_values.csv")
    relationships = rows("source_configurations.csv")
    attributes = {row["code"]: row for row in rows("attributes.csv")}

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
    targets = set(bigster) | set(duster)

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
    print(json.dumps({"bigster": bigster, "duster": duster}, ensure_ascii=False, indent=2))
    print(f"bigster_count={len(bigster)}")
    print(f"duster_count={len(duster)}")

    print("\n=== REPORTING SPECS REFERENCING TARGETS OR ATTRIBUTES ===")
    for path in sorted(REPORTING.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        payload_strings = strings(payload)
        target_refs = sorted(targets & payload_strings)
        attribute_refs = sorted(ATTRIBUTES & payload_strings)
        if target_refs or attribute_refs:
            technical_slots = []
            if isinstance(payload, dict) and isinstance(payload.get("technical_slots"), list):
                technical_slots = [
                    item
                    for item in payload["technical_slots"]
                    if isinstance(item, dict)
                    and item.get("attribute_code") in ATTRIBUTES
                ]
            relevant_decisions = []
            if isinstance(payload, dict) and isinstance(payload.get("decisions"), list):
                relevant_decisions = [
                    item
                    for item in payload["decisions"]
                    if isinstance(item, dict)
                    and item.get("configuration_code") in targets
                    and item.get("attribute_code") in ATTRIBUTES
                ]
            print(json.dumps({
                "path": path.relative_to(ROOT).as_posix(),
                "target_refs": target_refs,
                "attribute_refs": attribute_refs,
                "technical_slots": technical_slots,
                "relevant_decisions": relevant_decisions,
            }, ensure_ascii=False, sort_keys=True))

    print("\n=== TARGET RELATIONSHIP COVERAGE ===")
    relationship_pairs = {
        (row.get("source_code", ""), row.get("configuration_code", ""))
        for row in relationships
    }
    missing = []
    for code in bigster:
        if ("src_pl_bigster_brochure_20251210", code) not in relationship_pairs:
            missing.append(code)
    for code in duster:
        if ("src_pl_duster_mini_brochure_20251020", code) not in relationship_pairs:
            missing.append(code)
    print(json.dumps({"missing": missing, "covered": len(targets) - len(missing)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
