#!/usr/bin/env python3
"""Verify the bounded Spring saved-state artifact intake package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "project/sources/dacia-pl-spring-saved-configurations-20260802.json"
REPORT = ROOT / "data/reporting/spring_saved_state_artifact_intake.json"
SOURCES = ROOT / "data/master/sources.csv"
STATE = ROOT / "project/state.json"
COMMERCIAL_ITEMS = ROOT / "data/master/commercial_items.csv"
COMMERCIAL_MAPPINGS = ROOT / "data/master/commercial_item_configurations.csv"
SOURCE_CODE = "src_pl_spring_saved_configurations_20260802"

EXPECTED_ARTIFACTS = {
    "spring_expression_electric70_automatic": {
        "reference": "7OO7LQ",
        "sha256": "9e4d3493dcb411f9a4c5160707868e89e755708bab0a00aba33dcde96bbb0ec3",
        "price": 81500,
    },
    "spring_extreme_electric100_automatic": {
        "reference": "WKAWYV",
        "sha256": "9e3f11003090227e018254dd0ea2f5dc2f9eb5f80a35859706a2fea06d031f74",
        "price": 85900,
    },
}


def read_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"expected JSON object: {path}")
    return payload


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def verify(root: Path = ROOT) -> None:
    snapshot_path = root / SNAPSHOT.relative_to(ROOT)
    snapshot = read_json(snapshot_path)
    report = read_json(root / REPORT.relative_to(ROOT))
    state = read_json(root / STATE.relative_to(ROOT))

    if snapshot["source_code"] != SOURCE_CODE:
        raise AssertionError("saved-state source code drifted")
    if snapshot["binary_archive"]["status"] != "not_archived_by_connector":
        raise AssertionError("binary archive boundary drifted")

    artifacts = {row["configuration_code"]: row for row in snapshot["artifacts"]}
    if set(artifacts) != set(EXPECTED_ARTIFACTS):
        raise AssertionError("saved-state artifact set drifted")
    for code, expected in EXPECTED_ARTIFACTS.items():
        row = artifacts[code]
        if row["configuration_reference"] != expected["reference"]:
            raise AssertionError(f"configuration reference drifted: {code}")
        if row["pdf_sha256"] != expected["sha256"]:
            raise AssertionError(f"PDF digest drifted: {code}")
        if row["catalog_price_pln"] != expected["price"]:
            raise AssertionError(f"catalogue price drifted: {code}")
        if "type 2 charging cable for wallbox and public terminals" not in row["standard_charging_equipment"]:
            raise AssertionError(f"Type 2 standard evidence missing: {code}")

    matrix = {row["configuration_code"]: row for row in snapshot["charging_cable_evidence_matrix"]}
    if matrix["spring_expression_electric70_automatic"]["type2_cable"] != "standard":
        raise AssertionError("Expression Type 2 state drifted")
    if matrix["spring_expression_electric70_automatic"]["domestic_socket_cable"] != "unresolved":
        raise AssertionError("Expression domestic-cable boundary drifted")
    if snapshot["architecture_decision"]["status"] != "accepted":
        raise AssertionError("charging-cable architecture was not accepted")
    planned = {
        row["planned_attribute_code"]
        for row in snapshot["architecture_decision"]["canonical_concepts"]
    }
    if planned != {"type2_charging_cable_supplied", "domestic_socket_charging_cable"}:
        raise AssertionError("planned cable attributes drifted")
    if snapshot["architecture_decision"]["master_data_mutation_authorized_in_this_package"] is not False:
        raise AssertionError("intake package must remain source-and-decision only")

    actual_snapshot_sha = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
    source_rows = [row for row in read_csv(root / SOURCES.relative_to(ROOT)) if row["code"] == SOURCE_CODE]
    if len(source_rows) != 1:
        raise AssertionError("saved-state normalized source must be registered exactly once")
    source_row = source_rows[0]
    if source_row["id"] != "36" or source_row["sha256"] != actual_snapshot_sha:
        raise AssertionError("saved-state source registration drifted")
    if source_row["file_path"] != "project/sources/dacia-pl-spring-saved-configurations-20260802.json":
        raise AssertionError("saved-state source path drifted")
    if source_row["status"] != "active":
        raise AssertionError("saved-state source must remain active")
    if report["source_registration"]["snapshot_sha256"] != actual_snapshot_sha:
        raise AssertionError("saved-state report hash drifted")

    expected_delta = {
        "source_rows_added": 1,
        "other_master_rows_added": 0,
        "configuration_values_changed": 0,
        "availability_rows_changed": 0,
        "commercial_records_changed": 0,
        "attributes_added": 0,
        "net_master_row_increase": 1,
    }
    if report["master_data_delta"] != expected_delta:
        raise AssertionError("saved-state data boundary drifted")

    # Historical brochure-backed item and mappings remain untouched.
    items = [row for row in read_csv(root / COMMERCIAL_ITEMS.relative_to(ROOT)) if row["code"] == "spring_type2_charging_cable_option"]
    if len(items) != 1 or items[0]["id"] != "29" or items[0]["status"] != "active":
        raise AssertionError("historical Spring cable commercial item drifted")
    mappings = [
        row for row in read_csv(root / COMMERCIAL_MAPPINGS.relative_to(ROOT))
        if row["commercial_item_code"] == "spring_type2_charging_cable_option"
    ]
    expected_mapping_codes = {
        "spring_essential_electric70_automatic",
        "spring_expression_electric70_automatic",
        "spring_extreme_electric100_automatic",
    }
    if {row["configuration_code"] for row in mappings} != expected_mapping_codes:
        raise AssertionError("historical Spring cable mappings drifted")
    if any(row["availability_status"] != "optional" for row in mappings):
        raise AssertionError("historical Spring cable mapping status was rewritten")

    baseline = state["baseline"]
    if baseline["rows"] != 11716 or baseline["configuration_values"] != 3567:
        raise AssertionError("canonical baseline counts drifted")
    if baseline["availability_records"] != 5906 or baseline["attributes"] != 385:
        raise AssertionError("intake package mutated equipment data")
    if state["current_package"]["package_id"] != "spring_expression_saved_state_artifact_intake_001":
        raise AssertionError("canonical package did not advance to saved-state intake")
    if state["next_package"]["package_id"] != "spring_charging_cable_representation_migration_001":
        raise AssertionError("unexpected charging-cable follow-up package")


if __name__ == "__main__":
    verify()
    print("Spring saved-state artifact intake: PASS")
