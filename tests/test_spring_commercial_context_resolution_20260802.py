from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "project/sources/dacia-pl-spring-commercial-context-20260802.json"
REPORT = ROOT / "data/reporting/spring_commercial_context_resolution.json"
TOOL = ROOT / "tools/review_spring_commercial_context_20260802.py"
STATE = ROOT / "project/state.json"
MAPPINGS = ROOT / "data/master/commercial_item_configurations.csv"


def read_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"expected object: {path}")
    return payload


def load_tool():
    spec = importlib.util.spec_from_file_location("spring_context_review", TOOL)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load Spring context review tool")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_contract() -> None:
    source = read_json(SOURCE)
    report = read_json(REPORT)
    tool = load_tool()

    if source["package_conclusion"]["master_rows_changed"] != 0:
        raise AssertionError("review package must not mutate master data")
    if report != tool.build_report(source):
        raise AssertionError("Spring context report is not deterministic")
    tool.verify(ROOT)

    type2 = report["type2_resolution"]
    expected_current = {
        "spring_essential_electric70_automatic",
        "spring_extreme_electric100_automatic",
    }
    if set(type2["exact_current_standard_configurations"]) != expected_current:
        raise AssertionError("unexpected exact-current Type 2 resolution")
    if type2["current_grade_unresolved_configurations"] != [
        "spring_expression_electric70_automatic"
    ]:
        raise AssertionError("Expression MY26 must remain unresolved")

    paints = {
        (item["configuration_code"], item["commercial_item_code"]): (
            item["availability_status"], item["price_pln"]
        )
        for item in report["paint_resolution"]["exact_current_my26_rows"]
    }
    expected_paints = {
        (
            "spring_essential_electric70_automatic",
            "spring_colour_biel_alpejska",
        ): ("standard", 0),
        (
            "spring_essential_electric70_automatic",
            "spring_colour_lichen_khaki",
        ): ("optional", 2300),
    }
    if paints != expected_paints:
        raise AssertionError("unexpected exact-current Essential paint states")
    if report["paint_resolution"]["my2025_price_promotions"] != 0:
        raise AssertionError("MY2025 prices must not be promoted to MY26")
    if report["stock_resolution"]["stock_totals_decomposed"] != 0:
        raise AssertionError("stock totals must not be decomposed")

    with MAPPINGS.open(encoding="utf-8-sig", newline="") as handle:
        rows = {
            row["configuration_code"]: row
            for row in csv.DictReader(handle)
            if row["commercial_item_code"] == "spring_type2_charging_cable_option"
        }
    if set(rows) != {
        "spring_essential_electric70_automatic",
        "spring_expression_electric70_automatic",
        "spring_extreme_electric100_automatic",
    }:
        raise AssertionError("unexpected Type 2 mapping set")
    if any(row["amount"] for row in rows.values()):
        raise AssertionError("review package must not invent a Type 2 price")

    state = read_json(STATE)
    if state["current_package"]["status"] != "complete":
        raise AssertionError("canonical current package must remain complete")
    current_id = state["current_package"]["package_id"]
    if not current_id:
        raise AssertionError("canonical current package is missing")
    if not state["next_package"]["package_id"]:
        raise AssertionError("canonical next package is missing")
    if state["reference_delivery"]["pull_request"] < 450:
        raise AssertionError("reference delivery predates Spring context resolution")
    if state["baseline"]["tests"] != 1788:
        raise AssertionError("import-time contracts must preserve test baseline")
    expected_rows = {
        "spring_essential_khaki_price_apply_001": 11714,
        "spring_standard_equipment_representation_review_001": 11714,
        "spring_biel_alpejska_default_colour_migration_001": 11715,
    }.get(current_id, 11713)
    if state["baseline"]["rows"] != expected_rows:
        raise AssertionError("Spring context history has an unexpected master row count")


# unittest discovery imports this module. The contract protects the completed
# Spring context evidence while allowing canonical state to advance through
# later bounded packages.
verify_contract()
