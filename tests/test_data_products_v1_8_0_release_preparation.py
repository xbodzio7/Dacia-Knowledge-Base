from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "reporting" / "data_products_v1_8_0_release_preparation.json"
STATE = ROOT / "project" / "state.json"
VERIFIER = ROOT / "tools" / "review_data_products_v1_8_0_release_preparation_20260726.py"
TARGET_RELEASE = ROOT / "project" / "releases" / "data-products-v1.8.0.md"


class DataProductsV180ReleasePreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_metadata_target_and_selection_source(self) -> None:
        self.assertEqual(self.report["version"], 1)
        self.assertEqual(
            self.report["kind"],
            "data_products_v1_8_0_release_preparation",
        )
        self.assertEqual(self.report["prepared_on"], "2026-07-26")
        self.assertEqual(self.report["status"], "complete")
        self.assertEqual(
            self.report["selected_by"],
            "post_cross_model_priority_selection_review.json",
        )
        target = self.report["target"]
        self.assertEqual(target["version"], "1.8.0")
        self.assertEqual(target["tag"], "data-products-v1.8.0")
        self.assertEqual(
            target["archive_name"],
            "dacia-knowledge-base-data-products-v1.8.0.zip",
        )

    def test_public_baseline_is_exact_immutable_v1_7_0(self) -> None:
        public = self.report["public_baseline"]
        self.assertEqual(public["version"], "1.7.0")
        self.assertEqual(public["tag"], "data-products-v1.7.0")
        self.assertEqual(public["release_id"], 360090447)
        self.assertEqual(
            public["source_commit"],
            "99e0e19b86cad6eae619f37702464e6a5a761cd8",
        )
        self.assertEqual(public["archive_members"], 83)
        self.assertEqual(public["verification"], "PASS")

    def test_candidate_baseline_adds_only_two_cross_model_members(self) -> None:
        candidate = self.report["candidate_baseline"]
        self.assertEqual(candidate["selected_configuration_count"], 72)
        self.assertEqual(candidate["scope_group_count"], 19)
        self.assertEqual(candidate["comparable_scope_count"], 19)
        self.assertEqual(candidate["singleton_scope_count"], 0)
        self.assertEqual(candidate["within_scope_pair_count"], 114)
        self.assertEqual(candidate["recorded_difference_count"], 1695)
        self.assertEqual(candidate["archive_member_count"], 85)
        self.assertEqual(
            candidate["new_members_since_public_baseline"],
            [
                "cross-model/cross-model-comparison-view.json",
                "cross-model/cross-model-comparison-view.html",
            ],
        )
        self.assertEqual(
            candidate["semantic_boundaries"],
            {
                "cross_scope_pairs_generated": False,
                "ranking_generated": False,
                "recommendations_generated": False,
                "inferred_values_generated": False,
            },
        )

    def test_cross_model_contract_preserves_navigation_and_unknowns(self) -> None:
        contract = self.report["cross_model_product_contract"]
        self.assertEqual(contract["model_family_count"], 5)
        self.assertEqual(contract["reporting_scope_count"], 19)
        self.assertEqual(contract["active_configuration_count"], 72)
        self.assertEqual(contract["within_scope_pair_count"], 114)
        self.assertEqual(contract["json_comparison_paths"], 76)
        self.assertEqual(contract["json_navigation_paths"], 2)
        self.assertEqual(contract["html_local_file_links"], 57)
        self.assertTrue(contract["standalone_html"])
        self.assertFalse(contract["javascript_used"])
        self.assertFalse(contract["runtime_image_dependency"])
        self.assertEqual(
            contract["unknown_seat_models"],
            ["bigster", "duster_iii"],
        )
        self.assertEqual(contract["unknown_state"], "not_stated")

    def test_release_lifecycle_requires_separate_exact_preflight(self) -> None:
        self.assertEqual(
            self.report["publication_lifecycle"],
            [
                "preflight",
                "publish",
                "independent_public_audit",
                "record_publication",
            ],
        )
        preflight = self.report["preflight_contract"]
        self.assertEqual(preflight["source"], "exact squash-merged preparation commit")
        self.assertEqual(preflight["build_count"], 2)
        self.assertIn("byte_identical_rebuilds", preflight["required_checks"])
        self.assertIn("cross_model_html_verification", preflight["required_checks"])
        self.assertIn("archive_sha256", preflight["final_identity_fields"])

    def test_preparation_does_not_publish_or_guess_final_identity(self) -> None:
        publication = self.report["publication_state"]
        self.assertFalse(publication["publication_performed"])
        self.assertFalse(publication["tag_created"])
        self.assertFalse(publication["release_created"])
        self.assertIsNone(publication["final_source_commit"])
        self.assertIsNone(publication["final_asset_identity"])
        self.assertIn("not the final squash-merged", publication["reason"])

    def test_non_goals_and_next_package_are_explicit(self) -> None:
        self.assertEqual(
            self.report["non_goals"],
            [
                "new_data_imports",
                "cross_model_ui_expansion",
                "ranking",
                "recommendations",
                "cross_scope_pair_generation",
                "inferred_values",
                "rewriting_public_v1_7_0_assets",
            ],
        )
        self.assertEqual(
            self.report["next_package"]["name"],
            "Data Products v1.8.0 Preflight",
        )
        baseline = self.report["repository_baseline"]
        self.assertEqual(baseline["tests"], 1014)
        self.assertEqual(baseline["rows"], 9688)
        self.assertEqual(baseline["configuration_values"], 2949)
        self.assertEqual(baseline["configuration_value_ranges"], 244)
        self.assertEqual(baseline["availability_records"], 4754)
        self.assertEqual(baseline["attributes"], 385)

    def test_verifier_and_project_state_preserve_preparation_history(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VERIFIER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("PASS: Data Products v1.8.0 release preparation", completed.stdout)
        state = json.loads(STATE.read_text(encoding="utf-8"))
        self.assertTrue(state["phase"])
        self.assertTrue(state["current_package"]["name"])
        self.assertIn(state["current_package"]["status"], {"planned", "active", "blocked", "complete"})
        self.assertTrue(state["next_package"]["name"])
        self.assertGreaterEqual(state["baseline"]["tests"], 1014)
        self.assertGreaterEqual(state["baseline"]["rows"], 9688)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2949)
        self.assertGreaterEqual(state["baseline"]["configuration_value_ranges"], 244)
        self.assertGreaterEqual(state["baseline"]["availability_records"], 4754)
        self.assertGreaterEqual(state["baseline"]["attributes"], 385)

if __name__ == "__main__":
    unittest.main()
