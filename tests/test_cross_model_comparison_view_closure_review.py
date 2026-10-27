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
    / "cross_model_comparison_view_closure_review.json"
)
STATE = ROOT / "project" / "state.json"
VERIFIER = ROOT / "tools" / "review_cross_model_comparison_view_closure_20260726.py"


class CrossModelComparisonViewClosureReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_metadata_and_exact_source_package(self) -> None:
        self.assertEqual(self.report["version"], 1)
        self.assertEqual(
            self.report["kind"],
            "cross_model_comparison_view_closure_review",
        )
        self.assertEqual(self.report["reviewed_on"], "2026-07-26")
        self.assertEqual(self.report["status"], "complete")
        source = self.report["source_package"]
        self.assertEqual(source["name"], "Cross-Model Comparison View Foundation")
        self.assertEqual(source["pull_request"], 281)
        self.assertEqual(
            source["merge_commit"],
            "4f11eaa9be96dd028d4c7f5e0e36c1ba27325558",
        )

    def test_product_contract_preserves_models_scopes_and_pairs(self) -> None:
        contract = self.report["product_contract"]
        self.assertEqual(
            contract["kind"],
            "scope_preserving_cross_model_comparison_view",
        )
        self.assertEqual(contract["view_version"], 1)
        self.assertEqual(contract["snapshot_date"], "2026-07-25")
        self.assertEqual(contract["model_family_count"], 5)
        self.assertEqual(contract["reporting_scope_count"], 19)
        self.assertEqual(contract["single_model_scope_count"], 18)
        self.assertEqual(contract["mixed_model_scope_count"], 1)
        self.assertEqual(contract["active_configuration_count"], 72)
        self.assertEqual(contract["within_scope_pair_count"], 114)
        self.assertEqual(contract["catalog_price_recorded_count"], 72)

    def test_mixed_scope_remains_exact(self) -> None:
        mixed = self.report["product_contract"]["mixed_scope"]
        self.assertEqual(mixed["slug"], "sandero_ecog120_manual")
        self.assertEqual(mixed["configuration_count"], 5)
        self.assertEqual(mixed["pair_count"], 10)
        self.assertEqual(mixed["technical_slot_count"], 56)
        self.assertEqual(
            mixed["model_codes"],
            ["sandero_iii", "sandero_stepway_iii"],
        )

    def test_output_and_link_contracts_match_release_inventory(self) -> None:
        output = self.report["output_contract"]
        self.assertEqual(
            output["json_path"],
            "cross-model/cross-model-comparison-view.json",
        )
        self.assertEqual(
            output["html_path"],
            "cross-model/cross-model-comparison-view.html",
        )
        self.assertEqual(output["release_archive_member_count"], 85)
        self.assertEqual(output["comparison_paths_in_json"], 76)
        self.assertEqual(output["navigation_paths_in_json"], 2)
        self.assertEqual(output["local_file_links_in_html"], 57)
        self.assertTrue(output["standalone_html"])
        self.assertFalse(output["javascript_used"])
        self.assertFalse(output["runtime_image_dependency"])
        self.assertTrue(output["byte_deterministic"])
        links = self.report["link_contract"]
        self.assertTrue(links["all_local_file_targets_exist_in_release"])
        self.assertFalse(links["path_escape_allowed"])
        self.assertFalse(links["cross_scope_launch_allowed"])

    def test_unknown_seat_values_remain_not_stated(self) -> None:
        unknown = self.report["unknown_contract"]
        self.assertEqual(
            unknown["models_without_recorded_seat_values"],
            ["bigster", "duster_iii"],
        )
        self.assertEqual(unknown["machine_state"], "not_stated")
        self.assertEqual(unknown["human_label"], "nie podano")
        self.assertFalse(unknown["zero_substitution_allowed"])
        self.assertFalse(unknown["assumed_five_seats_allowed"])

    def test_semantic_and_cli_boundaries_are_closed(self) -> None:
        boundaries = self.report["semantic_boundaries"]
        self.assertEqual(
            boundaries,
            {
                "cross_scope_pairs_generated": False,
                "ranking_generated": False,
                "recommendations_generated": False,
                "inferred_values_generated": False,
                "master_data_changed": False,
                "schema_changed": False,
                "comparison_engine_changed": False,
            },
        )
        cli = self.report["cli_contract"]
        self.assertEqual(cli["command"], "cross-model-comparison-view")
        self.assertEqual(cli["json_option"], "--json")
        self.assertEqual(cli["html_option"], "--html")
        self.assertTrue(cli["at_least_one_output_required"])
        self.assertTrue(cli["both_outputs_supported"])

    def test_closure_selects_post_milestone_priority_review(self) -> None:
        self.assertEqual(self.report["closure_decision"]["result"], "closed")
        self.assertEqual(
            self.report["next_package"]["name"],
            "Post-Cross-Model Priority Selection Review",
        )
        baseline = self.report["repository_baseline"]
        self.assertEqual(baseline["tests"], 998)
        self.assertEqual(baseline["csv_files"], 46)
        self.assertEqual(baseline["rows"], 9688)
        self.assertEqual(baseline["configuration_values"], 2949)
        self.assertEqual(baseline["configuration_value_ranges"], 244)
        self.assertEqual(baseline["availability_records"], 4754)
        self.assertEqual(baseline["attributes"], 385)

    def test_verifier_and_project_state_preserve_closure_history(self) -> None:
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
            "PASS: cross-model comparison view closure review",
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
        self.assertGreaterEqual(state["baseline"]["tests"], 998)
        self.assertGreaterEqual(state["baseline"]["rows"], 9688)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2949)
        self.assertGreaterEqual(state["baseline"]["configuration_value_ranges"], 244)
        self.assertGreaterEqual(state["baseline"]["availability_records"], 4754)
        self.assertGreaterEqual(state["baseline"]["attributes"], 385)

if __name__ == "__main__":
    unittest.main()
