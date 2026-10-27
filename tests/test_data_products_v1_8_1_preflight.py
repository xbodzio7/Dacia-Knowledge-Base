from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "reporting" / "data_products_v1_8_1_preflight.json"
STATE = ROOT / "project" / "state.json"
VERIFIER = ROOT / "tools" / "review_data_products_v1_8_1_preflight_20260727.py"
PUBLIC_RECORD = ROOT / "project" / "releases" / "data-products-v1.8.1.md"
SOURCE_COMMIT = "0b7009fd1950693e347638a6b96756aeefb43b8a"


class DataProductsV181PreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_metadata_and_exact_source_identity(self) -> None:
        self.assertEqual(self.report["version"], 1)
        self.assertEqual(self.report["kind"], "data_products_v1_8_1_preflight")
        self.assertEqual(self.report["verified_on"], "2026-07-27")
        self.assertEqual(self.report["status"], "PASS")
        self.assertEqual(self.report["source_commit"], SOURCE_COMMIT)
        self.assertEqual(self.report["release_version"], "1.8.1")
        self.assertEqual(self.report["release_tag"], "data-products-v1.8.1")

    def test_two_builds_are_byte_identical(self) -> None:
        self.assertEqual(self.report["build_count"], 2)
        self.assertTrue(self.report["byte_identical_rebuilds"])
        self.assertEqual(self.report["archive_member_count"], 85)
        self.assertEqual(self.report["duplicate_archive_members"], 0)

    def test_asset_identity_is_complete(self) -> None:
        assets = self.report["assets"]
        self.assertEqual(
            set(assets),
            {
                "dacia-knowledge-base-data-products-v1.8.1.zip",
                "data-product-release-manifest.json",
                "SHA256SUMS",
            },
        )
        for identity in assets.values():
            self.assertGreater(identity["size_bytes"], 0)
            self.assertEqual(len(identity["sha256"]), 64)

    def test_chromium_smoke_confirms_filtering(self) -> None:
        smoke = self.report["chromium_smoke"]
        self.assertEqual(smoke["visible_equipment_choices"], 108)
        self.assertEqual(smoke["camera_search_visible_choices"], 1)
        self.assertEqual(smoke["selection_count"], 1)
        self.assertEqual(smoke["matched_configurations"], 66)
        self.assertEqual(smoke["javascript_errors"], 0)

    def test_publication_controls_remain_non_destructive(self) -> None:
        controls = self.report["publication_controls"]
        self.assertTrue(controls["tag_absent"])
        self.assertTrue(controls["release_absent"])
        self.assertEqual(controls["public_v1_8_0_control_download"], "PASS")
        self.assertFalse(controls["publication_performed"])
        if PUBLIC_RECORD.exists():
            self.assertIn("Data Products v1.8.1 Publication", PUBLIC_RECORD.read_text(encoding="utf-8"))

    def test_semantic_boundaries_remain_unchanged(self) -> None:
        boundaries = self.report["semantic_boundaries"]
        self.assertEqual(
            boundaries,
            {
                "new_data_imports": False,
                "new_comparison_pairs": False,
                "cross_scope_pairs_generated": False,
                "ranking_generated": False,
                "recommendations_generated": False,
                "inferred_values_generated": False,
                "older_public_releases_rewritten": False,
            },
        )

    def test_next_package_requires_publication_action(self) -> None:
        self.assertEqual(
            self.report["next_package"]["name"],
            "Data Products v1.8.1 Publication",
        )
        state = json.loads(STATE.read_text(encoding="utf-8"))
        self.assertTrue(state["phase"])
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 1046)
        self.assertGreaterEqual(state["baseline"]["rows"], 9688)

    def test_verifier_accepts_preflight(self) -> None:
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
        self.assertIn("PASS: Data Products v1.8.1 preflight", completed.stdout)


if __name__ == "__main__":
    unittest.main()
