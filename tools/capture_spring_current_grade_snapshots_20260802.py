#!/usr/bin/env python3
"""Build and verify bounded current Spring grade snapshots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "project/sources/dacia-pl-spring-current-grade-snapshots-20260802.json"
REPORT_JSON_PATH = ROOT / "data/reporting/spring_current_grade_snapshot_capture.json"
REPORT_MD_PATH = ROOT / "data/reporting/spring_current_grade_snapshot_capture.md"


def read_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return payload


def build_report(source: Mapping[str, Any]) -> dict[str, Any]:
    snapshots = source["grade_snapshots"]
    by_grade = {item["grade"]: item for item in snapshots}
    expression = by_grade["expression"]
    extreme = by_grade["extreme"]
    summary = source["capture_summary"]
    return {
        "version": 1,
        "generated_on": source["observed_on"],
        "status": "complete",
        "source_code": source["source_code"],
        "scope": {
            "market": source["market"],
            "model_code": source["model_code"],
            "grades": ["expression", "extreme"],
            "master_data_mutation_authorized": False,
        },
        "capture_summary": summary,
        "expression": {
            "configuration_code": expression["configuration_code"],
            "snapshot_status": expression["snapshot_status"],
            "powertrain": expression["powertrain"],
            "equipment_item_count": expression["confirmed"]["equipment_item_count"],
            "standard_highlights": expression["confirmed"]["standard_highlights"],
            "optional_items": expression["confirmed"]["optional_items"],
            "unresolved_fields": expression["not_captured"],
            "master_migration_authorized": expression["master_migration_authorized"],
        },
        "extreme": {
            "configuration_code": extreme["configuration_code"],
            "snapshot_status": extreme["snapshot_status"],
            "powertrain": extreme["powertrain"],
            "catalog_price_pln": extreme["confirmed"]["catalog_price_pln"],
            "equipment_item_count": extreme["confirmed"]["equipment_item_count"],
            "technical": extreme["confirmed"]["technical"],
            "standard_highlights": extreme["confirmed"]["standard_highlights"],
            "charging_equipment": extreme["confirmed"]["charging_equipment"],
            "optional_packages": extreme["confirmed"]["optional_packages"],
            "unresolved_fields": extreme["not_captured"],
            "master_migration_authorized": extreme["master_migration_authorized"],
        },
        "evidence_boundaries": [
            "The current Expression grade page confirms 46 equipment items but exposes neither a complete paint palette nor battery-and-charging semantics.",
            "The default Essential configurator state is not reassigned to Expression.",
            "The current Extreme comparison state confirms price, technical data, Type 2 standard equipment and current charging/package prices, but not a complete paint palette.",
            "No MY2025 stock-only value is promoted to a current grade snapshot.",
            "No dealer-stock card is generalized into a complete grade palette or reusable standalone price."
        ],
        "mutation_summary": {
            "master_rows_changed": 0,
            "prices_imported": 0,
            "availability_states_changed": 0,
            "models_or_domains_added": 0,
        },
        "next_package": source["next_package"],
    }


def render_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"


def render_markdown(report: Mapping[str, Any]) -> str:
    expression = report["expression"]
    extreme = report["extreme"]
    boundaries = "\n".join(f"- {item}" for item in report["evidence_boundaries"])
    expression_missing = "\n".join(
        f"- `{name}`: {details['state']}"
        for name, details in expression["unresolved_fields"].items()
    )
    extreme_missing = "\n".join(
        f"- `{name}`: {details['state']}"
        for name, details in extreme["unresolved_fields"].items()
    )
    return f"""# Spring Current Grade Snapshot Capture

**Status:** complete  
**Date:** {report['generated_on']}  
**Master-data mutations:** 0

## Expression electric 70

Snapshot status: `{expression['snapshot_status']}`.

The exact current Expression page confirms **{expression['equipment_item_count']}** equipment items, including Media Control, manual air conditioning, rear parking assistance and the lane-keeping system. The optional TECHNO package contains Media Display, USB-C and the reversing camera, but the exact grade page does not state its price.

Unresolved current-grade fields:

{expression_missing}

These gaps are not filled from the default Essential configurator or the MY2025 stock-only price list.

## Extreme electric 100

Snapshot status: `{extreme['snapshot_status']}`.

Confirmed current state:

- catalogue price: **{extreme['catalog_price_pln']} PLN**,
- power: **{extreme['technical']['power_kw']} kW ({extreme['technical']['power_hp']} KM)**,
- battery: **{extreme['technical']['battery_capacity_kwh']} kWh**,
- WLTP range: **{extreme['technical']['wltp_range_km']} km**,
- Type 2 cable: **standard**,
- home charging cable: **optional, 1500 PLN**,
- CITY package: **1800 PLN**,
- POWER package: **3000 PLN**.

Unresolved current-grade fields:

{extreme_missing}

## Evidence boundaries

{boundaries}

## Mutation boundary

- master rows changed: **0**,
- prices imported: **0**,
- availability states changed: **0**,
- models or domains added: **0**.

## Next package

`{report['next_package']['package_id']}` will compare these exact current snapshots with existing availability and commercial mappings and identify only safely migratable states.
"""


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def apply(root: Path = ROOT) -> None:
    source = read_object(root / SOURCE_PATH.relative_to(ROOT))
    report = build_report(source)
    write_atomic(root / REPORT_JSON_PATH.relative_to(ROOT), render_json(report))
    write_atomic(root / REPORT_MD_PATH.relative_to(ROOT), render_markdown(report))


def verify(root: Path = ROOT) -> None:
    source = read_object(root / SOURCE_PATH.relative_to(ROOT))
    expected = build_report(source)
    actual = read_object(root / REPORT_JSON_PATH.relative_to(ROOT))
    if actual != expected:
        raise RuntimeError("Spring current grade snapshot JSON report is stale")
    if (root / REPORT_MD_PATH.relative_to(ROOT)).read_text(encoding="utf-8") != render_markdown(expected):
        raise RuntimeError("Spring current grade snapshot Markdown report is stale")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    if arguments.apply:
        apply()
    else:
        verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
