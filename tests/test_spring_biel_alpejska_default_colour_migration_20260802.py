from __future__ import annotations

import importlib.util
import json
import sys
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
    module_name = "spring_white_migration"
    spec = importlib.util.spec_from_file_location(module_name, TOOL)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load Spring white migration tool")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
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
        "source_configuration_rows_added": 1,
        "attributes_added": 0,
        "commercial_items_added": 0,
        "net_master_row_increase": 2,
    }:
        raise AssertionError("unexpected Spring white migration delta")
    if report["verified_after_counts"] != {
        "configuration_values": 3568,
        "configuration_import_specs": 139,
        "master_rows": 11729,
    }:
        raise AssertionError("unexpected Spring white post-migration counts")
    state = read_json(STATE)
    if state["current_package"]["status"] != "complete":
        raise AssertionError("canonical package must remain complete after Spring white migration")
    if state["baseline"]["rows"] < 11729:
        raise AssertionError("canonical master-row baseline regressed behind Spring white migration")
    if state["baseline"]["configuration_values"] < 3568:
        raise AssertionError("canonical configuration-value baseline drifted")
    if state["baseline"]["configuration_import_specs"] != 139:
        raise AssertionError("canonical import-spec baseline drifted")
    if state["reference_delivery"]["pull_request"] < 464:
        raise AssertionError("canonical history predates the Spring white selection review")
    if not state["next_package"]["package_id"]:
        raise AssertionError("canonical package queue is incomplete")


verify_contract()
