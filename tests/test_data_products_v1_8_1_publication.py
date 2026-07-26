from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLICATION = ROOT / ".github" / "data-products-v1.8.1-publication.json"
AUDIT = ROOT / "data" / "reporting" / "data_products_v1_8_1_publication_audit.json"
RELEASE_RECORD = ROOT / "project" / "releases" / "data-products-v1.8.1.md"
STATE = ROOT / "project" / "state.json"
VERIFIER = ROOT / "tools" / "review_data_products_v1_8_1_publication_20260727.py"
SOURCE_COMMIT = "0b7009fd1950693e347638a6b96756aeefb43b8a"


class DataProductsV181PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.publication = json.loads(PUBLICATION.read_text(encoding="utf-8"))
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))

    def test_publication_identity_is_exact(self) -> None:
        self.assertEqual(self.publication["kind"], "data_products_v1_8_1_publication")
        self.assertEqual(self.publication["status"], "PASS")
        self.assertEqual(self.publication["release_id"], 360138130)
        self.assertEqual(self.publication["release_tag"], "data-products-v1.8.1")
        self.assertEqual(self.publication["source_commit"], SOURCE_COMMIT)
        self.assertFalse(self.publication["draft"])
        self.assertFalse(self.publication["prerelease"])
        self.assertEqual(self.publication["asset_count"], 3)

    def test_public_assets_match_preflight_identity(self) -> None:
        expected = {
            "dacia-knowledge-base-data-products-v1.8.1.zip": (490767591, 62141954, "3bb8ba7c48195651bbe24cae042560273c5e4083467c01b203bb07dab7401bc5"),
            "data-product-release-manifest.json": (490767592, 20607, "f4ed40ed7e469876c80ee95c6b1ad18fcf6c86f215934ab5942373f2889a54fd"),
            "SHA256SUMS": (490767593, 213, "ca59fb187c8fbdcbacf7c62d0c65559a8f604defc5634b1d7fe257df7f7e668e"),
        }
        self.assertEqual(set(self.publication["assets"]), set(expected))
        for name, (asset_id, size, digest) in expected.items():
            item = self.publication["assets"][name]
            self.assertEqual(item["asset_id"], asset_id)
            self.assertEqual(item["size_bytes"], size)
            self.assertEqual(item["sha256"], digest)
            self.assertEqual(item["api_digest"], "sha256:" + digest)
        self.assertEqual(self.publication["public_redownload_verification"], "PASS")

    def test_independent_public_audit_is_exact(self) -> None:
        self.assertEqual(self.audit["kind"], "data_products_v1_8_1_public_audit")
        self.assertEqual(self.audit["status"], "PASS")
        self.assertEqual(self.audit["release_id"], 360138130)
        self.assertEqual(self.audit["source_commit"], SOURCE_COMMIT)
        self.assertEqual(self.audit["publication_workflow_run"], 30224467755)
        self.assertEqual(self.audit["audit_workflow_run"], 30225040623)
        self.assertEqual(self.audit["verification"], "PASS")

    def test_public_workspace_and_release_contents_are_exact(self) -> None:
        self.assertEqual(self.audit["workspace"]["asset_count"], 3)
        self.assertEqual(self.audit["workspace"]["content_file_count"], 85)
        self.assertEqual(self.audit["workspace"]["index_local_link_count"], 83)
        self.assertEqual(self.audit["workspace"]["index_sha256"], "653a505102a15dc66d770b82612e18da324c0299162f644b7192628911c54b80")
        contents = self.audit["release_contents"]
        self.assertEqual(contents["selected_configuration_count"], 72)
        self.assertEqual(contents["scope_group_count"], 19)
        self.assertEqual(contents["within_scope_pair_count"], 114)
        self.assertEqual(contents["archive_member_count"], 85)
        self.assertEqual(contents["equipment_facet_count"], 110)

    def test_public_filter_and_model_order_are_exact(self) -> None:
        equipment = self.audit["equipment_filter"]
        self.assertEqual(equipment["visible_choices"], 108)
        self.assertEqual(equipment["camera_matches"], 66)
        self.assertTrue(equipment["missing_and_unknown_are_exclusions"])
        self.assertEqual(
            [item["model_code"] for item in self.audit["model_order"]],
            ["sandero_iii", "sandero_stepway_iii", "jogger", "duster_iii", "bigster"],
        )
        self.assertEqual(
            [item["minimum_catalog_price_pln"] for item in self.audit["model_order"]],
            [68000, 71700, 77900, 82000, 101400],
        )

    def test_cross_model_and_semantic_boundaries_are_preserved(self) -> None:
        cross_model = self.audit["cross_model"]
        self.assertEqual(cross_model["model_family_count"], 5)
        self.assertEqual(cross_model["reporting_scope_count"], 19)
        self.assertEqual(cross_model["active_configuration_count"], 72)
        self.assertEqual(cross_model["comparison_path_count"], 76)
        self.assertEqual(cross_model["navigation_path_count"], 2)
        self.assertEqual(cross_model["html_local_file_link_count"], 57)
        self.assertEqual(cross_model["unknown_seat_models"], ["bigster", "duster_iii"])
        self.assertEqual(cross_model["unknown_state"], "not_stated")
        self.assertTrue(all(value is False for value in self.audit["semantic_boundaries"].values()))

    def test_release_record_and_project_state_are_complete(self) -> None:
        record = RELEASE_RECORD.read_text(encoding="utf-8")
        for value in (
            "Release ID: `360138130`",
            SOURCE_COMMIT,
            "62,141,954 bytes",
            "30225040623",
            "Publication audit result: `PASS`",
        ):
            self.assertIn(value, record)
        state = json.loads(STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["phase"], "Data Products v1.8.1 Publication")
        self.assertEqual(state["current_package"]["name"], "Data Products v1.8.1 Publication")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(state["next_package"]["name"], "Cross-Model Navigation Usability Review")
        self.assertEqual(state["baseline"]["tests"], 1054)

    def test_publication_verifier_accepts_record(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VERIFIER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("PASS: Data Products v1.8.1 publication", completed.stdout)


if __name__ == "__main__":
    unittest.main()
