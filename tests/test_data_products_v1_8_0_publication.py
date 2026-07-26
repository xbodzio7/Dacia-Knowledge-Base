from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "reporting" / "data_products_v1_8_0_publication_audit.json"
RELEASE = ROOT / "project" / "releases" / "data-products-v1.8.0.md"
STATE = ROOT / "project" / "state.json"
VERIFIER = ROOT / "tools" / "review_data_products_v1_8_0_publication_20260726.py"


class DataProductsV180PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))

    def test_release_identity_and_workflow_evidence(self) -> None:
        self.assertEqual(self.audit["version"], 1)
        self.assertEqual(
            self.audit["kind"],
            "data_products_v1_8_0_publication_audit",
        )
        self.assertEqual(self.audit["status"], "PASS")
        release = self.audit["release"]
        self.assertEqual(release["version"], "1.8.0")
        self.assertEqual(release["tag"], "data-products-v1.8.0")
        self.assertEqual(release["release_id"], 360115681)
        self.assertEqual(
            release["source_commit"],
            "becd218228e3f4f0cdd312b0ed836ade487422b1",
        )
        self.assertFalse(release["draft"])
        self.assertFalse(release["prerelease"])
        workflow = self.audit["workflow_evidence"]
        self.assertEqual(workflow["preparation_pull_request"], 284)
        self.assertEqual(workflow["preflight_run"], 30219704364)
        self.assertEqual(workflow["publication_run"], 30219809423)
        self.assertEqual(workflow["independent_audit_run"], 30220008441)

    def test_three_assets_have_exact_ids_sizes_and_hashes(self) -> None:
        assets = self.audit["assets"]
        self.assertEqual(set(assets), {
            "dacia-knowledge-base-data-products-v1.8.0.zip",
            "data-product-release-manifest.json",
            "SHA256SUMS",
        })
        expected = {
            "dacia-knowledge-base-data-products-v1.8.0.zip": (
                490686120,
                62141187,
                "2af02fc148446eb3789ed4e19f32c52e54c484464ca1cdb2ba1048ae02b7cec9",
            ),
            "data-product-release-manifest.json": (
                490686121,
                20606,
                "af9366e92543a8aadca5e0a94a43391d202bce71f684bf3d9583913764f0de3b",
            ),
            "SHA256SUMS": (
                490686122,
                213,
                "8649769104a5b695c2b6e21177c032523fdc0a694ea11931ce95a6a5ae428596",
            ),
        }
        for name, values in expected.items():
            record = assets[name]
            self.assertEqual(record["asset_id"], values[0])
            self.assertEqual(record["size_bytes"], values[1])
            self.assertEqual(record["sha256"], values[2])
            self.assertEqual(record["api_digest"], "sha256:" + values[2])

    def test_release_contents_preserve_scope_safe_counts(self) -> None:
        contents = self.audit["release_contents"]
        self.assertEqual(contents["selected_configuration_count"], 72)
        self.assertEqual(contents["scope_group_count"], 19)
        self.assertEqual(contents["comparable_scope_count"], 19)
        self.assertEqual(contents["singleton_scope_count"], 0)
        self.assertEqual(contents["within_scope_pair_count"], 114)
        self.assertEqual(contents["recorded_difference_count"], 1695)
        self.assertEqual(contents["archive_member_count"], 85)
        self.assertEqual(contents["technical_comparison_facet_count"], 124)
        self.assertEqual(contents["equipment_facet_count"], 110)

    def test_cross_model_product_is_published_without_inference(self) -> None:
        product = self.audit["cross_model_product"]
        self.assertEqual(product["model_family_count"], 5)
        self.assertEqual(product["reporting_scope_count"], 19)
        self.assertEqual(product["active_configuration_count"], 72)
        self.assertEqual(product["within_scope_pair_count"], 114)
        self.assertEqual(product["comparison_path_count"], 76)
        self.assertEqual(product["navigation_path_count"], 2)
        self.assertEqual(product["html_local_file_link_count"], 57)
        self.assertTrue(product["standalone_html"])
        self.assertFalse(product["javascript_used"])
        self.assertFalse(product["runtime_image_dependency"])
        self.assertEqual(
            product["unknown_seat_models"],
            ["bigster", "duster_iii"],
        )
        self.assertEqual(product["unknown_state"], "not_stated")

    def test_workspace_distinguishes_content_and_index_links(self) -> None:
        workspace = self.audit["offline_workspace"]
        self.assertEqual(workspace["verification"], "PASS")
        self.assertEqual(workspace["asset_count"], 3)
        self.assertEqual(workspace["content_file_count"], 85)
        self.assertEqual(workspace["index_local_link_count"], 83)
        self.assertEqual(
            workspace["index_sha256"],
            "ad2074a55e110ac11a518b441cbdc51864d5c7223cba75812c5b719facdf9b24",
        )
        self.assertIn("four primary product links", workspace["index_link_explanation"])
        self.assertIn("next usability review", workspace["index_link_explanation"])

    def test_semantic_boundaries_and_verification_all_pass(self) -> None:
        self.assertEqual(
            self.audit["semantic_boundaries"],
            {
                "cross_scope_pairs_generated": False,
                "ranking_generated": False,
                "recommendations_generated": False,
                "inferred_values_generated": False,
                "public_v1_7_0_rewritten": False,
            },
        )
        self.assertTrue(
            all(value == "PASS" for value in self.audit["verification"].values())
        )

    def test_release_record_is_durable_and_immutable(self) -> None:
        text = RELEASE.read_text(encoding="utf-8")
        self.assertIn("Data Products v1.8.0 Publication", text)
        self.assertIn("360115681", text)
        self.assertIn("62,141,187 bytes", text)
        self.assertIn("85 deterministic archive members", text)
        self.assertIn("83 local links", text)
        self.assertIn("must not replace or rewrite `data-products-v1.8.0`", text)
        self.assertEqual(
            self.audit["next_package"]["name"],
            "Cross-Model Navigation Usability Review",
        )

    def test_verifier_and_project_state_preserve_publication_history(self) -> None:
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
            "PASS: Data Products v1.8.0 publication",
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
        self.assertGreaterEqual(state["baseline"]["tests"], 1022)


if __name__ == "__main__":
    unittest.main()
