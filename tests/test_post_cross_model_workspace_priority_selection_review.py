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
    / "post_cross_model_workspace_priority_selection_review.json"
)
STATE = ROOT / "project" / "state.json"
VERIFIER = (
    ROOT
    / "tools"
    / "review_post_cross_model_workspace_priority_selection_20260727.py"
)


class PostCrossModelWorkspacePrioritySelectionReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_metadata_and_source_milestone_are_exact(self) -> None:
        self.assertEqual(self.report["version"], 1)
        self.assertEqual(
            self.report["kind"],
            "post_cross_model_workspace_priority_selection_review",
        )
        self.assertEqual(self.report["reviewed_on"], "2026-07-27")
        self.assertEqual(self.report["status"], "complete")
        self.assertEqual(
            self.report["source_milestone"],
            "cross_model_workspace_entry_point.json",
        )

    def test_selection_policy_preserves_stable_weights(self) -> None:
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

    def test_repository_readiness_records_completed_consumer_flow(self) -> None:
        readiness = self.report["repository_readiness"]
        self.assertEqual(
            readiness["latest_documented_public_release"],
            "data-products-v1.8.1",
        )
        self.assertEqual(readiness["public_release_archive_members"], 85)
        self.assertEqual(readiness["offline_workspace_primary_cards"], 5)
        self.assertEqual(readiness["offline_workspace_local_links"], 84)
        self.assertEqual(readiness["active_configurations"], 72)
        self.assertEqual(readiness["model_families"], 5)
        self.assertEqual(readiness["independent_comparison_scopes"], 19)
        self.assertEqual(readiness["within_scope_pairs"], 114)
        self.assertEqual(readiness["recorded_differences"], 1695)

    def test_repository_readiness_records_pdf_foundation(self) -> None:
        readiness = self.report["repository_readiness"]
        self.assertEqual(readiness["registered_official_brochures"], 5)
        self.assertEqual(readiness["registered_brochure_pages"], 114)
        self.assertEqual(readiness["registered_brochure_bytes"], 40608101)
        self.assertTrue(readiness["registered_brochures_have_sha256"])
        self.assertEqual(readiness["pdf_text_backend_in_quality_ci"], "pdftotext")
        self.assertEqual(
            readiness["existing_pdf_review_command"],
            "configuration-gap-source-review",
        )
        self.assertEqual(len(readiness["existing_declarative_import_commands"]), 2)

    def test_candidate_order_scores_and_statuses_are_exact(self) -> None:
        candidates = self.report["candidates"]
        self.assertEqual([candidate["rank"] for candidate in candidates], [1, 2, 3, 4, 5])
        self.assertEqual(
            [candidate["weighted_score"] for candidate in candidates],
            [81, 78, 76, 57, 46],
        )
        self.assertEqual(
            [candidate["status"] for candidate in candidates],
            [
                "selected",
                "follow_up",
                "follow_up",
                "blocked_evidence",
                "blocked_source",
            ],
        )
        self.assertEqual(
            candidates[0]["code"],
            "pdf_candidate_extraction_automation_review",
        )

    def test_selection_requires_candidate_only_pdf_review(self) -> None:
        selection = self.report["selection"]
        self.assertEqual(
            selection["name"],
            "PDF Candidate Extraction Automation Review",
        )
        self.assertEqual(selection["weighted_score"], 81)
        self.assertIn("candidate-only", selection["rationale"])
        self.assertIn("without changing source data", selection["rationale"])
        self.assertEqual(
            self.report["next_package"]["name"],
            "PDF Candidate Extraction Automation Review",
        )

    def test_pdf_review_contract_preserves_evidence_boundaries(self) -> None:
        contract = self.report["pdf_candidate_extraction_review_contract"]
        self.assertEqual(contract["registered_source_count"], 5)
        self.assertEqual(contract["registered_page_count"], 114)
        self.assertIn("source_sha256", contract["required_candidate_provenance"])
        self.assertIn("requires_visual_review", contract["required_status_boundaries"])
        self.assertIn("ambiguous_source_evidence", contract["required_status_boundaries"])
        self.assertIn("no_master_data_changes", contract["required_verification"])
        self.assertIn(
            "no_approved_import_spec_generation",
            contract["required_verification"],
        )
        self.assertIn("OCR implementation", contract["non_goals"])
        self.assertIn("automatic approval", contract["non_goals"])
        self.assertIn("resolving ambiguous evidence", contract["non_goals"])

    def test_verifier_and_project_state_accept_completed_review(self) -> None:
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
            "PASS: post-cross-model workspace priority selection review",
            completed.stdout,
        )
        state = json.loads(STATE.read_text(encoding="utf-8"))
        self.assertGreaterEqual(state["baseline"]["tests"], 1078)
        self.assertEqual(state["baseline"]["rows"], 9688)
        self.assertEqual(state["baseline"]["configuration_values"], 2949)
        self.assertEqual(state["baseline"]["availability_records"], 4754)


if __name__ == "__main__":
    unittest.main()
