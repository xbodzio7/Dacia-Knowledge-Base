#!/usr/bin/env python3
"""Build and verify the bounded Spring semantic-migration review."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
CONTEXT_PATH = ROOT / "data/reporting/spring_commercial_context_resolution.json"
SNAPSHOT_PATH = ROOT / "data/reporting/spring_current_grade_snapshot_capture.json"
ITEMS_PATH = ROOT / "data/master/commercial_items.csv"
MEMBERSHIPS_PATH = ROOT / "data/master/commercial_item_attributes.csv"
MAPPINGS_PATH = ROOT / "data/master/commercial_item_configurations.csv"
REPORT_JSON_PATH = ROOT / "data/reporting/spring_exact_current_semantic_migration_review.json"
REPORT_MD_PATH = ROOT / "data/reporting/spring_exact_current_semantic_migration_review.md"

SPRING_CONFIGURATIONS = {
    "spring_essential_electric70_automatic",
    "spring_expression_electric70_automatic",
    "spring_extreme_electric100_automatic",
}
TYPE2_ITEM = "spring_type2_charging_cable_option"
HOME_CABLE_ITEM = "spring_domestic_socket_charging_cable_option"
KHaki_MAPPING = "spring_colour_lichen_khaki__spring_essential_electric70_automatic"
WHITE_MAPPING = "spring_colour_biel_alpejska__spring_essential_electric70_automatic"
CITY_MAPPING = "spring_city_package__spring_extreme_electric100_automatic"
POWER_MAPPING = "spring_power_package__spring_extreme_electric100_automatic"


def read_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return payload


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def selected_mappings(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {
        row["code"]: row
        for row in rows
        if row.get("configuration_code") in SPRING_CONFIGURATIONS
        and row.get("commercial_item_code", "").startswith("spring_")
    }


def build_report(
    context: Mapping[str, Any],
    snapshot: Mapping[str, Any],
    items: list[dict[str, str]],
    memberships: list[dict[str, str]],
    mappings: list[dict[str, str]],
) -> dict[str, Any]:
    selected = selected_mappings(mappings)
    item_index = {row["code"]: row for row in items}
    migration_complete = HOME_CABLE_ITEM in item_index
    membership_index = {
        row["commercial_item_code"]: row
        for row in memberships
        if row["commercial_item_code"] == TYPE2_ITEM
    }

    if len(selected) not in {25, 27}:
        raise RuntimeError(f"expected 25 pre-migration or 27 post-migration Spring commercial mappings, found {len(selected)}")
    khaki = selected[KHaki_MAPPING]
    white = selected[WHITE_MAPPING]
    city = selected[CITY_MAPPING]
    power = selected[POWER_MAPPING]
    type2 = [
        row for row in selected.values()
        if row["commercial_item_code"] == TYPE2_ITEM
    ]
    if len(type2) != 3:
        raise RuntimeError("expected three Type 2 commercial mappings")

    exact_paints = {
        row["commercial_item_code"]: row
        for row in context["paint_resolution"]["exact_current_my26_rows"]
        if row["configuration_code"] == "spring_essential_electric70_automatic"
    }
    if exact_paints["spring_colour_lichen_khaki"]["price_pln"] != 2300:
        raise RuntimeError("exact current Essential Khaki price drifted")
    if exact_paints["spring_colour_biel_alpejska"]["availability_status"] != "standard":
        raise RuntimeError("exact current Essential white state drifted")
    khaki_before_apply = (
        khaki["availability_status"] == "optional"
        and not khaki["amount"]
        and not khaki["price_date"]
        and khaki["source_code"] == "src_pl_spring_brochure_20260219"
    )
    khaki_after_apply = (
        khaki["availability_status"] == "optional"
        and khaki["amount"] == "2300"
        and khaki["currency_code"] == "PLN"
        and khaki["price_date"] == "2026-08-02"
        and khaki["source_code"] == "src_pl_spring_commercial_context_20260802"
    )
    if not (khaki_before_apply or khaki_after_apply):
        raise RuntimeError("Essential Khaki mapping is outside the reviewed transition")
    if white["availability_status"] != "optional" or white["amount"]:
        raise RuntimeError("Essential white mapping is not the expected blank option")
    if (city["amount"], power["amount"]) != ("1800", "3000"):
        raise RuntimeError("reviewed Extreme package prices drifted")
    if item_index[TYPE2_ITEM]["item_type"] != "option":
        raise RuntimeError("Type 2 item no longer has option semantics")
    expected_type2_attribute = "type2_charging_cable_supplied" if migration_complete else "charging_connector_type"
    if membership_index[TYPE2_ITEM]["attribute_code"] != expected_type2_attribute:
        raise RuntimeError("Type 2 membership transition drifted")
    home_rows = [row for row in selected.values() if row["commercial_item_code"] == HOME_CABLE_ITEM]
    if migration_complete:
        if len(home_rows) != 2 or any(row["amount"] != "1500" for row in home_rows):
            raise RuntimeError("domestic charging-cable mappings drifted")
    elif home_rows:
        raise RuntimeError("home charging cable mappings unexpectedly exist")

    expression_unresolved = set(snapshot["expression"]["unresolved_fields"])
    if expression_unresolved != {
        "catalog_price",
        "paint_palette",
        "type2_charging_cable",
        "home_charging_cable",
        "dc40_option_price",
    }:
        raise RuntimeError("Expression unresolved boundary drifted")

    return {
        "version": 1,
        "generated_on": "2026-08-02",
        "status": "complete",
        "scope": {
            "spring_configuration_count": 3,
            "existing_spring_mapping_count": len(selected),
            "master_data_mutation_authorized": False,
            "source_reports": [
                "data/reporting/spring_commercial_context_resolution.json",
                "data/reporting/spring_current_grade_snapshot_capture.json",
            ],
        },
        "classification_summary": {
            "safe_in_place_update": 1,
            "verified_current_no_change": 2,
            "semantic_migration_required": 3,
            "unresolved_no_change": 19,
            "new_representation_required": 2,
        },
        "safe_in_place_updates": [
            {
                "mapping_code": KHaki_MAPPING,
                "commercial_item_code": "spring_colour_lichen_khaki",
                "configuration_code": "spring_essential_electric70_automatic",
                "current_state": {
                    "availability_status": "optional",
                    "amount": None,
                    "source_code": "src_pl_spring_brochure_20260219",
                },
                "approved_state": {
                    "availability_status": "optional",
                    "amount_pln": 2300,
                    "price_date": "2026-08-02",
                    "source_code": "src_pl_spring_commercial_context_20260802",
                },
                "reason": "The existing option semantics and exact current Essential configuration match; only the missing price and provenance require updating.",
            }
        ],
        "verified_current_no_change": [
            {
                "mapping_code": CITY_MAPPING,
                "amount_pln": 1800,
                "price_date": city["price_date"],
            },
            {
                "mapping_code": POWER_MAPPING,
                "amount_pln": 3000,
                "price_date": power["price_date"],
            },
        ],
        "semantic_migrations": [
            {
                "mapping_code": "spring_type2_charging_cable_option__spring_essential_electric70_automatic",
                "exact_current_state": "standard_equipment",
                "current_model_state": "commercial_option",
                "required_action": "create or confirm a direct standard-equipment representation before retiring the option mapping",
            },
            {
                "mapping_code": "spring_type2_charging_cable_option__spring_extreme_electric100_automatic",
                "exact_current_state": "standard_equipment",
                "current_model_state": "commercial_option",
                "required_action": "create or confirm a direct standard-equipment representation before retiring the option mapping",
            },
            {
                "mapping_code": WHITE_MAPPING,
                "exact_current_state": "standard_paint_at_zero_surcharge",
                "current_model_state": "commercial_option_with_unknown_price",
                "required_action": "model the grade default or standard paint explicitly before retiring or converting the option mapping",
            },
        ],
        "new_representation_required": [
            {
                "configuration_code": "spring_essential_electric70_automatic",
                "source_item": "kabel do ładowania z gniazda domowego",
                "exact_current_state": "optional_1500_pln",
                "blocking_reason": "No compatible commercial item and no dedicated charging-cable attribute exist; charging_connector_type describes the vehicle connector standard, not the supplied cable.",
            },
            {
                "configuration_code": "spring_extreme_electric100_automatic",
                "source_item": "kabel do ładowania z gniazda domowego",
                "exact_current_state": "optional_1500_pln",
                "blocking_reason": "No compatible commercial item and no dedicated charging-cable attribute exist; charging_connector_type describes the vehicle connector standard, not the supplied cable.",
            },
        ],
        "unresolved_no_change": {
            "mapping_count": 19,
            "groups": [
                {
                    "name": "Expression current commercial state",
                    "mapping_count": 9,
                    "reason": "The current exact Expression pages do not expose a price, Type 2 state, charging-option prices or a complete paint palette.",
                },
                {
                    "name": "Extreme paint palette",
                    "mapping_count": 6,
                    "reason": "No complete exact current Extreme paint palette with prices was captured.",
                },
                {
                    "name": "Essential residual paint palette",
                    "mapping_count": 4,
                    "reason": "Only Biel Alpejska and Lichen Khaki have exact current Essential states; absence of four legacy colours is not converted into unavailability.",
                },
            ],
        },
        "mutation_summary": {
            "master_rows_changed": 0,
            "prices_imported": 0,
            "availability_states_changed": 0,
            "items_added": 0,
            "attributes_added": 0,
        },
        "next_package": {
            "package_id": "spring_essential_khaki_price_apply_001",
            "goal": "Apply only the exact current 2300 PLN Essential Lichen Khaki price to the existing optional mapping, register bounded provenance if required, and leave all semantic or unresolved cases untouched.",
        },
    }


def render_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = report["classification_summary"]
    safe = report["safe_in_place_updates"][0]
    return f"""# Spring Exact Current Semantic Migration Review

