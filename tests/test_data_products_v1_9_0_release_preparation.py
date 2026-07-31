from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "reporting" / "data_products_v1_9_0_release_preparation.json"
STATE = ROOT / "project" / "state.json"
VERIFIER = ROOT / "tools" / "review_data_products_v1_9_0_release_preparation_20260731.py"
NEW_CONFIGURATIONS = {
    "sandero_iii_essential_tce100_manual",
    "sandero_iii_expression_tce100_manual",
    "sandero_iii_journey_tce100_manual",
    "sandero_stepway_iii_essential_tce110_manual",
    "sandero_stepway_iii_expression_tce110_manual",
    "sandero_stepway_iii_extreme_tce110_manual",
}


class DataProductsV190ReleasePreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_metadata_target_and_public_baseline(self) -> None:
        self.assertEqual(self.report["version"], 1)
        self.assertEqual(
            self.report["kind"],
            "data_products_v1_9_0_release_preparation",
        )
        self.assertEqual(self.report["prepared_on"], "2026-07-31")
        self.assertEqual(self.report["status"], "complete")
        self.assertEqual(
            self.report["selected_by"],
            "sandero_page17_power_torque_rpm_range_import_closure.json",
        )
        self.assertEqual(
            self.report["target"],
            {
                "version": "1.9.0",
                "tag": "data-products-v1.9.0",
                "archive_name": "dacia-knowledge-base-data-products-v1.9.0.zip",
                "manifest_name": "data-product-release-manifest.json",
                "checksums_name": "SHA256SUMS",
            },
        )
        public = self.report["public_baseline"]
        self.assertEqual(public["version"], "1.8.1")
        self.assertEqual(public["release_id"], 360138130)
        self.assertEqual(
            public["source_commit"],
            "0b7009fd1950693e347638a6b96756aeefb43b8a",
        )
        self.assertEqual(public["archive_members"], 85)
        self.assertEqual(public["verification"], "PASS")

    def test_candidate_baseline_records_minor_release_expansion(self) -> None:
        candidate = self.report["candidate_baseline"]
        self.assertEqual(candidate["selected_configuration_count"], 78)
        self.assertEqual(candidate["scope_group_count"], 20)
        self.assertEqual(candidate["comparable_scope_count"], 20)
        self.assertEqual(candidate["singleton_scope_count"], 0)
        self.assertEqual(candidate["within_scope_pair_count"], 129)
        self.assertEqual(candidate["recorded_difference_count"], 2180)
        self.assertEqual(candidate["archive_member_count"], 89)
        self.assertEqual(candidate["technical_comparison_facet_count"], 127)
        self.assertEqual(candidate["equipment_facet_count"], 110)
        self.assertTrue(candidate["member_set_change_since_public_baseline"])
        boundaries = candidate["semantic_boundaries"]
        self.assertTrue(boundaries["new_source_backed_configurations"])
        self.assertTrue(boundaries["new_reporting_scope"])
        self.assertTrue(boundaries["new_within_scope_pairs"])
        self.assertFalse(boundaries["cross_scope_pairs_generated"])
        self.assertFalse(boundaries["ranking_generated"])
        self.assertFalse(boundaries["recommendations_generated"])
        self.assertFalse(boundaries["inferred_values_generated"])

    def test_release_delta_names_exact_new_configurations_and_scope(self) -> None:
        delta = self.report["release_delta"]
        self.assertEqual(set(delta["new_configuration_codes"]), NEW_CONFIGURATIONS)
        self.assertEqual(
            delta["new_reporting_scope"],
            "sandero_tce100_stepway_tce110_manual",
        )
        self.assertEqual(delta["selected_configuration_delta"], 6)
        self.assertEqual(delta["scope_group_delta"], 1)
        self.assertEqual(delta["within_scope_pair_delta"], 15)
        self.assertEqual(delta["recorded_difference_delta"], 485)
        self.assertEqual(delta["archive_member_delta"], 4)
        self.assertEqual(delta["technical_comparison_facet_delta"], 3)
        self.assertEqual(delta["equipment_facet_delta"], 0)
        self.assertEqual(
            delta["repository_data_delta"],
            {
                "master_rows": 1692,
                "configuration_values": 549,
                "configuration_value_ranges": 54,
                "availability_records": 1016,
            },
        )

    def test_shortlist_contract_preserves_filter_and_price_semantics(self) -> None:
        shortlist = self.report["shortlist_contract"]
        self.assertEqual(shortlist["active_configuration_count"], 78)
        self.assertEqual(shortlist["equipment_facet_count"], 110)
        self.assertEqual(shortlist["visible_equipment_choices"], 108)
        self.assertEqual(shortlist["rear_view_camera_matches"], 71)
        self.assertTrue(shortlist["missing_and_unknown_are_exclusions"])
        self.assertEqual(
            [item["model_code"] for item in shortlist["model_order"]],
            [
                "sandero_iii",
                "sandero_stepway_iii",
                "jogger",
                "duster_iii",
                "bigster",
            ],
        )
        self.assertEqual(
            [
                item["minimum_catalog_price_pln"]
                for item in shortlist["model_order"]
            ],
            [63900, 71700, 77900, 82000, 101400],
        )

    def test_release_notes_contract_describes_exact_candidate(self) -> None:
        contract = self.report["release_notes_contract"]
        self.assertEqual(contract["headline"], "Data Products v1.9.0")
        statements = contract["must_state"]
        self.assertIn(
            "six new source-backed Sandero and Sandero Stepway manual configurations",
            statements,
        )
        self.assertIn("78 active configurations in 20 independent scopes", statements)
        self.assertIn("129 within-scope pairs and 2180 recorded differences", statements)
        self.assertIn("89 deterministic archive members", statements)
        self.assertIn(
            "no cross-scope pairs, ranking, recommendations or inferred values",
            statements,
        )
        self.assertIn(
            "public data-products-v1.8.1 remains immutable",
            statements,
        )

    def test_preparation_requires_separate_preflight_and_does_not_publish(self) -> None:
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
        self.assertIn("byte_identical_rebuilds", preflight["required_checks"])
        self.assertIn(
            "public_v1_8_1_control_download",
            preflight["required_checks"],
        )
        publication = self.report["publication_state"]
        self.assertFalse(publication["publication_performed"])
        self.assertFalse(publication["tag_created"])
        self.assertFalse(publication["release_created"])
        self.assertIsNone(publication["final_source_commit"])
        self.assertIsNone(publication["final_asset_identity"])

    def test_repository_baseline_and_next_package_are_exact(self) -> None:
        baseline = self.report["repository_baseline"]
        self.assertEqual(baseline["tests"], 1684)
        self.assertEqual(baseline["csv_files"], 46)
        self.assertEqual(baseline["rows"], 11380)
        self.assertEqual(baseline["configuration_values"], 3498)
        self.assertEqual(baseline["configuration_import_specs"], 138)
        self.assertEqual(baseline["configuration_value_ranges"], 298)
        self.assertEqual(baseline["configuration_range_import_specs"], 24)
        self.assertEqual(baseline["availability_records"], 5770)
        self.assertEqual(baseline["attributes"], 385)
        self.assertEqual(baseline["attribute_categories"], 30)
        self.assertEqual(
            self.report["next_package"]["name"],
            "Data Products v1.9.0 Preflight",
        )

    def test_verifier_and_project_state_accept_preparation(self) -> None:
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
            "PASS: Data Products v1.9.0 release preparation",
            completed.stdout,
        )
        state = json.loads(STATE.read_text(encoding="utf-8"))
        self.assertEqual(
            state["current_package"]["name"],
            "Data Products v1.9.0 Release Preparation",
        )
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(
            state["next_package"]["name"],
            "Data Products v1.9.0 Preflight",
        )
        self.assertGreaterEqual(state["baseline"]["tests"], 1684)


if __name__ == "__main__":
    unittest.main()
