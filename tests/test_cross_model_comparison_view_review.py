from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "reporting" / "cross_model_comparison_view_review.json"
STATE = ROOT / "project" / "state.json"
VERIFIER = ROOT / "tools" / "review_cross_model_comparison_view_history_20260726.py"


class CrossModelComparisonViewReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_review_metadata_and_source_release(self) -> None:
        self.assertEqual(self.report["version"], 1)
        self.assertEqual(
            self.report["kind"],
            "cross_model_comparison_view_review",
        )
        self.assertEqual(self.report["reviewed_on"], "2026-07-26")
        self.assertEqual(self.report["status"], "complete")
        source = self.report["source_release"]
        self.assertEqual(source["tag"], "data-products-v1.7.0")
        self.assertEqual(
            source["target_commit"],
            "99e0e19b86cad6eae619f37702464e6a5a761cd8",
        )
        self.assertEqual(source["verification"], "PASS")

    def test_inventory_preserves_current_scope_boundaries(self) -> None:
        inventory = self.report["inventory"]
        self.assertEqual(inventory["as_of"], "2026-07-25")
        self.assertEqual(inventory["active_configuration_count"], 72)
        self.assertEqual(inventory["model_family_count"], 5)
        self.assertEqual(inventory["reporting_scope_count"], 19)
        self.assertEqual(inventory["single_model_scope_count"], 18)
        self.assertEqual(inventory["mixed_model_scope_count"], 1)
        self.assertEqual(inventory["within_scope_pair_count"], 114)
        self.assertEqual(inventory["price_recorded_count"], 72)
        self.assertEqual(inventory["technical_comparison_facet_count"], 124)
        self.assertEqual(inventory["equipment_facet_count"], 110)
        self.assertTrue(inventory["one_scope_per_configuration"])

    def test_model_family_cards_have_exact_counts_prices_and_unknowns(self) -> None:
        models = {
            item["model_code"]: item
            for item in self.report["model_families"]
        }
        self.assertEqual(set(models), {
            "bigster",
            "duster_iii",
            "jogger",
            "sandero_iii",
            "sandero_stepway_iii",
        })
        expected = {
            "bigster": (14, 4, 101400, 137600, "14/14", []),
            "duster_iii": (27, 5, 82000, 123600, "27/27", []),
            "jogger": (22, 4, 77900, 118050, "22/22", [5, 7]),
            "sandero_iii": (4, 2, 68000, 80500, "4/4", [5]),
            "sandero_stepway_iii": (5, 3, 71700, 89400, "5/5", [5]),
        }
        for code, values in expected.items():
            item = models[code]
            self.assertEqual(item["configuration_count"], values[0])
            self.assertEqual(item["version_count"], values[1])
            self.assertEqual(item["catalog_price_min_pln"], values[2])
            self.assertEqual(item["catalog_price_max_pln"], values[3])
            self.assertEqual(item["catalog_price_coverage"], values[4])
            self.assertEqual(item["recorded_seat_values"], values[5])

    def test_existing_sandero_stepway_mixed_scope_is_preserved_exactly(self) -> None:
        mixed = self.report["existing_mixed_model_scope"]
        self.assertEqual(mixed["slug"], "sandero_ecog120_manual")
        self.assertEqual(
            mixed["model_codes"],
            ["sandero_iii", "sandero_stepway_iii"],
        )
        self.assertEqual(mixed["configuration_count"], 5)
        self.assertEqual(mixed["pair_count"], 10)
        self.assertEqual(mixed["technical_slot_count"], 56)
        self.assertIn("does not generalize", mixed["reason_preserved"])

    def test_design_options_select_navigation_and_reject_unsafe_comparisons(self) -> None:
        statuses = {
            item["code"]: item["status"]
            for item in self.report["design_options"]
        }
        self.assertEqual(
            statuses,
            {
                "scope_preserving_navigation": "selected",
                "global_common_attribute_matrix": "rejected",
                "unrestricted_cross_model_pairs": "rejected",
                "normalized_model_ranking": "rejected",
            },
        )
        rejected = {
            item["code"]: item["rejection_reason"]
            for item in self.report["design_options"]
            if item["status"] == "rejected"
        }
        self.assertIn("measurement context", rejected["global_common_attribute_matrix"])
        self.assertIn("cross-scope", rejected["unrestricted_cross_model_pairs"])
        self.assertIn("preference weights", rejected["normalized_model_ranking"])

    def test_selection_uses_three_layers_and_never_synthesizes_pairs(self) -> None:
        selection = self.report["selection"]
        self.assertEqual(selection["code"], "scope_preserving_navigation")
        self.assertEqual(
            selection["layers"],
            [
                "model_family_overview",
                "reporting_scope_directory",
                "existing_scope_comparison_launch",
            ],
        )
        self.assertIn("not stated", selection["required_unknown_handling"])
        self.assertIn("Never synthesize a pair", selection["pair_generation_rule"])
        self.assertIn("sandero_ecog120_manual", selection["mixed_scope_rule"])

    def test_implementation_contract_reuses_existing_tools_without_data_changes(self) -> None:
        contract = self.report["implementation_contract"]
        self.assertEqual(
            contract["next_package"],
            "Cross-Model Comparison View Foundation",
        )
        self.assertEqual(
            contract["outputs"],
            ["deterministic_json", "standalone_html"],
        )
        self.assertEqual(contract["model_card_count"], 5)
        self.assertEqual(contract["scope_card_count"], 19)
        self.assertEqual(contract["configuration_count"], 72)
        self.assertFalse(contract["master_data_changes"])
        self.assertFalse(contract["new_schema"])
        self.assertFalse(contract["new_comparison_engine"])
        self.assertEqual(len(contract["reuse"]), 4)
        self.assertEqual(len(contract["acceptance_criteria"]), 7)
        self.assertEqual(
            self.report["next_package"]["name"],
            "Cross-Model Comparison View Foundation",
        )

    def test_verifier_and_project_state_preserve_historical_review(self) -> None:
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
            "PASS: cross-model comparison view historical contract",
            completed.stdout,
        )
        state = json.loads(STATE.read_text(encoding="utf-8"))
        self.assertTrue(state["phase"])
        self.assertTrue(state["current_package"]["name"])
        self.assertIn(
            state["current_package"]["status"],
            {"planned", "active", "blocked", "complete"},
        )
        self.assertTrue(state["next_package"]["name"])
        self.assertGreaterEqual(state["baseline"]["tests"], 979)
        self.assertGreaterEqual(state["baseline"]["rows"], 9688)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2949)
        self.assertGreaterEqual(state["baseline"]["configuration_value_ranges"], 244)
        self.assertGreaterEqual(state["baseline"]["attributes"], 385)


if __name__ == "__main__":
    unittest.main()
