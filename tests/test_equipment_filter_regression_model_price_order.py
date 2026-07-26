from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "data"
    / "reporting"
    / "equipment_filter_regression_model_price_order.json"
)
STATE = ROOT / "project" / "state.json"
VERIFIER = (
    ROOT
    / "tools"
    / "review_equipment_filter_regression_model_price_order_20260726.py"
)


class EquipmentFilterRegressionModelPriceOrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_metadata_and_user_report(self) -> None:
        self.assertEqual(self.report["version"], 1)
        self.assertEqual(
            self.report["kind"],
            "equipment_filter_regression_model_price_order",
        )
        self.assertEqual(self.report["reviewed_on"], "2026-07-26")
        self.assertEqual(self.report["status"], "complete")
        self.assertEqual(
            self.report["user_report"]["affected_public_versions"],
            ["1.6.1", "1.7.0"],
        )

    def test_reproduction_records_zero_visible_equipment_choices(self) -> None:
        reproduction = self.report["reproduction"]
        self.assertEqual(reproduction["active_configuration_count"], 72)
        self.assertEqual(reproduction["equipment_facet_count"], 110)
        self.assertEqual(reproduction["visible_equipment_choices_before_fix"], 0)
        self.assertEqual(reproduction["browser"], "Chromium")
        self.assertEqual(reproduction["javascript_errors"], 0)
        self.assertIn("global completeness condition", reproduction["root_cause"])

    def test_fix_restores_search_selection_and_result_filtering(self) -> None:
        snapshot = self.report["fix_contract"]["post_fix_current_snapshot"]
        self.assertEqual(snapshot["visible_equipment_choices"], 108)
        self.assertEqual(snapshot["camera_search_visible_choices"], 1)
        self.assertEqual(snapshot["rear_view_camera_matches"], 66)
        self.assertEqual(snapshot["selection_count_after_camera_click"], 1)
        self.assertEqual(snapshot["javascript_errors"], 0)

    def test_missing_and_unknown_equipment_are_never_inferred_available(self) -> None:
        contract = self.report["fix_contract"]
        self.assertIn("source-confirmed", contract["matching_rule"])
        self.assertIn("Missing, unknown", contract["matching_rule"])
        self.assertIn("never inferred", contract["matching_rule"])
        self.assertIn("do not silently remove", contract["selection_conflict_rule"])

    def test_model_choices_are_ordered_by_minimum_catalog_price(self) -> None:
        expected = self.report["model_order_contract"]["expected_order"]
        self.assertEqual(
            [item["model_code"] for item in expected],
            [
                "sandero_iii",
                "sandero_stepway_iii",
                "jogger",
                "duster_iii",
                "bigster",
            ],
        )
        self.assertEqual(
            [item["minimum_catalog_price_pln"] for item in expected],
            [68000, 71700, 77900, 82000, 101400],
        )
        self.assertIn(
            "sort after all models",
            self.report["model_order_contract"]["missing_price_rule"],
        )

    def test_historical_releases_remain_immutable(self) -> None:
        immutability = self.report["immutability"]
        self.assertFalse(immutability["rewrite_public_1_6_1"])
        self.assertFalse(immutability["rewrite_public_1_7_0"])
        self.assertFalse(immutability["rewrite_public_1_8_0"])
        self.assertIn("new patch release", immutability["delivery"])
        self.assertEqual(
            self.report["next_package"]["name"],
            "Data Products v1.8.1 Release Preparation",
        )

    def test_data_and_comparison_boundaries_are_unchanged(self) -> None:
        self.assertEqual(
            self.report["semantic_boundaries"],
            {
                "new_data_imports": False,
                "new_comparison_pairs": False,
                "ranking": False,
                "recommendations": False,
                "inferred_equipment_availability": False,
                "master_data_changes": False,
            },
        )
        baseline = self.report["repository_baseline"]
        self.assertEqual(baseline["tests"], 1030)
        self.assertEqual(baseline["csv_files"], 46)
        self.assertEqual(baseline["rows"], 9688)
        self.assertEqual(baseline["configuration_values"], 2949)
        self.assertEqual(baseline["configuration_value_ranges"], 244)
        self.assertEqual(baseline["availability_records"], 4754)
        self.assertEqual(baseline["attributes"], 385)

    def test_verifier_and_project_state_accept_fix(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VERIFIER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            completed.stderr or completed.stdout,
        )
        self.assertIn(
            "PASS: equipment filter regression and model price ordering",
            completed.stdout,
        )
        state = json.loads(STATE.read_text(encoding="utf-8"))
        self.assertEqual(
            state["phase"],
            "Equipment Filter Regression and Model Price Ordering",
        )
        self.assertEqual(
            state["current_package"]["name"],
            "Equipment Filter Regression and Model Price Ordering",
        )
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(
            state["next_package"]["name"],
            "Data Products v1.8.1 Release Preparation",
        )
        self.assertEqual(state["baseline"]["tests"], 1030)


if __name__ == "__main__":
    unittest.main()
