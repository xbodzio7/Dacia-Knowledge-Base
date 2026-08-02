from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/reporting/spring_standard_equipment_representation_review.json"
TOOL = ROOT / "tools/review_spring_standard_equipment_representation_20260802.py"
STATE = ROOT / "project/state.json"
VALUES = ROOT / "data/master/configuration_attribute_values.csv"
ATTRIBUTES = ROOT / "data/master/attributes.csv"
MAPPINGS = ROOT / "data/master/commercial_item_configurations.csv"
MEMBERSHIPS = ROOT / "data/master/commercial_item_attributes.csv"
ITEMS = ROOT / "data/master/commercial_items.csv"

ESSENTIAL = "spring_essential_electric70_automatic"
WHITE_MAPPING = "spring_colour_biel_alpejska__spring_essential_electric70_automatic"
TYPE2_ITEM = "spring_type2_charging_cable_option"
HOME_CABLE_ITEM = "spring_home_charging_cable_option"
HISTORICAL_PACKAGE_ID = "spring_standard_equipment_representation_review_001"


def read_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"expected object: {path}")
    return payload


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_tool():
    spec = importlib.util.spec_from_file_location("spring_representation_review", TOOL)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load Spring representation review tool")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_contract() -> None:
    report = read_json(REPORT)
    state = read_json(STATE)

    # Full reconstruction is meaningful only while this review is the current
    # package. Later accepted migrations are verified by their own contracts
    # and must not rewrite the historical report's observed repository state.
    if state["current_package"]["package_id"] == HISTORICAL_PACKAGE_ID:
        tool = load_tool()
        if report != tool.build(ROOT):
            raise AssertionError("Spring representation review is not deterministic")
        tool.verify(ROOT)

    if report["scope"]["master_data_mutation_authorized"]:
        raise AssertionError("representation review must not authorize master mutation")
    if report["summary"] != {
        "existing_pattern_migrations": 1,
        "new_representation_decisions": 2,
        "master_rows_changed": 0,
        "attributes_added": 0,
        "commercial_items_added": 0,
    }:
        raise AssertionError("unexpected Spring representation summary")

    patterns = report["repository_patterns"]
    if patterns["direct_scalar_default_colour"] != {
        "attribute_code": "exterior_color",
        "data_type": "string",
        "existing_value_rows": 7,
        "spring_value_rows": 0,
        "pattern_status": "available",
        "meaning": "A source-stated default exterior colour is stored as a direct configuration value, independently of commercial palette options.",
    }:
        raise AssertionError("default-colour representation pattern drifted")
    if patterns["boolean_equipment_availability"]["standard_rows"] != 4592:
        raise AssertionError("standard equipment availability count drifted")
    if patterns["commercial_standard_relationship"]["standard_mapping_rows"] != 4:
        raise AssertionError("standard commercial relationship count drifted")
    if patterns["commercial_standard_relationship"]["non_stock_grade_standard_rows"] != 0:
        raise AssertionError("unexpected trim-level standard commercial precedent")
    if patterns["charging_connector_scalar"]["existing_value_rows"] != 0:
        raise AssertionError("unexpected direct connector scalar")
    if patterns["supplied_charging_cable_attribute"]["compatible_attribute_codes"]:
        raise AssertionError("historical review unexpectedly contained a supplied-cable attribute")

    decisions = {row["concept"]: row for row in report["decisions"]}
    colour = decisions["Essential Biel Alpejska default colour"]
    if colour["classification"] != "existing_pattern_available":
        raise AssertionError("Essential white should use the existing colour pattern")
    approved = colour["approved_representation"]
    if approved["direct_value_attribute"] != "exterior_color":
        raise AssertionError("unexpected Essential white direct attribute")
    if approved["commercial_mapping"]["target_availability_status"] != "standard":
        raise AssertionError("Essential white target commercial status drifted")
    if approved["commercial_mapping"]["target_amount_pln"] != 0:
        raise AssertionError("Essential white target price drifted")

    for concept in ("Type 2 supplied charging cable", "Home charging cable"):
        if decisions[concept]["classification"] != "new_representation_decision_required":
            raise AssertionError(f"{concept} must remain behind a model decision in the historical report")
        if not decisions[concept]["new_attribute_required"]:
            raise AssertionError(f"{concept} required a dedicated attribute")

    attribute_index = {row["code"]: row for row in read_rows(ATTRIBUTES)}
    if attribute_index["charging_connector_type"]["description"] != "Charging connector standard":
        raise AssertionError("connector semantics drifted")
    spring_colours = [
        row for row in read_rows(VALUES)
        if row["configuration_code"].startswith("spring_")
        and row["attribute_code"] == "exterior_color"
    ]
    if spring_colours:
        raise AssertionError("review boundary for the deferred Essential white value drifted")

    mapping_index = {row["code"]: row for row in read_rows(MAPPINGS)}
    white = mapping_index[WHITE_MAPPING]
    if white["availability_status"] != "optional" or white["amount"]:
        raise AssertionError("review boundary for Essential white drifted")

    memberships = [
        row for row in read_rows(MEMBERSHIPS)
        if row["commercial_item_code"] == TYPE2_ITEM
    ]
    item_codes = {row["code"] for row in read_rows(ITEMS)}
    migration_complete = "spring_domestic_socket_charging_cable_option" in item_codes
    expected_attribute = "type2_charging_cable_supplied" if migration_complete else "charging_connector_type"
    if len(memberships) != 1 or memberships[0]["attribute_code"] != expected_attribute:
        raise AssertionError("historical Type 2 membership transition drifted")

    if state["current_package"]["status"] != "complete":
        raise AssertionError("canonical current package must remain complete")
    if not state["current_package"]["package_id"] or not state["next_package"]["package_id"]:
        raise AssertionError("canonical package queue is incomplete")
    if state["reference_delivery"]["pull_request"] < 454:
        raise AssertionError("canonical history predates the representation review")
    if state["baseline"]["tests"] < 1788 or state["baseline"]["rows"] < 11714:
        raise AssertionError("canonical baseline regressed behind the representation review")


# Import-time verification protects the completed historical review while
# allowing later bounded packages to implement its accepted decisions.
verify_contract()
