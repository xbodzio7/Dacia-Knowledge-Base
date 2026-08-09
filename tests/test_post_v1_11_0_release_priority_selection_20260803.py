from __future__ import annotations

import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/reporting/post_v1_11_0_release_priority_selection_review.json"
PACKAGE_ID = "post_v1_11_0_release_priority_selection_review_001"
NEXT_PACKAGE_ID = "portfolio_model_family_summary_001"


class PostV111ReleasePrioritySelectionReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_publication_is_the_verified_selection_starting_point(self) -> None:
        publication = self.report["publication"]
        self.assertEqual(publication["tag"], "data-products-v1.11.0")
        self.assertEqual(
            publication["source_commit"],
            "0f9a76228ef374d7982421c5a246f00fe7378a94",
        )
        self.assertTrue(publication["double_build_byte_identity"])
        self.assertEqual(publication["offline_workspace_verification"], "PASS")

    def test_source_registry_receipt_matches_canonical_rows(self) -> None:
        with (ROOT / "data/master/sources.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            rows = [
                row for row in csv.DictReader(handle)
                if not row.get("document_date") or row.get("document_date") <= "2026-08-03"
            ]
        self.assertGreater(len(rows), 0)
        self.assertEqual(self.report["source_registry"]["source_count"], len(rows))

    def test_no_source_backed_candidate_is_eligible(self) -> None:
        completeness = self.report["completeness"]
        self.assertEqual(completeness["active_configuration_count"], 81)
        self.assertEqual(completeness["missing_technical_count"], 89)
        self.assertEqual(completeness["missing_equipment_count"], 36)
        self.assertEqual(completeness["candidate_count"], 7)
        self.assertEqual(completeness["exhausted_source_candidate_count"], 7)
        self.assertEqual(completeness["eligible_candidate_count"], 0)

    def test_selected_package_follows_the_reporting_roadmap(self) -> None:
        selection = self.report["selection"]
        self.assertEqual(selection["package_id"], NEXT_PACKAGE_ID)
        self.assertEqual(selection["kind"], "reporting_product")
        self.assertIn("JSON, Markdown and HTML", selection["goal"])
        roadmap = (ROOT / "project/ROADMAP.md").read_text(encoding="utf-8")
        for item in self.report["roadmap_reporting_contract"]:
            self.assertIn(item, roadmap)

    def test_selection_preserves_non_inference_boundaries(self) -> None:
        boundaries = set(self.report["preserved_boundaries"])
        self.assertIn("no exhausted source candidate is reopened", boundaries)
        self.assertIn("no cross-scope configuration pair is generated", boundaries)
        self.assertIn("no ranking or recommendation is generated", boundaries)
        self.assertIn(
            "no source-backed value is inferred or transferred between configurations",
            boundaries,
        )

    def test_review_tool_verify_mode_passes(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "tools/review_post_v1_11_0_release_priority_selection_20260803.py",
                "--verify",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_canonical_state_advances_to_selected_reporting_package(self) -> None:
        state = json.loads(
            (ROOT / "project/state.json").read_text(encoding="utf-8")
        )
        self.assertGreaterEqual(state["baseline"]["tests"], 1842)
        self.assertEqual(
            self.report["selection"]["package_id"], NEXT_PACKAGE_ID
        )
        package_doc = (
            ROOT
            / "project/packages/post-v1.11.0-release-priority-selection-review-20260803.md"
        )
        self.assertTrue(package_doc.exists())
        if state["current_package"]["package_id"] == PACKAGE_ID:
            self.assertEqual(
                state["current_package"]["status"], "complete"
            )
            self.assertEqual(
                state["next_package"]["package_id"], NEXT_PACKAGE_ID
            )
            manifest = set(state["current_package"]["manifest_paths"])
            required = {
                "tools/review_post_v1_11_0_release_priority_selection_20260803.py",
                "data/reporting/post_v1_11_0_release_priority_selection_review.json",
                "data/reporting/post_v1_11_0_release_priority_selection_review.md",
                "project/packages/post-v1.11.0-release-priority-selection-review-20260803.md",
                "tests/test_post_v1_11_0_release_priority_selection_20260803.py",
                "project/state.json",
                "project/STATE_SUMMARY.md",
            }
            self.assertTrue(required.issubset(manifest))



if __name__ == "__main__":
    unittest.main()