**Status:** complete  
**Date:** {report['generated_on']}  
**Master-data mutations:** 0

## Classification

| Class | Count |
|---|---:|
| Safe in-place update | {summary['safe_in_place_update']} |
| Verified current — no change | {summary['verified_current_no_change']} |
| Semantic migration required | {summary['semantic_migration_required']} |
| Unresolved — no change | {summary['unresolved_no_change']} |
| New representation required | {summary['new_representation_required']} |

## Safe in-place update

`{safe['mapping_code']}` can be updated from an optional item with an unknown amount to an exact current **2300 PLN** optional paint price. The item, configuration and option semantics already match the current Essential configurator state.

## Verified current records

- Extreme CITY: **1800 PLN** — already correct.
- Extreme POWER: **3000 PLN** — already correct.

## Semantic migrations — not a price import

- Type 2 cable for Essential: exact current standard equipment, but modeled as a commercial option.
- Type 2 cable for Extreme: exact current standard equipment, but modeled as a commercial option.
- Biel Alpejska for Essential: exact current standard paint at zero surcharge, but modeled as an optional commercial item with an unknown price.

These records require an explicit standard/default representation before the stale option mapping can be retired or converted.

## New representation required

The home charging cable is an exact current **1500 PLN option** for Essential and Extreme, but the repository has neither a compatible commercial item nor a dedicated cable attribute. `charging_connector_type` describes the vehicle connector standard and must not be reused for a supplied cable.

