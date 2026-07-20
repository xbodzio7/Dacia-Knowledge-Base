from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))

import dkb  # noqa: E402


GUIDE_PATH = REPOSITORY / "project/guides/data-product-consumer-guide.md"
README_PATH = REPOSITORY / "README.md"
WORKFLOW_PATH = REPOSITORY / ".github/workflows/data-product-release-download.yml"


class DataProductConsumerGuideChecks(unittest.TestCase):
    def setUp(self) -> None:
        self.guide = GUIDE_PATH.read_text(encoding="utf-8")

    def test_guide_contains_complete_consumer_flow(self) -> None:
        required = (
            "data-product-release-download",
            "index.html",
            "configuration-shortlist.html",
            "configuration-comparison-workbook.xlsx",
            "comparison-bundle-manifest.json",
            "configuration-comparison-bundle",
            "data-product-workspace-verify",
            "data-product-release-manifest.json",
            "SHA256SUMS",
            "data-products-v1.0.0",
        )
        for value in required:
            with self.subTest(value=value):
                self.assertIn(value, self.guide)

    def test_every_documented_dkb_command_exists(self) -> None:
        commands = re.findall(
            r"python tools/dkb\.py ([a-z0-9-]+)",
            self.guide,
        )
        self.assertGreaterEqual(len(commands), 7)
        for command in commands:
            with self.subTest(command=command):
                self.assertIn(command, dkb.SCRIPT_COMMANDS)

    def test_guide_uses_explicit_immutable_versions(self) -> None:
        self.assertIn("--version 1.0.0", self.guide)
        self.assertIn("data-products-v1.0.0", self.guide)
        self.assertNotIn("--version latest", self.guide.lower())
        self.assertIn("Nie obsługuje mutowalnego aliasu `latest`", self.guide)

    def test_guide_preserves_read_only_and_data_boundaries(self) -> None:
        required = (
            "Weryfikator tylko odczytuje pliki",
            "nie naprawia uszkodzeń",
            "nie są generowane rankingi ani rekomendacje",
            "nie są inferowane brakujące wartości",
            "nie generuje par między zakresami",
        )
        for value in required:
            with self.subTest(value=value):
                self.assertIn(value, self.guide)

    def test_readme_links_the_consumer_guide(self) -> None:
        readme = README_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "project/guides/data-product-consumer-guide.md",
            readme,
        )

    def test_release_download_workflow_runs_guide_checks(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn("tests/data_product_consumer_guide_checks.py", workflow)
        self.assertIn("Run consumer guide checks", workflow)
        self.assertIn("contents: read", workflow)
        self.assertNotIn("contents: write", workflow)


if __name__ == "__main__":
    unittest.main()
