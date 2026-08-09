from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

REPOSITORY = Path(__file__).resolve().parents[1]
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
    VERSION_MATRIX_FILES,
    VERSION_MATRIX_HTML,
)
from reporting.portfolio_source_coverage_matrix_release_integration import (  # noqa: E402
    RELEASE_NOTES,
    SOURCE_MATRIX_FILES,
    SOURCE_MATRIX_HTML,
    create_release_assets,
)


class PortfolioModelFamilyReleaseIntegrationTests(unittest.TestCase):
    COMMIT = "1" * 40
    VERSION = "1.15.0"

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
                or name.startswith("source-coverage/")
                or name == "cross-model/cross-model-comparison-view.html"
                or name == RELEASE_NOTES
            }

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_manifest_declares_all_integrated_products(self) -> None:
        expectations = (
            (
                "portfolio_model_family_summary",
                ["JSON", "Markdown", "HTML"],
                "model-families",
            ),
            (
                "portfolio_model_family_comparison_matrix",
                ["JSON", "CSV", "HTML"],
                "model-families",
            ),
            (
                "portfolio_model_version_comparison_matrix",
                ["JSON", "CSV", "HTML"],
                "model-versions",
            ),
            (
                "portfolio_source_coverage_matrix",
                ["JSON", "CSV", "HTML"],
                "source-coverage",
            ),
        )
        for prefix, formats, directory in expectations:
            self.assertIs(self.manifest[f"{prefix}_generated"], True)
            self.assertEqual(self.manifest[f"{prefix}_formats"], formats)
            self.assertEqual(self.manifest[f"{prefix}_directory"], directory)

    def test_archive_copies_all_twelve_verified_outputs_byte_for_byte(self) -> None:
        products = (
            ("model-families", FAMILY_FILES + FAMILY_MATRIX_FILES),
            ("model-versions", VERSION_MATRIX_FILES),
            ("source-coverage", SOURCE_MATRIX_FILES),
        )
        expected = {
            f"{directory}/{name}"
            for directory, names in products
            for name in names
        }
        self.assertTrue(expected.issubset(set(self.names)))
        for directory, names in products:
            for name in names:
                self.assertEqual(
                    self.contents[f"{directory}/{name}"],
                    (REPOSITORY / "data" / "reporting" / name).read_bytes(),
                )

        notes = self.contents[RELEASE_NOTES].decode("utf-8")
        self.assertEqual(
            notes.count("## v1.15.0 portfolio source coverage matrix"),
            1,
        )
        self.assertIn("source_coverage_matrix_html", notes)
        self.assertIn("Public `data-products-v1.14.1` remains immutable", notes)
        self.assertIn("built twice from the exact publication merge SHA", notes)

    def test_json_products_preserve_exact_coverage_boundaries(self) -> None:
        family = json.loads(
            self.contents[
                "model-families/portfolio_model_family_summary.json"
            ]
        )
        family_matrix = json.loads(
            self.contents[
                "model-families/portfolio_model_family_comparison_matrix.json"
            ]
        )
        version_matrix = json.loads(
            self.contents[
                "model-versions/portfolio_model_version_comparison_matrix.json"
            ]
        )
        source_matrix = json.loads(
            self.contents[
                "source-coverage/portfolio_source_coverage_matrix.json"
            ]
        )

        self.assertEqual(
            family_matrix["source_product"],
            {
                "kind": "portfolio_model_family_summary",
                "version": 1,
                "path": "data/reporting/portfolio_model_family_summary.json",
            },
        )
        for summary in (
            family["summary"],
            family_matrix["summary"],
            version_matrix["summary"],
        ):
            self.assertEqual(summary["model_family_count"], 6)
            self.assertEqual(summary["active_configuration_count"], 84)
            self.assertEqual(summary["reporting_scope_count"], 23)
            self.assertEqual(
                summary["source_configuration_relationship_count"],
                284,
            )
            self.assertEqual(
                summary["configurations_without_provenance_count"],
                0,
            )
            self.assertFalse(summary["cross_scope_pairs_generated"])
            self.assertFalse(summary["ranking_generated"])
            self.assertFalse(summary["recommendations_generated"])
            self.assertFalse(summary["inferred_values_generated"])

        version_summary = version_matrix["summary"]
        self.assertEqual(version_summary["provenance_source_count"], 35)
        self.assertEqual(version_summary["active_version_count"], 22)
        self.assertFalse(version_summary["configuration_pairs_generated"])
        self.assertEqual(len(version_matrix["versions"]), 22)
        version_configurations = [
            code
            for row in version_matrix["versions"]
            for code in row["configuration_codes"]
        ]
        self.assertEqual(len(version_configurations), 84)
        self.assertEqual(len(set(version_configurations)), 84)
        self.assertEqual(
            sum(
                row["provenance"]["relationship_count"]
                for row in version_matrix["versions"]
            ),
            269,
        )

        self.assertEqual(source_matrix["kind"], "portfolio_source_coverage_matrix")
        self.assertEqual(source_matrix["version"], 1)
        source_summary = source_matrix["summary"]
        expected_summary = {
            "provenance_source_count": 34,
            "source_configuration_relationship_count": 269,
            "active_configuration_count": 84,
            "active_version_count": 22,
            "model_family_count": 6,
            "configurations_without_provenance_count": 0,
            "source_quality_scores_generated": False,
            "source_rankings_generated": False,
            "recommendations_generated": False,
            "inferred_values_generated": False,
        }
        for key, value in expected_summary.items():
            self.assertEqual(source_summary[key], value)

        source_rows = source_matrix["sources"]
        self.assertEqual(len(source_rows), 34)
        self.assertEqual(len({row["source_code"] for row in source_rows}), 34)
        self.assertEqual(
            sum(row["relationship_count"] for row in source_rows),
            269,
        )
        self.assertEqual(
            len(
                {
                    code
                    for row in source_rows
                    for code in row["configuration_codes"]
                }
            ),
            84,
        )
        self.assertEqual(
            len(
                {
                    code
                    for row in source_rows
                    for code in row["version_codes"]
                }
            ),
            22,
        )
        self.assertEqual(
            len(
                {
                    code
                    for row in source_rows
                    for code in row["model_codes"]
                }
            ),
            6,
        )
        for row in source_rows:
            self.assertEqual(row["status"], "active")
            self.assertEqual(len(row["sha256"]), 64)
            self.assertTrue(row["external_reference"] or row["file_path"])

    def test_standalone_html_products_preserve_offline_boundary(self) -> None:
        cross_model = self.contents[
            "cross-model/cross-model-comparison-view.html"
        ].decode("utf-8")
        family_html = self.contents[FAMILY_MATRIX_HTML].decode("utf-8")
        version_html = self.contents[VERSION_MATRIX_HTML].decode("utf-8")
        source_html = self.contents[SOURCE_MATRIX_HTML].decode("utf-8")

        self.assertEqual(cross_model.count(FAMILY_HTML_HREF), 1)
        self.assertIn("exact source provenance", cross_model)
        for rendered in (family_html, version_html, source_html):
            lowered = rendered.lower()
            self.assertTrue(rendered.startswith("<!doctype html>"))
            self.assertNotIn("<script", lowered)
            self.assertNotIn('href="http', lowered)
            self.assertNotIn("src=\"http", lowered)
        for rendered in (family_html, version_html):
            self.assertNotIn("http://", rendered.lower())
            self.assertNotIn("https://", rendered.lower())

        self.assertIn("creates no configuration pair", family_html)
        self.assertIn("creates no configuration pair", version_html)
        self.assertEqual(family_html.count('data-state="not_stated"'), 2)
        self.assertEqual(version_html.count("<tr>"), 23)
        self.assertIn("No version is ranked or recommended", version_html)
        self.assertEqual(source_html.count("<tr>"), 35)
        self.assertIn("Portfolio Source Coverage Matrix", source_html)
        self.assertIn("https://", source_html)

    def test_integrated_assets_and_workspace_verify(self) -> None:
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
            "source_coverage_matrix_html": (
                "contents/source-coverage/"
                "portfolio_source_coverage_matrix.html"
            ),
        }
        for key, relative_path in expected.items():
            self.assertEqual(entry_points[key], relative_path)
            self.assertTrue((workspace / relative_path).is_file())
            self.assertIn(relative_path, rendered)
        for title in (
            "Model family summary",
            "Model family comparison matrix",
            "Model version comparison matrix",
            "Source coverage matrix",
        ):
            self.assertIn(title, rendered)
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

    def test_cli_build_uses_source_coverage_integrated_path(self) -> None:
        output = self.root / "cli"
        self.assertEqual(
            release_cli.main(
                [
                    "--version",
                    self.VERSION,
                    "--commit-sha",
                    self.COMMIT,
                    "--output-directory",
                    str(output),
                ],
                repository=REPOSITORY,
            ),
            0,
        )
        manifest = verify_release_assets(output)
        for key in (
            "portfolio_model_family_summary_generated",
            "portfolio_model_family_comparison_matrix_generated",
            "portfolio_model_version_comparison_matrix_generated",
            "portfolio_source_coverage_matrix_generated",
        ):
            self.assertIs(manifest[key], True)


if __name__ == "__main__":
    unittest.main()