## Unresolved mappings

Nineteen mappings remain unchanged:

- 9 Expression mappings: current price, charging states and full palette are not exposed by exact current grade pages;
- 6 Extreme paint mappings: no complete current priced palette was captured;
- 4 residual Essential paint mappings: absence from the captured palette is not treated as proof of unavailability.

## Next package

`{report['next_package']['package_id']}` will apply only the exact current Essential Lichen Khaki price and leave every semantic or unresolved case untouched.
"""


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def build(root: Path = ROOT) -> dict[str, Any]:
    return build_report(
        read_object(root / CONTEXT_PATH.relative_to(ROOT)),
        read_object(root / SNAPSHOT_PATH.relative_to(ROOT)),
        read_rows(root / ITEMS_PATH.relative_to(ROOT)),
        read_rows(root / MEMBERSHIPS_PATH.relative_to(ROOT)),
        read_rows(root / MAPPINGS_PATH.relative_to(ROOT)),
    )


def apply(root: Path = ROOT) -> None:
    report = build(root)
    write_atomic(root / REPORT_JSON_PATH.relative_to(ROOT), render_json(report))
    write_atomic(root / REPORT_MD_PATH.relative_to(ROOT), render_markdown(report))


def verify(root: Path = ROOT) -> None:
    expected = build(root)
    actual = read_object(root / REPORT_JSON_PATH.relative_to(ROOT))
    if actual != expected:
        raise RuntimeError("Spring semantic migration review JSON is stale")
    if (root / REPORT_MD_PATH.relative_to(ROOT)).read_text(encoding="utf-8") != render_markdown(expected):
        raise RuntimeError("Spring semantic migration review Markdown is stale")


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
