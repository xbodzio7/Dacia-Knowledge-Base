from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

REPOSITORY = Path(__file__).resolve().parents[1]

import sys
sys.path.insert(0, str(REPOSITORY / "tools"))

import data_product_release as release_cli  # noqa: E402
from reporting.data_product_release_download import (  # noqa: E402
    ASSETS_DIRECTORY_NAME,
    CONTENTS_DIRECTORY_NAME,
    _extract_verified_contents,
)
from reporting.data_product_release_model import (  # noqa: E402
    archive_name,
    verify_release_assets,
)
from reporting.data_product_workspace_index import (  # noqa: E402
    render_workspace_index,
    write_workspace_index,
)
from reporting.data_product_workspace_verify import verify_workspace  # noqa: E402
from reporting.portfolio_model_family_comparison_release_integration import (  # noqa: E402
    MATRIX_FILES as FAMILY_MATRIX_FILES,
    MATRIX_HTML as FAMILY_MATRIX_HTML,
)
from reporting.portfolio_model_family_release_integration import (  # noqa: E402
    FAMILY_FILES,
    FAMILY_HTML_HREF,
)
from reporting.portfolio_model_version_comparison_release_integration import (  # noqa: E402
    RELEASE_NOTES,
    VERSION_MATRIX_FILES,
    VERSION_MATRIX_HTML,
    create_release_assets,
)


