from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "project/sources/dacia-pl-spring-current-grade-snapshots-20260802.json"
REPORT = ROOT / "data/reporting/spring_current_grade_snapshot_capture.json"
TOOL = ROOT / "tools/capture_spring_current_grade_snapshots_20260802.py"
STATE = ROOT / "project/state.json"


def read_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"expected object: {path}")
    return payload


def load_tool():
    spec = importlib.util.spec_from_file_location("spring_grade_capture", TOOL)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load Spring grade capture tool")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_contract() -> None:
    source = read_json(SOURCE)
    report = read_json(REPORT)
    tool = load_tool()
    if report != tool.build_report(source):
        raise AssertionError("Spring grade snapshot report is not deterministic")
    tool.verify(ROOT)

    summary = report["capture_summary"]
    if summary != {
        "grade_count": 2,
        "complete_exact_current_snapshots": 0,
        "partial_exact_current_snapshots": 2,
        "expression_unresolved_fields": 5,
        "extreme_unresolved_fields": 1,
        "my2025_values_promoted": 0,
        "stock_cards_generalized": 0,
        "master_rows_changed": 0,
    }:
        raise AssertionError("unexpected Spring grade capture summary")

    expression = report["expression"]
    if expression["equipment_item_count"] != 46:
        raise AssertionError("Expression exact grade equipment count drifted")
    if set(expression["unresolved_fields"]) != {
        "catalog_price",
        "paint_palette",
        "type2_charging_cable",
        "home_charging_cable",
        "dc40_option_price",
    }:
        raise AssertionError("Expression unresolved boundary drifted")
    if expression["master_migration_authorized"]:
        raise AssertionError("partial Expression snapshot must not authorize migration")

    extreme = report["extreme"]
    if extreme["catalog_price_pln"] != 85900:
        raise AssertionError("Extreme current catalogue price drifted")
    if extreme["technical"] != {
        "power_kw": 75,
        "power_hp": 100,
        "battery_capacity_kwh": 24.3,
        "wltp_range_km": 225,
        "zero_to_100_seconds": 9.6,
        "ac_charging_kw": 7,
        "dc_charging_kw": 40,
    }:
        raise AssertionError("Extreme technical snapshot drifted")
    charging = {
        item["name"]: item for item in extreme["charging_equipment"]
    }
    type2 = "kabel do ładowania z końcówką typu 2 (do Wallbox-a i terminali publicznych)"
    if charging[type2]["availability_status"] != "standard":
        raise AssertionError("Extreme Type 2 standard state drifted")
    if extreme["unresolved_fields"].keys() != {"paint_palette"}:
        raise AssertionError("Extreme unresolved boundary drifted")

    if report["mutation_summary"] != {
        "master_rows_changed": 0,
        "prices_imported": 0,
        "availability_states_changed": 0,
        "models_or_domains_added": 0,
    }:
        raise AssertionError("capture-only package mutated master scope")

    state = read_json(STATE)
    if state["current_package"]["status"] != "complete":
        raise AssertionError("canonical current package must remain complete")
    current_id = state["current_package"]["package_id"]
    if not current_id:
        raise AssertionError("canonical current package is missing")
    if not state["next_package"]["package_id"]:
        raise AssertionError("canonical next package is missing")
    if state["reference_delivery"]["pull_request"] < 451:
        raise AssertionError("reference delivery predates Spring snapshot capture")
    if state["baseline"]["tests"] != 1788:
        raise AssertionError("import-time contracts must preserve test baseline")
    expected_rows = (
        11714
        if current_id
        in {
            "spring_essential_khaki_price_apply_001",
            "spring_standard_equipment_representation_review_001",
        }
        else 11713
    )
    if state["baseline"]["rows"] != expected_rows:
        raise AssertionError("Spring snapshot history has an unexpected master row count")


# The contract protects the completed exact-current snapshot while allowing
# canonical state to advance through later bounded review and apply packages.
verify_contract()
