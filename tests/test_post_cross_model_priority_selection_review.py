from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "reporting" / "post_cross_model_priority_selection_review.json"
STATE = ROOT / "project" / "state.json"
VERIFIER = ROOT / "tools" / "review_post_cross_model_priority_selection_20260726.py"


class PostCrossModelPrioritySelectionReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_metadata_and_source_milestone(self) -> None:
        self.assertEqual(self.report["version"], 1)
        self.assertEqual(
            self.report["kind"],
            "post_cross_model_priority_selection_review",
        )
        self.assertEqual(self.report["reviewed_on"], "2026-07-26")
        self.assertEqual(self.report["status"], "complete")
        self.assertEqual(
            self.report["source_milestone"],
            "cross_model_comparison_view_closure_review.json",
        )

    def test_selection_policy_has_stable_weights(self) -> None:
        policy = self.report["selection_policy"]
        self.assertEqual(policy["scale"], "1_to_5")
        self.assertEqual(
            policy["weights_percent"],
            {
                "consumer_value": 30,
                "evidence_readiness": 25,
                "existing_tooling_reuse": 20,
                "low_implementation_risk": 15,
                "dependency_clearance": 10,
            },
        )
        self.assertEqual(sum(policy["weights_percent"].values()), 100)
        self.assertIn("highest weighted score", policy["decision_rule"])

    def test_repository_readiness_distinguishes_public_and_candidate_archives(self) -> None:
        readiness = self.report["repository_readiness"]
        self.assertEqual(
            readiness["latest_documented_public_release"],
            "data-products-v1.7.0",
        )
        self.assertEqual(readiness["public_release_archive_members"], 83)
        self.assertEqual(readiness["current_candidate_archive_members"], 85)
        self.assertEqual(
            readiness["unpublished_products"],
            [
                "cross-model/cross-model-comparison-view.json",
                "cross-model/cross-model-comparison-view.html",
            ],
        )
        self.assertEqual(readiness["active_configurations"], 72)
        self.assertEqual(readiness["independent_comparison_scopes"], 19)
        self.assertEqual(readiness["within_scope_pairs"], 114)
        self.assertEqual(readiness["recorded_differences"], 1695)
        self.assertEqual(readiness["technical_comparison_facets"], 124)
        self.assertEqual(readiness["equipment_facets"], 110)

    def test_candidate_order_scores_and_statuses(self) -> None:
        candidates = self.report["candidates"]
        self.assertEqual([item["rank"] for item in candidates], [1, 2, 3, 4, 5])
        self.assertEqual(
            [item["weighted_score"] for item in candidates],
            [100, 84, 67, 57, 46],
        )
        self.assertEqual(
            [item["status"] for item in candidates],
            [
                "selected",
                "follow_up_after_release",
                "strategic_later",
                "blocked_evidence",
                "blocked_source",
            ],
        )
        self.assertEqual(
            candidates[0]["code"],
            "data_products_v1_8_0_release_preparation",
        )

    def test_selection_delivers_closed_products_before_new_work(self) -> None:
        selection = self.report["selection"]
        self.assertEqual(
            selection["name"],
            "Data Products v1.8.0 Release Preparation",
        )
        self.assertEqual(selection["weighted_score"], 100)
        self.assertIn("absent from immutable public v1.7.0", selection["rationale"])
        self.assertIn("minor version", selection["rationale"])

    def test_release_preparation_contract_targets_v1_8_0(self) -> None:
        contract = self.report["release_preparation_contract"]
        self.assertEqual(contract["target_version"], "1.8.0")
        self.assertEqual(contract["target_tag"], "data-products-v1.8.0")
        self.assertEqual(contract["publication_mode"], "manual_after_verified_preparation")
        self.assertEqual(contract["expected_archive_members"], 85)
        self.assertEqual(
            contract["required_new_members"],
            [
                "cross-model/cross-model-comparison-view.json",
                "cross-model/cross-model-comparison-view.html",
            ],
        )
        self.assertEqual(len(contract["required_assets"]), 3)
        self.assertIn("cross_model_product_verification", contract["required_verification"])
        self.assertIn("cross_model_ui_expansion", contract["non_goals"])

    def test_blocked_candidates_preserve_evidence_boundaries(self) -> None:
        candidates = {item["code"]: item for item in self.report["candidates"]}
        exact = candidates["exact_configuration_expansion_review"]
        self.assertEqual(exact["status"], "blocked_evidence")
        self.assertEqual(len(exact["blockers"]), 4)
        spring = candidates["spring_source_foundation_review"]
        self.assertEqual(spring["status"], "blocked_source")
        self.assertEqual(
            spring["blockers"],
            [
                "no_registered_exact_current_spring_catalogue_source",
                "no_approved_configuration_scope",
            ],
        )

    def test_verifier_and_project_state_preserve_selection_history(self) -> None:
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
            "PASS: post-cross-model priority selection review",
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
        self.assertGreaterEqual(state["baseline"]["tests"], 1006)
        self.assertGreaterEqual(state["baseline"]["rows"], 9688)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2949)
        self.assertGreaterEqual(state["baseline"]["configuration_value_ranges"], 244)
        self.assertGreaterEqual(state["baseline"]["attributes"], 385)

if __name__ == "__main__":
    unittest.main()