class PortfolioModelFamilyReleaseIntegrationTests(unittest.TestCase):
    COMMIT = "1" * 40
    VERSION = "1.14.0"

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
                or name.startswith("model-versions/")
                or name == "cross-model/cross-model-comparison-view.html"
                or name == RELEASE_NOTES
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
        self.assertIs(
            self.manifest[
                "portfolio_model_family_comparison_matrix_generated"
            ],
            True,
        )
        self.assertEqual(
            self.manifest[
                "portfolio_model_family_comparison_matrix_formats"
            ],
            ["JSON", "CSV", "HTML"],
        )
        self.assertEqual(
            self.manifest[
                "portfolio_model_family_comparison_matrix_directory"
            ],
            "model-families",
        )
        self.assertIs(
            self.manifest[
                "portfolio_model_version_comparison_matrix_generated"
            ],
            True,
        )
        self.assertEqual(
            self.manifest[
                "portfolio_model_version_comparison_matrix_formats"
            ],
            ["JSON", "CSV", "HTML"],
        )
        self.assertEqual(
            self.manifest[
                "portfolio_model_version_comparison_matrix_directory"
            ],
            "model-versions",
        )

    def test_archive_contains_all_three_verified_family_outputs(self) -> None:
        family_names = FAMILY_FILES + FAMILY_MATRIX_FILES
        expected_family = {
            f"model-families/{name}"
            for name in family_names
        }
        expected_versions = {
            f"model-versions/{name}"
            for name in VERSION_MATRIX_FILES
        }
        self.assertTrue(
            (expected_family | expected_versions).issubset(set(self.names))
        )
        for name in family_names:
            archived = self.contents[f"model-families/{name}"]
            committed = (REPOSITORY / "data" / "reporting" / name).read_bytes()
            self.assertEqual(archived, committed)
        for name in VERSION_MATRIX_FILES:
            archived = self.contents[f"model-versions/{name}"]
            committed = (REPOSITORY / "data" / "reporting" / name).read_bytes()
            self.assertEqual(archived, committed)

        notes = self.contents[RELEASE_NOTES].decode("utf-8")
        self.assertEqual(
            notes.count("## v1.14.0 portfolio model-version comparison matrix"),
            1,
        )
        self.assertIn("model_version_comparison_matrix_html", notes)
        self.assertIn("Public `data-products-v1.13.0` remains immutable", notes)
        self.assertIn("built twice from the exact publication merge SHA", notes)

    def test_family_json_preserves_scope_and_provenance_boundaries(self) -> None:
        family_payload = json.loads(
            self.contents[
                "model-families/portfolio_model_family_summary.json"
            ]
        )
        family_summary = family_payload["summary"]
        family_matrix_payload = json.loads(
            self.contents[
                "model-families/portfolio_model_family_comparison_matrix.json"
            ]
        )
        family_matrix_summary = family_matrix_payload["summary"]
        version_matrix_payload = json.loads(
            self.contents[
                "model-versions/portfolio_model_version_comparison_matrix.json"
            ]
        )
        version_matrix_summary = version_matrix_payload["summary"]

        self.assertEqual(
            family_matrix_payload["source_product"],
            {
                "kind": "portfolio_model_family_summary",
                "version": 1,
                "path": "data/reporting/portfolio_model_family_summary.json",
            },
        )
        for summary in (
            family_summary,
            family_matrix_summary,
            version_matrix_summary,
        ):
            self.assertEqual(summary["model_family_count"], 6)
            self.assertEqual(summary["active_configuration_count"], 81)
            self.assertEqual(summary["reporting_scope_count"], 22)
            self.assertEqual(
                summary["source_configuration_relationship_count"], 251
            )
            self.assertEqual(
                summary["configurations_without_provenance_count"], 0
            )
            self.assertFalse(summary["cross_scope_pairs_generated"])
            self.assertFalse(summary["ranking_generated"])
            self.assertFalse(summary["recommendations_generated"])
            self.assertFalse(summary["inferred_values_generated"])
        self.assertEqual(family_matrix_summary["provenance_source_count"], 33)
        self.assertEqual(version_matrix_summary["provenance_source_count"], 33)
        self.assertEqual(version_matrix_summary["active_version_count"], 22)
        self.assertFalse(version_matrix_summary["configuration_pairs_generated"])
        self.assertEqual(len(family_matrix_payload["families"]), 6)
        self.assertEqual(len(version_matrix_payload["versions"]), 22)

        configuration_codes = [
            code
            for row in version_matrix_payload["versions"]
            for code in row["configuration_codes"]
        ]
        self.assertEqual(len(configuration_codes), 81)
        self.assertEqual(len(set(configuration_codes)), 81)
        self.assertEqual(
            sum(
                row["provenance"]["relationship_count"]
                for row in version_matrix_payload["versions"]
            ),
            251,
        )

    def test_cross_model_html_links_to_offline_family_summary(self) -> None:
        cross_model = self.contents[
            "cross-model/cross-model-comparison-view.html"
        ].decode("utf-8")
        family_matrix_html = self.contents[FAMILY_MATRIX_HTML].decode("utf-8")
        version_matrix_html = self.contents[VERSION_MATRIX_HTML].decode("utf-8")
        self.assertEqual(cross_model.count(FAMILY_HTML_HREF), 1)
        self.assertIn("exact source provenance", cross_model)
        for rendered in (family_matrix_html, version_matrix_html):
            self.assertTrue(rendered.startswith("<!doctype html>"))
            self.assertNotIn("<script", rendered.lower())
            self.assertNotIn("http://", rendered.lower())
            self.assertNotIn("https://", rendered.lower())
            self.assertIn("creates no configuration pair", rendered)
        self.assertEqual(
            family_matrix_html.count('data-state="not_stated"'), 2
        )
        self.assertEqual(version_matrix_html.count("<tr>"), 23)
        self.assertIn("No version is ranked or recommended", version_matrix_html)

    def test_integrated_assets_pass_canonical_release_verification(self) -> None:
        self.assertEqual(verify_release_assets(self.output), self.manifest)

        workspace = self.root / "verified-workspace"
        assets = workspace / ASSETS_DIRECTORY_NAME
        contents = workspace / CONTENTS_DIRECTORY_NAME
        shutil.copytree(self.output, assets)
        entry_points = _extract_verified_contents(
            assets,
            contents,
            self.manifest,
        )
        metadata = {
            "release_version": self.VERSION,
            "release_tag": f"data-products-v{self.VERSION}",
            "repository_commit": self.COMMIT,
            "release_url": (
                "https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/"
                f"data-products-v{self.VERSION}"
            ),
        }
        rendered = render_workspace_index(
            workspace,
            self.manifest,
            metadata,
        )
        index_path = write_workspace_index(
            workspace,
            self.manifest,
            metadata,
        )

        expected = {
            "model_family_summary_html": (
                "contents/model-families/portfolio_model_family_summary.html"
            ),
            "model_family_comparison_matrix_html": (
                "contents/model-families/"
                "portfolio_model_family_comparison_matrix.html"
            ),
            "model_version_comparison_matrix_html": (
                "contents/model-versions/"
                "portfolio_model_version_comparison_matrix.html"
            ),
        }
        for key, relative_path in expected.items():
            self.assertEqual(entry_points[key], relative_path)
            self.assertTrue((workspace / relative_path).is_file())
            self.assertIn(relative_path, rendered)
        self.assertIn("Model family summary", rendered)
        self.assertIn("Model family comparison matrix", rendered)
        self.assertIn("Model version comparison matrix", rendered)
        self.assertEqual(index_path.read_bytes(), rendered.encode("utf-8"))
        self.assertEqual(verify_workspace(workspace)["status"], "verified")

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
        self.assertIs(
            manifest["portfolio_model_family_comparison_matrix_generated"],
            True,
        )
        self.assertIs(
            manifest["portfolio_model_version_comparison_matrix_generated"],
            True,
        )


if __name__ == "__main__":
    unittest.main()
