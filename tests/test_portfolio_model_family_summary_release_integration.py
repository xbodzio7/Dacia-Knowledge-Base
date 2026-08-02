from __future__ import annotations

import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import data_product_release_download as download_cli  # noqa: E402
from reporting.data_product_release import create_release_assets  # noqa: E402
from reporting.data_product_release_download import (  # noqa: E402
    ASSETS_DIRECTORY_NAME,
    CONTENTS_DIRECTORY_NAME,
    OPTIONAL_ENTRY_POINTS,
    _extract_verified_contents,
)
from reporting.data_product_release_model import (  # noqa: E402
    archive_name,
    verify_release_assets,
)
from reporting.data_product_workspace_index import (  # noqa: E402
    write_workspace_index,
)


VERSION = "1.2.3"
COMMIT_SHA = "1" * 40
FAMILY_DIRECTORY = "model-families"
FAMILY_JSON = f"{FAMILY_DIRECTORY}/portfolio-model-family-summary.json"
FAMILY_MARKDOWN = f"{FAMILY_DIRECTORY}/portfolio-model-family-summary.md"
FAMILY_HTML = f"{FAMILY_DIRECTORY}/portfolio-model-family-summary.html"


class PortfolioModelFamilySummaryReleaseIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name)
        cls.release = cls.root / "release"
        cls.manifest = create_release_assets(
            ROOT,
            cls.release,
            VERSION,
            COMMIT_SHA,
        )
        cls.archive = cls.release / archive_name(VERSION)
        cls.workspace = cls.root / "workspace"
        assets = cls.workspace / ASSETS_DIRECTORY_NAME
        contents = cls.workspace / CONTENTS_DIRECTORY_NAME
        shutil.copytree(cls.release, assets)
        verified = verify_release_assets(assets)
        cls.entry_points = _extract_verified_contents(
            assets,
            contents,
            verified,
        )
        cls.index_path = write_workspace_index(
            cls.workspace,
            verified,
            {
                "release_version": VERSION,
                "release_tag": f"data-products-v{VERSION}",
                "repository_commit": COMMIT_SHA,
                "release_url": (
                    "https://github.com/xbodzio7/Dacia-Knowledge-Base/"
                    f"releases/tag/data-products-v{VERSION}"
                ),
            },
        )

    def test_release_manifest_declares_family_summary(self) -> None:
        self.assertTrue(self.manifest["model_family_summary_generated"])
        self.assertEqual(self.manifest["model_family_count"], 6)
        self.assertEqual(self.manifest["model_family_summary_source_count"], 33)
        self.assertEqual(
            self.manifest["model_family_summary_relationship_count"],
            251,
        )
        self.assertFalse(self.manifest["cross_scope_pairs_generated"])
        self.assertFalse(self.manifest["ranking_generated"])
        self.assertFalse(self.manifest["recommendations_generated"])
        self.assertFalse(self.manifest["inferred_values_generated"])

    def test_release_archive_contains_all_three_family_members(self) -> None:
        with ZipFile(self.archive) as archive:
            names = archive.namelist()
        self.assertEqual(len(names), 96)
        self.assertTrue(
            {FAMILY_JSON, FAMILY_MARKDOWN, FAMILY_HTML}.issubset(set(names))
        )

    def test_released_family_summary_preserves_source_boundaries(self) -> None:
        with ZipFile(self.archive) as archive:
            summary = json.loads(archive.read(FAMILY_JSON))
        totals = summary["summary"]
        self.assertEqual(totals["model_family_count"], 6)
        self.assertEqual(totals["active_configuration_count"], 81)
        self.assertEqual(totals["reporting_scope_count"], 22)
        self.assertEqual(totals["within_scope_pair_count"], 130)
        self.assertEqual(totals["provenance_source_count"], 33)
        self.assertEqual(totals["source_configuration_relationship_count"], 251)
        self.assertEqual(totals["configurations_without_provenance_count"], 0)
        for flag in (
            "cross_scope_pairs_generated",
            "ranking_generated",
            "recommendations_generated",
            "inferred_values_generated",
        ):
            self.assertIs(totals[flag], False)

    def test_released_markdown_and_html_are_standalone(self) -> None:
        with ZipFile(self.archive) as archive:
            markdown = archive.read(FAMILY_MARKDOWN).decode("utf-8")
            rendered = archive.read(FAMILY_HTML).decode("utf-8")
        self.assertIn("# Portfolio Model Family Summary", markdown)
        self.assertIn("<!doctype html>", rendered.lower())
        self.assertEqual(rendered.count('class="family-card"'), 6)
        self.assertNotIn("<script", rendered.lower())

    def test_verified_download_exposes_family_html_entry_point(self) -> None:
        self.assertEqual(
            OPTIONAL_ENTRY_POINTS["model_family_summary_html"],
            FAMILY_HTML,
        )
        self.assertEqual(
            self.entry_points["model_family_summary_html"],
            f"contents/{FAMILY_HTML}",
        )
        self.assertTrue(
            (self.workspace / self.entry_points["model_family_summary_html"]).is_file()
        )

    def test_workspace_index_links_family_summary(self) -> None:
        rendered = self.index_path.read_text(encoding="utf-8")
        self.assertIn("Model family summary", rendered)
        self.assertIn(
            "contents/model-families/portfolio-model-family-summary.html",
            rendered,
        )
        self.assertEqual(rendered.count('class="product-card"'), 6)

    def test_download_cli_prints_family_summary_entry_point(self) -> None:
        output = io.StringIO()
        result = {
            "release_version": VERSION,
            "release_tag": f"data-products-v{VERSION}",
            "repository_commit": COMMIT_SHA,
            "selected_configuration_count": 81,
            "scope_group_count": 22,
            "assets_directory": "assets",
            "contents_directory": "contents",
            "entry_points": {
                "workspace_index": "index.html",
                "shortlist_html": "contents/shortlist/configuration-shortlist.html",
                "comparison_workbook": (
                    "contents/comparison-bundle/"
                    "configuration-comparison-workbook.xlsx"
                ),
                "comparison_bundle_manifest": (
                    "contents/comparison-bundle/comparison-bundle-manifest.json"
                ),
                "cross_model_html": (
                    "contents/cross-model/cross-model-comparison-view.html"
                ),
                "model_family_summary_html": f"contents/{FAMILY_HTML}",
                "release_notes": "contents/RELEASE_NOTES.md",
            },
        }
        with redirect_stdout(output):
            download_cli._print_summary(result, self.root / "consumer")
        self.assertIn("Model family summary", output.getvalue())
        self.assertIn(FAMILY_HTML, output.getvalue())

    def test_generator_and_canonical_state_contract_pass(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "tools/generate_portfolio_model_family_summary_release_integration_20260803.py",
                "--verify",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        state = json.loads((ROOT / "project/state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["baseline"]["tests"], 1860)
        self.assertEqual(
            state["current_package"]["package_id"],
            "portfolio_model_family_summary_release_integration_001",
        )
        self.assertEqual(
            state["next_package"]["package_id"],
            "data_products_v1_12_0_accelerated_release_preparation_001",
        )


if __name__ == "__main__":
    unittest.main()
