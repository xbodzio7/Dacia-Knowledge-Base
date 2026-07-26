from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "reporting" / "data_products_v1_8_1_release_preparation.json"
STATE = ROOT / "project" / "state.json"
VERIFIER = ROOT / "tools" / "review_data_products_v1_8_1_release_preparation_20260727.py"
TARGET_RELEASE = ROOT / "project" / "releases" / "data-products-v1.8.1.md"


class DataProductsV181ReleasePreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_metadata_target_and_selection_source(self) -> None:
        self.assertEqual(self.report["version"], 1)
        self.assertEqual(
            self.report["kind"],
            "data_products_v1_8_1_release_preparation",
        )
        self.assertEqual(self.report["prepared_on"], "2026-07-27")
        self.assertEqual(self.report["status"], "complete")
        self.assertEqual(
            self.report["selected_by"],
            "equipment_filter_regression_model_price_order.json",
        )
        target = self.report["target"]
        self.assertEqual(target["version"], "1.8.1")
        self.assertEqual(target["tag"], "data-products-v1.8.1")
        self.assertEqual(
            target["archive_name"],
            "dacia-knowledge-base-data-products-v1.8.1.zip",
        )

    def test_public_baseline_is_exact_immutable_v1_8_0(self) -> None:
        public = self.report["public_baseline"]
        self.assertEqual(public["version"], "1.8.0")
        self.assertEqual(public["tag"], "data-products-v1.8.0")
        self.assertEqual(public["release_id"], 360115681)
        self.assertEqual(
            public["source_commit"],
            "becd218228e3f4f0cdd312b0ed836ade487422b1",
        )
        self.assertEqual(public["archive_members"], 85)
        self.assertEqual(public["verification"], "PASS")

    def test_candidate_preserves_member_set_and_data_boundaries(self) -> None:
        candidate = self.report["candidate_baseline"]
        self.assertEqual(candidate["selected_configuration_count"], 72)
        self.assertEqual(candidate["scope_group_count"], 19)
        self.assertEqual(candidate["comparable_scope_count"], 19)
        self.assertEqual(candidate["singleton_scope_count"], 0)
        self.assertEqual(candidate["within_scope_pair_count"], 114)
        self.assertEqual(candidate["recorded_difference_count"], 1695)
        self.assertEqual(candidate["archive_member_count"], 85)
        self.assertFalse(candidate["member_set_change_since_public_baseline"])
        self.assertTrue(
            all(
                value is False
                for value in candidate["semantic_boundaries"].values()
            )
        )

    def test_patch_contract_records_filtering_and_missing_data_semantics(self) -> None:
        patch = self.report["patch_contract"]
        self.assertEqual(patch["active_configuration_count"], 72)
        self.assertEqual(patch["equipment_facet_count"], 110)
        self.assertEqual(patch["visible_equipment_choices"], 108)
        self.assertEqual(patch["camera_search_visible_choices"], 1)
        self.assertEqual(patch["rear_view_camera_matches"], 66)
        self.assertEqual(patch["selection_count_after_camera_click"], 1)
        self.assertTrue(patch["missing_and_unknown_are_exclusions"])

    def test_model_choices_are_ordered_by_minimum_catalog_price(self) -> None:
        order = self.report["patch_contract"]["model_order"]
        self.assertEqual(
            [item["model_code"] for item in order],
            [
                "sandero_iii",
                "sandero_stepway_iii",
                "jogger",
                "duster_iii",
                "bigster",
            ],
        )
        self.assertEqual(
            [item["minimum_catalog_price_pln"] for item in order],
            [68000, 71700, 77900, 82000, 101400],
        )

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
        self.assertEqual(
            preflight["source"],
            "exact squash-merged preparation commit",
        )
        self.assertEqual(preflight["build_count"], 2)
        self.assertIn(
            "real_chromium_filtering_smoke",
            preflight["required_checks"],
        )
        self.assertIn("archive_sha256", preflight["final_identity_fields"])

    def test_preparation_does_not_publish_and_defines_next_package(self) -> None:
        publication = self.report["publication_state"]
        self.assertFalse(publication["publication_performed"])
        self.assertFalse(publication["tag_created"])
        self.assertFalse(publication["release_created"])
        self.assertIsNone(publication["final_source_commit"])
        self.assertIsNone(publication["final_asset_identity"])
        self.assertFalse(TARGET_RELEASE.exists())
        self.assertEqual(
            self.report["next_package"]["name"],
            "Data Products v1.8.1 Preflight",
        )
        baseline = self.report["repository_baseline"]
        self.assertEqual(baseline["tests"], 1038)
        self.assertEqual(baseline["rows"], 9688)
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
        self.assertEqual(
            completed.returncode,
            0,
            completed.stderr or completed.stdout,
        )
        self.assertIn(
            "PASS: Data Products v1.8.1 release preparation",
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
        self.assertGreaterEqual(state["baseline"]["tests"], 1038)


if __name__ == "__main__":
    unittest.main()
