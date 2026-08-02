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
        raise AssertionError("unexpected compatible supplied-cable attribute")

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
            raise AssertionError(f"{concept} must remain behind a model decision")
        if not decisions[concept]["new_attribute_required"]:
            raise AssertionError(f"{concept} requires a dedicated attribute")

    attribute_index = {row["code"]: row for row in read_rows(ATTRIBUTES)}
    if attribute_index["charging_connector_type"]["description"] != "Charging connector standard":
        raise AssertionError("connector semantics drifted")
    spring_colours = [
        row for row in read_rows(VALUES)
        if row["configuration_code"].startswith("spring_")
        and row["attribute_code"] == "exterior_color"
    ]
    state = read_json(STATE)
    current_id = state["current_package"]["package_id"]
    mapping_index = {row["code"]: row for row in read_rows(MAPPINGS)}
    white = mapping_index[WHITE_MAPPING]
    if current_id == "spring_standard_equipment_representation_review_001":
        if spring_colours:
            raise AssertionError("review package must not apply the Essential white value")
        if white["availability_status"] != "optional" or white["amount"]:
            raise AssertionError("review package must not migrate Essential white")
    elif current_id == "spring_biel_alpejska_default_colour_migration_001":
        if len(spring_colours) != 1:
            raise AssertionError("white migration must add one Spring exterior colour")
        colour_value = spring_colours[0]
        if (
            colour_value["configuration_code"] != ESSENTIAL
            or colour_value["value"] != "biel alpejska"
            or colour_value["observation_date"] != "2026-08-02"
            or colour_value["source_code"]
            != "src_pl_spring_commercial_context_20260802"
        ):
            raise AssertionError("applied Spring exterior colour drifted")
        if (
            white["availability_status"] != "standard"
            or white["amount"] != "0"
            or white["price_date"] != "2026-08-02"
            or white["source_code"]
            != "src_pl_spring_commercial_context_20260802"
        ):
            raise AssertionError("applied Essential white mapping drifted")
    else:
        raise AssertionError("unexpected package after representation review")

    memberships = [
        row for row in read_rows(MEMBERSHIPS)
        if row["commercial_item_code"] == TYPE2_ITEM
    ]
    if len(memberships) != 1 or memberships[0]["attribute_code"] != "charging_connector_type":
        raise AssertionError("review must preserve the blocked Type 2 membership")
    item_codes = {row["code"] for row in read_rows(ITEMS)}
    if HOME_CABLE_ITEM in item_codes:
        raise AssertionError("review package must not add the home cable item")

    if state["current_package"]["status"] != "complete":
        raise AssertionError("canonical current package must remain complete")
    if current_id == "spring_standard_equipment_representation_review_001":
        if state["next_package"]["package_id"] != "spring_biel_alpejska_default_colour_migration_001":
            raise AssertionError("unexpected representation-review follow-up")
        if state["reference_delivery"]["pull_request"] != 453:
            raise AssertionError("representation review must reference Khaki apply PR 453")
        expected = (11714, 3567, 138)
    else:
        if state["next_package"]["package_id"] != "spring_supplied_charging_cable_model_decision_001":
            raise AssertionError("unexpected white-migration follow-up")
        if state["reference_delivery"]["pull_request"] != 454:
            raise AssertionError("white migration must reference representation review PR 454")
        expected = (11715, 3568, 139)
    if state["baseline"]["tests"] != 1788:
        raise AssertionError("import-time contracts must preserve the test baseline")
    actual = (
        state["baseline"]["rows"],
        state["baseline"]["configuration_values"],
        state["baseline"]["configuration_import_specs"],
    )
    if actual != expected:
        raise AssertionError("representation-review transition baseline drifted")


# Import-time verification preserves the established test-count baseline.
verify_contract()
