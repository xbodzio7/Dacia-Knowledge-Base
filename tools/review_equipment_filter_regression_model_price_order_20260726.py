#!/usr/bin/env python3
"""Verify the equipment-filter regression fix and model price ordering."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "data"
    / "reporting"
    / "equipment_filter_regression_model_price_order.json"
)
STATE = ROOT / "project" / "state.json"

sys.path.insert(0, str(ROOT / "tools"))

from reporting.configuration_shortlist import ShortlistCriteria  # noqa: E402
from reporting.configuration_shortlist_html import collect_browser_catalog  # noqa: E402
from reporting.configuration_shortlist_selection_html import (  # noqa: E402
    render_html,
)


class ReviewError(RuntimeError):
    """Raised when the regression-fix contract drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ensure(isinstance(payload, dict), f"expected JSON object: {path}")
    return payload


def verify_report(payload: Mapping[str, Any]) -> None:
    ensure(payload.get("version") == 1, "report version differs")
    ensure(
        payload.get("kind")
        == "equipment_filter_regression_model_price_order",
        "report kind differs",
    )
    ensure(payload.get("reviewed_on") == "2026-07-26", "review date differs")
    ensure(payload.get("status") == "complete", "review is not complete")

    user_report = payload.get("user_report")
    ensure(isinstance(user_report, Mapping), "user report is missing")
    ensure(
        user_report.get("affected_public_versions") == ["1.6.1", "1.7.0"],
        "reported versions differ",
    )

    reproduction = payload.get("reproduction")
    ensure(isinstance(reproduction, Mapping), "reproduction is missing")
    ensure(
        reproduction.get("source_commit")
        == "0c447452fe6a0f46522a8c7eeb209fb8ad342fba",
        "reproduction source differs",
    )
    ensure(reproduction.get("active_configuration_count") == 72, "configuration count differs")
    ensure(reproduction.get("equipment_facet_count") == 110, "equipment facet count differs")
    ensure(reproduction.get("visible_equipment_choices_before_fix") == 0, "pre-fix visible count differs")
    ensure(reproduction.get("javascript_errors") == 0, "pre-fix JavaScript error count differs")

    fix = payload.get("fix_contract")
    ensure(isinstance(fix, Mapping), "fix contract is missing")
    snapshot = fix.get("post_fix_current_snapshot")
    ensure(isinstance(snapshot, Mapping), "post-fix snapshot is missing")
    ensure(snapshot.get("visible_equipment_choices") == 108, "post-fix visible count differs")
    ensure(snapshot.get("camera_search_visible_choices") == 1, "camera search count differs")
    ensure(snapshot.get("rear_view_camera_matches") == 66, "camera result count differs")
    ensure(snapshot.get("selection_count_after_camera_click") == 1, "selection count differs")
    ensure(snapshot.get("javascript_errors") == 0, "post-fix JavaScript error count differs")

    order = payload.get("model_order_contract")
    ensure(isinstance(order, Mapping), "model order contract is missing")
    expected_order = order.get("expected_order")
    ensure(isinstance(expected_order, list) and len(expected_order) == 5, "model order differs")
    ensure(
        [item.get("model_code") for item in expected_order]
        == [
            "sandero_iii",
            "sandero_stepway_iii",
            "jogger",
            "duster_iii",
            "bigster",
        ],
        "expected model code order differs",
    )
    ensure(
        [item.get("minimum_catalog_price_pln") for item in expected_order]
        == [68000, 71700, 77900, 82000, 101400],
        "expected model minimum prices differ",
    )

    immutability = payload.get("immutability")
    ensure(isinstance(immutability, Mapping), "immutability contract is missing")
    for key in (
        "rewrite_public_1_6_1",
        "rewrite_public_1_7_0",
        "rewrite_public_1_8_0",
    ):
        ensure(immutability.get(key) is False, f"immutability boundary differs: {key}")

    boundaries = payload.get("semantic_boundaries")
    ensure(isinstance(boundaries, Mapping), "semantic boundaries are missing")
    for key in (
        "new_data_imports",
        "new_comparison_pairs",
        "ranking",
        "recommendations",
        "inferred_equipment_availability",
        "master_data_changes",
    ):
        ensure(boundaries.get(key) is False, f"semantic boundary differs: {key}")
    ensure(
        payload.get("next_package", {}).get("name")
        == "Data Products v1.8.1 Release Preparation",
        "next package differs",
    )


