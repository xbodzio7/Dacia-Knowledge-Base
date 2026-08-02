#!/usr/bin/env python3
"""Verify the bounded Spring charging-cable commercial semantics review."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/reporting/spring_charging_cable_commercial_semantics_review.json"
DECISION = ROOT / "project/decisions/spring-charging-cable-commercial-semantics-20260802.md"
ITEMS = ROOT / "data/master/commercial_items.csv"
MEMBERSHIPS = ROOT / "data/master/commercial_item_attributes.csv"
MAPPINGS = ROOT / "data/master/commercial_item_configurations.csv"
STATE = ROOT / "project/state.json"
PACKAGE_ID = "spring_charging_cable_commercial_semantics_review_001"
NEXT_PACKAGE_ID = "spring_charging_cable_commercial_semantics_migration_001"
TYPE2_ITEM = "spring_type2_charging_cable_option"
DOMESTIC_ITEM = "spring_domestic_socket_charging_cable_option"


def read_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"expected JSON object: {path}")
    return payload


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def verify(root: Path = ROOT) -> None:
    report = read_json(root / REPORT.relative_to(ROOT))
    state = read_json(root / STATE.relative_to(ROOT))

    items = {row["code"]: row for row in rows(root / ITEMS.relative_to(ROOT))}
    memberships = rows(root / MEMBERSHIPS.relative_to(ROOT))
    mappings = rows(root / MAPPINGS.relative_to(ROOT))

    historical = items.get(TYPE2_ITEM)
    if historical is None:
        raise AssertionError("historical Type 2 commercial item is missing")
    if historical["id"] != "29" or historical["source_code"] != "src_pl_spring_brochure_20260219":
        raise AssertionError("historical Type 2 commercial item drifted")
    if historical["item_type"] != "option" or historical["status"] != "active":
        raise AssertionError("historical Type 2 item lifecycle drifted")

    type2_memberships = [
        row for row in memberships if row["commercial_item_code"] == TYPE2_ITEM
    ]
    if len(type2_memberships) != 1:
        raise AssertionError("historical Type 2 membership count drifted")
    membership = type2_memberships[0]
    if membership["id"] != "70":
        raise AssertionError("historical Type 2 membership id drifted")
    migration_complete = state["current_package"]["package_id"] == "spring_charging_cable_commercial_semantics_migration_001"
    expected_membership = "type2_charging_cable_supplied" if migration_complete else "charging_connector_type"
    if membership["attribute_code"] != expected_membership:
        raise AssertionError("historical Type 2 membership is outside the accepted transition")
    if "Przewód ładowania ze złączem typu 2" not in membership["source_text"]:
        raise AssertionError("historical Type 2 source wording drifted")

    historical_mappings = [
        row for row in mappings if row["commercial_item_code"] == TYPE2_ITEM
    ]
    if len(historical_mappings) != 3:
        raise AssertionError("historical Type 2 mapping count drifted")
    if {row["configuration_code"] for row in historical_mappings} != {
        "spring_essential_electric70_automatic",
        "spring_expression_electric70_automatic",
        "spring_extreme_electric100_automatic",
    }:
        raise AssertionError("historical Type 2 mapping scope drifted")
    if any(row["availability_status"] != "optional" for row in historical_mappings):
        raise AssertionError("historical Type 2 mapping status drifted")
    if any(row["source_code"] != "src_pl_spring_brochure_20260219" for row in historical_mappings):
        raise AssertionError("historical Type 2 mapping source drifted")

    domestic_memberships = [row for row in memberships if row["commercial_item_code"] == DOMESTIC_ITEM]
    domestic_mappings = [row for row in mappings if row["commercial_item_code"] == DOMESTIC_ITEM]
    if migration_complete:
        if DOMESTIC_ITEM not in items or len(domestic_memberships) != 1 or len(domestic_mappings) != 2:
            raise AssertionError("materialized domestic-cable representation is incomplete")
        if domestic_memberships[0]["attribute_code"] != "domestic_socket_charging_cable":
            raise AssertionError("materialized domestic membership drifted")
        if {row["configuration_code"] for row in domestic_mappings} != {
            "spring_essential_electric70_automatic",
            "spring_extreme_electric100_automatic",
        }:
            raise AssertionError("materialized domestic mapping scope drifted")
    elif DOMESTIC_ITEM in items or domestic_memberships or domestic_mappings:
        raise AssertionError("review package unexpectedly materialized domestic representation")

    if report["historical_type2_item"]["source_meaning"] != "physical_type2_charging_cable":
        raise AssertionError("historical source meaning drifted")
    if report["historical_type2_item"]["accepted_membership_attribute"] != "type2_charging_cable_supplied":
        raise AssertionError("accepted Type 2 target membership drifted")
    current = report["current_domestic_socket_item"]
    if current["accepted_attribute_code"] != "domestic_socket_charging_cable":
        raise AssertionError("accepted domestic-cable attribute drifted")
    if {row["configuration_code"] for row in current["exact_mappings"]} != {
        "spring_essential_electric70_automatic",
        "spring_extreme_electric100_automatic",
    }:
        raise AssertionError("accepted domestic-cable mapping scope drifted")
    if any(row["amount_pln"] != 1500 for row in current["exact_mappings"]):
        raise AssertionError("accepted domestic-cable amount drifted")
    if current["unresolved_configuration_codes"] != [
        "spring_expression_electric70_automatic"
    ]:
        raise AssertionError("Expression unresolved boundary drifted")
    if report["master_data_delta"] != {
        "commercial_items_changed": 0,
        "commercial_memberships_changed": 0,
        "commercial_mappings_changed": 0,
        "net_master_rows_changed": 0,
    }:
        raise AssertionError("review package data boundary drifted")

    decision = (root / DECISION.relative_to(ROOT)).read_text(encoding="utf-8")
    if "spring_charging_cable_commercial_semantics" not in decision:
        raise AssertionError("commercial semantics decision is missing")

    if state["current_package"]["package_id"] == PACKAGE_ID:
        if state["next_package"]["package_id"] != NEXT_PACKAGE_ID:
            raise AssertionError("unexpected commercial semantics follow-up package")
        if state["baseline"]["rows"] != 11723:
            raise AssertionError("review package must not change master-row baseline")


if __name__ == "__main__":
    verify()
    print("Spring charging-cable commercial semantics review: PASS")
