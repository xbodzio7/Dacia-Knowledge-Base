from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/reporting/spring_exact_current_semantic_migration_review.json"
TOOL = ROOT / "tools/review_spring_exact_current_semantic_migration_20260802.py"
STATE = ROOT / "project/state.json"
MAPPINGS = ROOT / "data/master/commercial_item_configurations.csv"
ITEMS = ROOT / "data/master/commercial_items.csv"

KHaki_MAPPING = "spring_colour_lichen_khaki__spring_essential_electric70_automatic"
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
    spec = importlib.util.spec_from_file_location("spring_semantic_review", TOOL)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load Spring semantic review tool")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_contract() -> None:
    report = read_json(REPORT)
    tool = load_tool()
    if report != tool.build(ROOT):
        raise AssertionError("Spring semantic migration review is not deterministic")
    tool.verify(ROOT)

    if report["scope"] != {
        "spring_configuration_count": 3,
        "existing_spring_mapping_count": 25,
        "master_data_mutation_authorized": False,
        "source_reports": [
            "data/reporting/spring_commercial_context_resolution.json",
            "data/reporting/spring_current_grade_snapshot_capture.json",
        ],
    }:
        raise AssertionError("unexpected Spring semantic review scope")

    if report["classification_summary"] != {
        "safe_in_place_update": 1,
        "verified_current_no_change": 2,
        "semantic_migration_required": 3,
        "unresolved_no_change": 19,
        "new_representation_required": 2,
    }:
        raise AssertionError("unexpected Spring semantic classification")

    safe = report["safe_in_place_updates"]
    if len(safe) != 1 or safe[0]["mapping_code"] != KHaki_MAPPING:
        raise AssertionError("safe Spring migration boundary drifted")
    if safe[0]["approved_state"] != {
        "availability_status": "optional",
        "amount_pln": 2300,
        "price_date": "2026-08-02",
        "source_code": "src_pl_spring_commercial_context_20260802",
    }:
        raise AssertionError("Essential Khaki approved state drifted")

    semantic_codes = {
        row["mapping_code"] for row in report["semantic_migrations"]
    }
    if semantic_codes != {
        "spring_type2_charging_cable_option__spring_essential_electric70_automatic",
        "spring_type2_charging_cable_option__spring_extreme_electric100_automatic",
        "spring_colour_biel_alpejska__spring_essential_electric70_automatic",
    }:
        raise AssertionError("semantic migration set drifted")

    representation_configs = {
        row["configuration_code"] for row in report["new_representation_required"]
    }
    if representation_configs != {
        "spring_essential_electric70_automatic",
        "spring_extreme_electric100_automatic",
    }:
        raise AssertionError("home-cable representation boundary drifted")

    if report["mutation_summary"] != {
        "master_rows_changed": 0,
        "prices_imported": 0,
        "availability_states_changed": 0,
        "items_added": 0,
        "attributes_added": 0,
    }:
        raise AssertionError("review-only package mutated master scope")

    mapping_index = {row["code"]: row for row in read_rows(MAPPINGS)}
    khaki = mapping_index[KHaki_MAPPING]

    type2_rows = [
        row for row in mapping_index.values()
        if row["commercial_item_code"] == TYPE2_ITEM
    ]
    if len(type2_rows) != 3 or any(
        row["availability_status"] != "optional" for row in type2_rows
    ):
        raise AssertionError("later packages must preserve Type 2 review semantics")

    item_codes = {row["code"] for row in read_rows(ITEMS)}
    if HOME_CABLE_ITEM in item_codes:
        raise AssertionError("later packages must not bypass the home-cable model review")

    state = read_json(STATE)
    current_id = state["current_package"]["package_id"]
    if state["current_package"]["status"] != "complete":
        raise AssertionError("canonical current package must remain complete")

    if current_id == "spring_exact_current_semantic_migration_review_001":
        if khaki["availability_status"] != "optional" or khaki["amount"]:
            raise AssertionError("review package must not apply the Khaki price")
        if state["next_package"]["package_id"] != "spring_essential_khaki_price_apply_001":
            raise AssertionError("unexpected review follow-up package")
        if state["reference_delivery"]["pull_request"] != 451:
            raise AssertionError("semantic review must reference Spring snapshot PR 451")
        if state["baseline"]["rows"] != 11713:
            raise AssertionError("review-only package must preserve master row count")
    else:
        transitions = {
            "spring_essential_khaki_price_apply_001": (
                "spring_standard_equipment_representation_review_001",
                452,
                11714,
            ),
            "spring_standard_equipment_representation_review_001": (
                "spring_biel_alpejska_default_colour_migration_001",
                453,
                11714,
            ),
            "spring_biel_alpejska_default_colour_migration_001": (
                "spring_supplied_charging_cable_model_decision_001",
                454,
                11715,
            ),
        }
        if current_id not in transitions:
            raise AssertionError("unexpected package after Spring semantic review")
        if (
            khaki["availability_status"] != "optional"
            or khaki["amount"] != "2300"
            or khaki["price_date"] != "2026-08-02"
            or khaki["source_code"] != "src_pl_spring_commercial_context_20260802"
        ):
            raise AssertionError("approved Essential Khaki update was not preserved")
        expected_next, expected_pr, expected_rows = transitions[current_id]
        if state["next_package"]["package_id"] != expected_next:
            raise AssertionError("unexpected Spring semantic-review successor")
        if state["reference_delivery"]["pull_request"] != expected_pr:
            raise AssertionError("Spring semantic-review history references an unexpected delivery")
        if state["baseline"]["rows"] != expected_rows:
            raise AssertionError("later Spring package has an unexpected master row count")

    if state["baseline"]["tests"] != 1788:
        raise AssertionError("import-time contracts must preserve test baseline")


# The completed review remains protected while canonical state advances through
# its approved price, representation and default-colour packages.
verify_contract()