def node_contract(catalog: Mapping[str, Any]) -> dict[str, Any]:
    script = ROOT / "tools" / "reporting" / "configuration_shortlist_browser.js"
    program = r"""
const fs = require("fs");
const api = require(process.argv[1]);
const catalog = JSON.parse(fs.readFileSync(0, "utf8"));
const initial = api.reconcileEquipmentSelection(catalog, {
  models: [], versions: [], transmissions: [], powertrains: [],
  required_equipment: [], required_standard_equipment: []
});
const camera = api.filterCatalog(catalog, {
  required_equipment: ["rear_view_camera"],
  required_standard_equipment: []
});
const synthetic = [
  {equipment: {
    partial: {availability_status: "standard"},
    universal: {availability_status: "standard"},
    unknown_state: {availability_status: "unknown"}
  }},
  {equipment: {
    partial: {availability_status: "not_available"},
    universal: {availability_status: "optional"},
    unknown_state: {availability_status: "standard"}
  }},
  {equipment: {
    universal: {availability_status: "standard"}
  }}
];
const partialConfiguration = {
  configuration_code: "partial",
  model_code: "m",
  version_code: "v",
  transmission_type: "manual",
  powertrain_label: "p",
  catalog_price: {state: "missing"},
  number_of_seats: {state: "missing"},
  equipment: {}
};
process.stdout.write(JSON.stringify({
  initial,
  camera_match_count: camera.results.length,
  camera_missing_count: camera.summary.data_unknowns.required_equipment_missing.rear_view_camera || 0,
  synthetic_facets: api.differentiatingEquipmentCodes(synthetic),
  missing_reason: api.evaluate(partialConfiguration, {
    required_equipment: ["partial"],
    required_standard_equipment: []
  })
}));
"""
    completed = subprocess.run(
        ["node", "-e", program, str(script)],
        input=json.dumps(catalog, ensure_ascii=False),
        text=True,
        capture_output=True,
        check=False,
        cwd=ROOT,
    )
    ensure(completed.returncode == 0, completed.stderr or completed.stdout)
    payload = json.loads(completed.stdout)
    ensure(isinstance(payload, dict), "Node contract returned invalid JSON")
    return payload


def verify_repository() -> None:
    catalog = collect_browser_catalog(ROOT, ShortlistCriteria())
    configurations = catalog.get("configurations")
    facets = catalog.get("facets")
    ensure(isinstance(configurations, list) and len(configurations) == 72, "current configuration count differs")
    ensure(isinstance(facets, Mapping), "catalog facets are missing")
    equipment = facets.get("equipment")
    models = facets.get("models")
    ensure(isinstance(equipment, list) and len(equipment) == 110, "current equipment facet count differs")
    ensure(isinstance(models, list) and len(models) == 5, "current model facet count differs")
    ensure(
        [item.get("code") for item in models]
        == [
            "sandero_iii",
            "sandero_stepway_iii",
            "jogger",
            "duster_iii",
            "bigster",
        ],
        "current model order differs",
    )
    ensure(
        [item.get("minimum_catalog_price_pln") for item in models]
        == [68000, 71700, 77900, 82000, 101400],
        "current model minimum prices differ",
    )

    contract = node_contract(catalog)
    initial = contract.get("initial")
    ensure(isinstance(initial, Mapping), "initial equipment state is missing")
    available = initial.get("available_equipment")
    ensure(isinstance(available, list) and len(available) == 108, "visible equipment choices differ")
    ensure("rear_view_camera" in available, "rear-view camera is not selectable")
    ensure(contract.get("camera_match_count") == 66, "rear-view camera result count differs")
    ensure(
        contract.get("synthetic_facets") == ["partial", "unknown_state"],
        "partial-coverage facet semantics differ",
    )
    missing_reason = contract.get("missing_reason")
    ensure(
        isinstance(missing_reason, list)
        and "equipment_missing:partial" in missing_reason,
        "missing equipment was treated as available",
    )

    rendered = render_html(catalog)
    ensure(
        "potwierdzone jako dostępne w co najmniej jednej" in rendered,
        "corrected equipment explanation is missing",
    )
    ensure(
        "Brak danych i status nieustalony nie spełniają filtra" in rendered,
        "unknown handling explanation is missing",
    )
    ensure(
        rendered.index('data-value="sandero_iii"')
        < rendered.index('data-value="sandero_stepway_iii"')
        < rendered.index('data-value="jogger"')
        < rendered.index('data-value="duster_iii"')
        < rendered.index('data-value="bigster"'),
        "rendered model picker order differs",
    )

    state = load_json(STATE)
    ensure(
        state.get("phase")
        == "Equipment Filter Regression and Model Price Ordering",
        "project phase differs",
    )
    ensure(
        state.get("current_package", {}).get("name")
        == "Equipment Filter Regression and Model Price Ordering",
        "current package differs",
    )
    ensure(state.get("current_package", {}).get("status") == "complete", "current package is not complete")
    ensure(
        state.get("next_package", {}).get("name")
        == "Data Products v1.8.1 Release Preparation",
        "state next package differs",
    )
    baseline = state.get("baseline", {})
    ensure(baseline.get("tests") == 1030, "test baseline differs")
    ensure(baseline.get("csv_files") == 46, "CSV baseline changed")
    ensure(baseline.get("rows") == 9688, "master row baseline changed")
    ensure(baseline.get("configuration_values") == 2949, "configuration values changed")
    ensure(baseline.get("configuration_value_ranges") == 244, "configuration ranges changed")
    ensure(baseline.get("availability_records") == 4754, "availability baseline changed")
    ensure(baseline.get("attributes") == 385, "attribute baseline changed")


def verify() -> None:
    payload = load_json(REPORT)
    verify_report(payload)
    verify_repository()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the regression-fix contract.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    parse_args(argv)
    try:
        verify()
    except (OSError, json.JSONDecodeError, ReviewError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: equipment filter regression and model price ordering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
