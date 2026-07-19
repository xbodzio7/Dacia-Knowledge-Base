from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))
sys.path.insert(0, str(REPOSITORY / "tests"))

import configuration_comparison as comparison  # noqa: E402
from reporting.configuration_comparison_html import render_html  # noqa: E402
from test_configuration_comparison import ConfigurationComparisonTests  # noqa: E402


class ConfigurationComparisonHtmlTests(unittest.TestCase):
    def fixture(self, root: Path) -> tuple[Path, Path, Path]:
        return ConfigurationComparisonTests().fixture(root)

    def report(self, root: Path):
        repository, completeness, evidence = self.fixture(root)
        return (
            repository,
            completeness,
            evidence,
            comparison.collect_report(repository, completeness, evidence),
        )

    def test_render_is_deterministic_and_self_contained(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, _, _, report = self.report(Path(directory))
        rendered = render_html(report)
        self.assertEqual(rendered, render_html(report))
        self.assertTrue(rendered.startswith("<!doctype html>"))
        self.assertIn("<style>", rendered)
        self.assertIn("<script>", rendered)
        self.assertNotIn("generated_at", rendered)
        self.assertNotIn("http://", rendered)
        self.assertNotIn("https://", rendered)

    def test_render_includes_filters_summary_and_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, _, _, report = self.report(Path(directory))
        rendered = render_html(report)
        self.assertIn('id="search"', rendered)
        self.assertIn('id="domain"', rendered)
        self.assertIn('id="comparison"', rendered)
        self.assertIn('id="differences-only"', rendered)
        self.assertIn("cfg_a__vs__cfg_b", rendered)
        self.assertIn("src_a", rendered)
        self.assertIn("not_stated", rendered)
        self.assertIn("different_version_different_transmission", rendered)

    def test_render_escapes_labels_and_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, _, _, report = self.report(Path(directory))
        report["pairs"][0]["pair_code"] = '<script>alert("x")</script>'
        report["pairs"][0]["technical"][0]["attribute_name"] = "A&B <unsafe>"
        rendered = render_html(report)
        self.assertNotIn('<script>alert("x")</script>', rendered)
        self.assertIn("&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;", rendered)
        self.assertIn("A&amp;B &lt;unsafe&gt;", rendered)

    def test_render_supports_an_empty_pair_selection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, completeness, evidence = self.fixture(Path(directory))
            report = comparison.collect_report(
                repository,
                completeness,
                evidence,
                pair_type_filter="same_version_different_transmission",
            )
        rendered = render_html(report)
        self.assertIn("Pary konfiguracji", rendered)
        self.assertIn("<strong>0</strong>", rendered)
        self.assertNotIn('<article class="pair"', rendered)

    def test_extract_html_argument_supports_both_cli_forms(self) -> None:
        arguments, path = comparison._extract_html_argument(
            ["--json", "report.json", "--html", "report.html"]
        )
        self.assertEqual(arguments, ["--json", "report.json"])
        self.assertEqual(path, Path("report.html"))
        arguments, path = comparison._extract_html_argument(
            ["--html=other.html", "--pair-type", "same_version_same_transmission"]
        )
        self.assertEqual(
            arguments,
            ["--pair-type", "same_version_same_transmission"],
        )
        self.assertEqual(path, Path("other.html"))

    def test_extract_html_argument_rejects_missing_or_duplicate_paths(self) -> None:
        with self.assertRaisesRegex(comparison.ComparisonError, "requires a path"):
            comparison._extract_html_argument(["--html"])
        with self.assertRaisesRegex(comparison.ComparisonError, "only once"):
            comparison._extract_html_argument(
                ["--html", "one.html", "--html=two.html"]
            )

    def test_main_writes_html_alongside_existing_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, completeness, evidence = self.fixture(root)
            json_path = root / "comparison.json"
            html_path = root / "comparison.html"
            with patch.object(comparison._base, "repository_root", return_value=repository):
                result = comparison.main(
                    [
                        "--completeness-spec",
                        str(completeness),
                        "--evidence-spec",
                        str(evidence),
                        "--json",
                        str(json_path),
                        "--html",
                        str(html_path),
                    ]
                )
            self.assertEqual(result, 0)
            self.assertTrue(json_path.is_file())
            self.assertTrue(html_path.is_file())
            self.assertIn("cfg_a__vs__cfg_b", html_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
