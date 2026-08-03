from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

REPOSITORY = Path(__file__).resolve().parents[1]

import sys
sys.path.insert(0, str(REPOSITORY / "tools"))

import data_product_release as release_cli  # noqa: E402
from reporting.data_product_release_model import (  # noqa: E402
    archive_name,
    verify_release_assets,
)
from reporting.portfolio_model_family_release_integration import (  # noqa: E402
    FAMILY_FILES,
    FAMILY_HTML_HREF,
    create_release_assets,
)


class PortfolioModelFamilyReleaseIntegrationTests(unittest.TestCase):
    COMMIT = "1" * 40
    VERSION = "9.9.9"

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.output = cls.root / "release"
        cls.manifest = create_release_assets(
            REPOSITORY,
            cls.output,
            cls.VERSION,
            cls.COMMIT,
        )
        cls.archive = cls.output / archive_name(cls.VERSION)
        with ZipFile(cls.archive) as handle:
            cls.names = handle.namelist()
            cls.contents = {
                name: handle.read(name)
                for name in cls.names
                if name.startswith("model-families/")
                or name == "cross-model/cross-model-comparison-view.html"
            }

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_manifest_declares_integrated_family_product(self) -> None:
        self.assertIs(self.manifest["portfolio_model_family_summary_generated"], True)
        self.assertEqual(
            self.manifest["portfolio_model_family_summary_formats"],
            ["JSON", "Markdown", "HTML"],
        )
        self.assertEqual(
            self.manifest["portfolio_model_family_summary_directory"],
            "model-families",
        )

    def test_archive_contains_all_three_verified_family_outputs(self) -> None:
        expected = {
            f"model-families/{name}"
            for name in FAMILY_FILES
        }
        self.assertTrue(expected.issubset(set(self.names)))
        for name in FAMILY_FILES:
            archived = self.contents[f"model-families/{name}"]
            committed = (REPOSITORY / "data" / "reporting" / name).read_bytes()
            self.assertEqual(archived, committed)

    def test_family_json_preserves_scope_and_provenance_boundaries(self) -> None:
        payload = json.loads(
            self.contents[
                "model-families/portfolio_model_family_summary.json"
            ]
        )
        summary = payload["summary"]
        self.assertEqual(summary["model_family_count"], 6)
        self.assertEqual(summary["active_configuration_count"], 81)
        self.assertEqual(summary["reporting_scope_count"], 22)
        self.assertEqual(summary["source_configuration_relationship_count"], 251)
        self.assertEqual(summary["configurations_without_provenance_count"], 0)
        self.assertFalse(summary["cross_scope_pairs_generated"])
        self.assertFalse(summary["ranking_generated"])
        self.assertFalse(summary["recommendations_generated"])
        self.assertFalse(summary["inferred_values_generated"])

    def test_cross_model_html_links_to_offline_family_summary(self) -> None:
        html = self.contents[
            "cross-model/cross-model-comparison-view.html"
        ].decode("utf-8")
        self.assertEqual(html.count(FAMILY_HTML_HREF), 1)
        self.assertIn("exact source provenance", html)

    def test_integrated_assets_pass_canonical_release_verification(self) -> None:
        self.assertEqual(verify_release_assets(self.output), self.manifest)

    def test_double_build_is_byte_identical(self) -> None:
        second = self.root / "second"
        second_manifest = create_release_assets(
            REPOSITORY,
            second,
            self.VERSION,
            self.COMMIT,
        )
        self.assertEqual(second_manifest, self.manifest)
        for name in (
            archive_name(self.VERSION),
            "data-product-release-manifest.json",
            "SHA256SUMS",
        ):
            self.assertEqual(
                (self.output / name).read_bytes(),
                (second / name).read_bytes(),
            )

    def test_cli_build_uses_the_integrated_release_path(self) -> None:
        output = self.root / "cli"
        result = release_cli.main(
            [
                "--version",
                self.VERSION,
                "--commit-sha",
                self.COMMIT,
                "--output-directory",
                str(output),
            ],
            repository=REPOSITORY,
        )
        self.assertEqual(result, 0)
        manifest = verify_release_assets(output)
        self.assertIs(manifest["portfolio_model_family_summary_generated"], True)


if __name__ == "__main__":
    unittest.main()
