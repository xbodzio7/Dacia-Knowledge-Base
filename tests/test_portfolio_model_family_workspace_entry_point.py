from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from reporting.data_product_release_download import (  # noqa: E402
    ASSETS_DIRECTORY_NAME,
    CONTENTS_DIRECTORY_NAME,
    OPTIONAL_ENTRY_POINTS,
    _extract_verified_contents,
)
from reporting.data_product_release_model import verify_release_assets  # noqa: E402
from reporting.data_product_workspace_index import write_workspace_index  # noqa: E402
from reporting.portfolio_model_family_release_integration import (  # noqa: E402
    create_release_assets,
)


class PortfolioModelFamilyWorkspaceEntryPointTest(unittest.TestCase):
    def test_optional_entry_point_is_declared(self) -> None:
        self.assertEqual(
            OPTIONAL_ENTRY_POINTS["model_family_summary_html"],
            "model-families/portfolio_model_family_summary.html",
        )

    def test_verified_workspace_exposes_direct_family_entry_point_and_card(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            release = root / "release"
            create_release_assets(ROOT, release, "9.9.9", "1" * 40)
            workspace = root / "workspace"
            assets = workspace / ASSETS_DIRECTORY_NAME
            contents = workspace / CONTENTS_DIRECTORY_NAME
            shutil.copytree(release, assets)
            manifest = verify_release_assets(assets)
            entry_points = _extract_verified_contents(assets, contents, manifest)
            self.assertEqual(
                entry_points["model_family_summary_html"],
                "contents/model-families/portfolio_model_family_summary.html",
            )
            index = write_workspace_index(
                workspace,
                manifest,
                {
                    "release_version": "9.9.9",
                    "release_tag": "data-products-v9.9.9",
                    "repository_commit": "1" * 40,
                    "release_url": (
                        "https://github.com/xbodzio7/Dacia-Knowledge-Base/"
                        "releases/tag/data-products-v9.9.9"
                    ),
                },
            ).read_text(encoding="utf-8")
            self.assertIn("Model family summary", index)
            self.assertIn(
                "contents/model-families/portfolio_model_family_summary.html",
                index,
            )

    def test_older_release_without_family_member_remains_compatible(self) -> None:
        source = (ROOT / "tools/reporting/data_product_release_download.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("if relative_name not in release_members", source)

    def test_cli_prints_family_entry_point_when_present(self) -> None:
        source = (ROOT / "tools/data_product_release_download.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('"model_family_summary_html": "Model family summary"', source)
        self.assertIn('keys.append("model_family_summary_html")', source)


if __name__ == "__main__":
    unittest.main()
