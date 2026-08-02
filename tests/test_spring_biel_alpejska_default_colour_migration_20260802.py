from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/apply_spring_biel_alpejska_default_colour_migration_20260802.py"
SPEC = ROOT / "data/imports/configuration_values/spring_biel_alpejska_default_colour_20260802.json"
STATE = ROOT / "project/state.json"


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected object: {path}")
    return value


def load_tool():
    spec = importlib.util.spec_from_file_location("spring_white_migration", TOOL)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load Spring white migration tool")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_contract() -> None:
    tool = load_tool()
    tool.verify(ROOT)
    if read_json(SPEC) != tool.EXPECTED_SPEC:
        raise AssertionError("canonical Spring white import specification drifted")
    report = tool.build(ROOT)
    if report["master_data_delta"] != {
        "configuration_value_rows_added": 1,
        "commercial_mapping_rows_updated": 1,
        "commercial_mapping_rows_added": 0,
        "source_rows_added": 0,
        "attributes_added": 0,
        "commercial_items_added": 0,
        "net_master_row_increase": 1,
    }:
        raise AssertionError("unexpected Spring white migration delta")
    if report["verified_after_counts"] != {
        "configuration_values": 3568,
        "configuration_import_specs": 139,
        "master_rows": 11728,
    }:
        raise AssertionError("unexpected Spring white post-migration counts")
    state = read_json(STATE)
    if state["current_package"]["package_id"] != "spring_biel_alpejska_default_colour_migration_001":
        raise AssertionError("canonical package did not advance to Spring white migration")
    if state["next_package"]["package_id"] != "post_spring_biel_alpejska_priority_selection_review_001":
        raise AssertionError("unexpected next package after Spring white migration")
    if state["reference_delivery"]["pull_request"] != 464:
        raise AssertionError("Spring white migration must reference PR 464")
    if state["baseline"]["rows"] != 11728:
        raise AssertionError("canonical master-row baseline drifted")
    if state["baseline"]["configuration_values"] != 3568:
        raise AssertionError("canonical configuration-value baseline drifted")
    if state["baseline"]["configuration_import_specs"] != 139:
        raise AssertionError("canonical import-spec baseline drifted")


verify_contract()
