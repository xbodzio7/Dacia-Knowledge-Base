from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "reporting" / "cross_model_navigation_usability_review.json"
STATE = ROOT / "project" / "state.json"
VERIFIER = ROOT / "tools" / "review_cross_model_navigation_usability_20260727.py"


class CrossModelNavigationUsabilityReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_metadata_and_source_release_are_exact(self) -> None:
        self.assertEqual(self.report["version"], 1)
        self.assertEqual(self.report["kind"], "cross_model_navigation_usability_review")
        self.assertEqual(self.report["reviewed_on"], "2026-07-27")
        self.assertEqual(self.report["status"], "complete")
        source = self.report["source_release"]
        self.assertEqual(source["version"], "1.8.1")
        self.assertEqual(source["release_id"], 360138130)
        self.assertEqual(source["publication_record_commit"], "3b7709b41dca39f1822d20bb9a20fd61144f5443")
        self.assertEqual(source["verification"], "PASS")

    def test_current_workspace_discoverability_gap_is_exact(self) -> None:
        current = self.report["current_discoverability"]["workspace_index"]
        self.assertEqual(current["primary_card_count"], 4)
        self.assertEqual(current["scope_report_link_count"], 76)
        self.assertEqual(current["asset_link_count"], 3)
        self.assertEqual(current["total_local_link_count"], 83)
        self.assertFalse(current["cross_model_html_linked"])
        self.assertEqual(current["cross_model_entry_point_count"], 0)

    def test_cross_model_product_is_ready_for_entry_point(self) -> None:
        product = self.report["current_discoverability"]["cross_model_product"]
        self.assertEqual(product["model_family_count"], 5)
        self.assertEqual(product["reporting_scope_count"], 19)
        self.assertEqual(product["active_configuration_count"], 72)
        self.assertEqual(product["within_scope_pair_count"], 114)
        self.assertEqual(product["local_file_launch_count"], 57)
        self.assertFalse(product["javascript_used"])
        self.assertTrue(product["byte_deterministic"])

    def test_candidate_ranking_selects_smallest_change(self) -> None:
        candidates = self.report["candidates"]
        self.assertEqual([item["rank"] for item in candidates], [1, 2, 3, 4, 5])
        self.assertEqual(candidates[0]["code"], "conditional_primary_cross_model_card")
        self.assertEqual(candidates[0]["weighted_score"], 100)
        self.assertTrue(all(candidates[index]["weighted_score"] > candidates[index + 1]["weighted_score"] for index in range(4)))

    def test_selected_contract_is_conditional_and_compatible(self) -> None:
        selection = self.report["selection"]
        contract = self.report["implementation_contract"]
        self.assertEqual(selection["title"], "Models and comparison scopes")
        self.assertEqual(selection["workspace_path"], "contents/cross-model/cross-model-comparison-view.html")
        self.assertEqual(contract["member_absent_primary_card_count"], 4)
        self.assertEqual(contract["member_present_primary_card_count"], 5)
        self.assertEqual(contract["v1_8_1_expected_local_link_count"], 84)
        self.assertTrue(contract["older_release_behavior_unchanged"])
        self.assertFalse(contract["release_republication_required"])

    def test_immutability_and_semantic_boundaries_are_preserved(self) -> None:
        self.assertTrue(all(value is False for value in self.report["semantic_boundaries"].values()))

    def test_project_state_selects_implementation_package(self) -> None:
        state = json.loads(STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["phase"], "Cross-Model Navigation Usability Review")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(state["next_package"]["name"], "Cross-Model Workspace Entry Point")
        self.assertEqual(state["baseline"]["tests"], 1062)

    def test_verifier_accepts_review(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VERIFIER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("PASS: Cross-Model Navigation Usability Review", completed.stdout)


if __name__ == "__main__":
    unittest.main()
