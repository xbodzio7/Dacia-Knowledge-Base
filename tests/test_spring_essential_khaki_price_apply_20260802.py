from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/reporting/spring_essential_khaki_price_apply.json"
REVIEW = ROOT / "data/reporting/spring_exact_current_semantic_migration_review.json"
SOURCE_SNAPSHOT = ROOT / "project/sources/dacia-pl-spring-commercial-context-20260802.json"
SOURCES = ROOT / "data/master/sources.csv"
MAPPINGS = ROOT / "data/master/commercial_item_configurations.csv"
TOOL = ROOT / "tools/apply_spring_essential_khaki_price_20260802.py"
STATE = ROOT / "project/state.json"

SOURCE_CODE = "src_pl_spring_commercial_context_20260802"
TARGET = "spring_colour_lichen_khaki__spring_essential_electric70_automatic"
EXPRESSION = "spring_colour_lichen_khaki__spring_expression_electric70_automatic"
EXTREME = "spring_colour_lichen_khaki__spring_extreme_electric100_automatic"


def read_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"expected object: {path}")
    return payload


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_tool():
    spec = importlib.util.spec_from_file_location("spring_khaki_apply", TOOL)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load Spring Khaki apply tool")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_contract() -> None:
    report = read_json(REPORT)
    review = read_json(REVIEW)
    tool = load_tool()
    tool.verify(ROOT)

    if report["scope"] != {
        "mapping_code": TARGET,
        "configuration_code": "spring_essential_electric70_automatic",
        "commercial_item_code": "spring_colour_lichen_khaki",
        "source_code": SOURCE_CODE,
    }:
        raise AssertionError("unexpected Spring Khaki apply scope")

    source_sha256 = hashlib.sha256(SOURCE_SNAPSHOT.read_bytes()).hexdigest()
    if report["source_registration"] != {
        "rows_added": 1,
        "registered_source_count": 1,
        "source_sha256": source_sha256,
        "file_path": "project/sources/dacia-pl-spring-commercial-context-20260802.json",
    }:
        raise AssertionError("Spring context source registration drifted")

    if report["mapping_update"] != {
        "rows_changed": 1,
        "before": {
            "availability_status": "optional",
            "amount": None,
            "currency_code": "PLN",
            "price_date": None,
            "source_code": "src_pl_spring_brochure_20260219",
        },
        "after": {
            "availability_status": "optional",
            "amount": 2300,
            "currency_code": "PLN",
            "price_date": "2026-08-02",
            "source_code": SOURCE_CODE,
        },
    }:
        raise AssertionError("Spring Essential Khaki price update drifted")

    if report["preserved_boundaries"] != {
        "semantic_migrations_unchanged": 3,
        "unresolved_mappings_unchanged": 19,
        "new_representation_cases_unchanged": 2,
        "other_mapping_rows_changed": 0,
    }:
        raise AssertionError("Spring apply boundary drifted")
    if report["master_data_delta"] != {
        "source_rows_added": 1,
        "commercial_mapping_rows_added": 0,
        "commercial_mapping_rows_updated": 1,
        "commercial_items_added": 0,
        "attributes_added": 0,
    }:
        raise AssertionError("unexpected Spring apply master-data delta")

    if review["classification_summary"] != {
        "safe_in_place_update": 1,
        "verified_current_no_change": 2,
        "semantic_migration_required": 3,
        "unresolved_no_change": 19,
        "new_representation_required": 2,
    }:
        raise AssertionError("approved review boundary drifted")

    source_index = {row["code"]: row for row in read_rows(SOURCES)}
    source = source_index[SOURCE_CODE]
    if source["id"] != "34":
        raise AssertionError("unexpected Spring context source id")
    if source["source_type"] != "normalized_snapshot":
        raise AssertionError("unexpected Spring context source type")
    if source["file_path"] != "project/sources/dacia-pl-spring-commercial-context-20260802.json":
        raise AssertionError("unexpected Spring context source path")
    if source["sha256"] != source_sha256 or source["status"] != "active":
        raise AssertionError("Spring context source integrity drifted")

    mapping_index = {row["code"]: row for row in read_rows(MAPPINGS)}
    target = mapping_index[TARGET]
    if (
        target["availability_status"] != "optional"
        or target["amount"] != "2300"
        or target["currency_code"] != "PLN"
        or target["price_date"] != "2026-08-02"
        or target["source_code"] != SOURCE_CODE
    ):
        raise AssertionError("Spring Essential Khaki mapping is not in the approved state")

    for code in (EXPRESSION, EXTREME):
        row = mapping_index[code]
        if row["amount"] or row["price_date"] or row["source_code"] != "src_pl_spring_brochure_20260219":
            raise AssertionError(f"unapproved Khaki mapping changed: {code}")

    state = read_json(STATE)
    current_id = state["current_package"]["package_id"]
    if state["current_package"]["status"] != "complete":
        raise AssertionError("canonical current package must remain complete")
    if current_id == "spring_essential_khaki_price_apply_001":
        if state["next_package"]["package_id"] != "spring_standard_equipment_representation_review_001":
            raise AssertionError("unexpected Khaki apply follow-up")
        if state["reference_delivery"]["pull_request"] != 452:
            raise AssertionError("Khaki apply must reference semantic review PR 452")
    else:
        if current_id != "spring_standard_equipment_representation_review_001":
            raise AssertionError("unexpected package after Spring Khaki apply")
        if state["next_package"]["package_id"] != "spring_biel_alpejska_default_colour_migration_001":
            raise AssertionError("unexpected representation-review follow-up")
        if state["reference_delivery"]["pull_request"] != 453:
            raise AssertionError("representation review must reference Khaki apply PR 453")
    if state["baseline"]["tests"] != 1788:
        raise AssertionError("import-time contract must preserve test baseline")
    if state["baseline"]["rows"] != 11714:
        raise AssertionError("later review package must preserve the Khaki baseline")


# The completed Khaki apply remains protected while canonical state advances
# to the representation review.
verify_contract()
