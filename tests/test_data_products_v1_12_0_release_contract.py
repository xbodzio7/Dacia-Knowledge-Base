from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]

import sys
sys.path.insert(0, str(ROOT / "tools"))

from reporting.data_product_release_model import archive_name, verify_release_assets  # noqa: E402
from reporting.portfolio_model_family_release_integration import create_release_assets  # noqa: E402


class DataProductsV112AcceleratedReleaseContractTest(unittest.TestCase):
    VERSION = "1.12.0"
    COMMIT = "2" * 40

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.first = cls.root / "first"
        cls.second = cls.root / "second"
        cls.first_manifest = create_release_assets(ROOT, cls.first, cls.VERSION, cls.COMMIT)
        cls.second_manifest = create_release_assets(ROOT, cls.second, cls.VERSION, cls.COMMIT)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_accelerated_release_policy_is_enabled(self) -> None:
        state = json.loads((ROOT / "project/state.json").read_text(encoding="utf-8"))
        policy = state["execution_policy"]
        self.assertTrue(policy["release_double_build_required"])
        self.assertTrue(policy["release_exact_source_sha_required"])
        self.assertTrue(policy["full_quality_on_final_head"])

    def test_v1_12_0_notes_describe_the_family_product(self) -> None:
        archive = self.first / archive_name(self.VERSION)
        with ZipFile(archive) as handle:
            notes = handle.read("RELEASE_NOTES.md").decode("utf-8")
        for expected in (
            "v1.12.0 portfolio model-family product",
            "six canonical families",
            "81 active",
            "22 existing reporting scopes",
            "251 explicit",
            "data-products-v1.11.0",
            "exact publication merge SHA",
        ):
            self.assertIn(expected, notes)

    def test_release_contains_the_three_family_outputs(self) -> None:
        archive = self.first / archive_name(self.VERSION)
        with ZipFile(archive) as handle:
            names = set(handle.namelist())
        self.assertTrue(
            {
                "model-families/portfolio_model_family_summary.json",
                "model-families/portfolio_model_family_summary.md",
                "model-families/portfolio_model_family_summary.html",
            }.issubset(names)
        )

    def test_double_build_is_byte_identical(self) -> None:
        self.assertEqual(self.first_manifest, self.second_manifest)
        for name in (
            archive_name(self.VERSION),
            "data-product-release-manifest.json",
            "SHA256SUMS",
        ):
            self.assertEqual(
                (self.first / name).read_bytes(),
                (self.second / name).read_bytes(),
            )

    def test_both_builds_pass_canonical_verification(self) -> None:
        self.assertEqual(verify_release_assets(self.first), self.first_manifest)
        self.assertEqual(verify_release_assets(self.second), self.second_manifest)


if __name__ == "__main__":
    unittest.main()
