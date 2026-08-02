from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))

import portfolio_model_family_summary as cli  # noqa: E402
from reporting.portfolio_model_family_summary import (  # noqa: E402
    collect_summary,
    render_html,
    render_json,
    render_markdown,
)


class PortfolioModelFamilySummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = collect_summary(REPOSITORY)
        cls.families = {
            item["model_code"]: item for item in cls.summary["families"]
        }

    def test_portfolio_summary_matches_verified_repository_baseline(self) -> None:
        self.assertEqual(self.summary["version"], 1)
        self.assertEqual(self.summary["kind"], "portfolio_model_family_summary")
        self.assertEqual(self.summary["as_of"], "2026-08-02")
        self.assertEqual(
            self.summary["summary"],
            {
                "model_family_count": 6,
                "reporting_scope_count": 22,
                "single_model_scope_count": 20,
                "mixed_model_scope_count": 2,
                "active_configuration_count": 81,
                "within_scope_pair_count": 130,
                "provenance_source_count": 33,
                "source_configuration_relationship_count": 251,
                "configurations_with_provenance_count": 81,
                "configurations_without_provenance_count": 0,
                "cross_scope_pairs_generated": False,
                "ranking_generated": False,
                "recommendations_generated": False,
                "inferred_values_generated": False,
            },
        )

    def test_family_order_and_commercial_counts_are_exact(self) -> None:
        self.assertEqual(
            [item["model_code"] for item in self.summary["families"]],
            [
                "sandero_iii",
                "sandero_stepway_iii",
                "jogger",
                "duster_iii",
                "bigster",
                "spring",
            ],
        )
        expected = {
            "sandero_iii": (7, 3, 63900, 80500),
            "sandero_stepway_iii": (8, 3, 71700, 89400),
            "jogger": (22, 4, 77900, 118050),
            "duster_iii": (27, 5, 82000, 123600),
            "bigster": (14, 4, 101400, 137600),
            "spring": (3, 3, 73500, 85900),
        }
        for code, values in expected.items():
            family = self.families[code]
            price = family["catalog_price"]
            self.assertEqual(family["configuration_count"], values[0])
            self.assertEqual(family["version_count"], values[1])
            self.assertEqual(price["minimum"], values[2])
            self.assertEqual(price["maximum"], values[3])
            self.assertEqual(price["recorded_count"], values[0])
            self.assertEqual(price["missing_count"], 0)

    def test_exact_provenance_counts_and_date_ranges_are_preserved(self) -> None:
        expected = {
            "sandero_iii": (8, 29, "2026-02-02", "2026-07-24"),
            "sandero_stepway_iii": (11, 36, "2026-02-02", "2026-07-24"),
            "jogger": (4, 88, "2025-12-17", "2026-07-24"),
            "duster_iii": (8, 62, "2025-10-20", "2026-07-25"),
            "bigster": (2, 28, "2025-12-10", "2026-07-03"),
            "spring": (4, 8, "2026-02-19", "2026-08-02"),
        }
        for code, values in expected.items():
            provenance = self.families[code]["provenance"]
            self.assertEqual(provenance["source_count"], values[0])
            self.assertEqual(provenance["relationship_count"], values[1])
            self.assertEqual(provenance["earliest_document_date"], values[2])
            self.assertEqual(provenance["latest_document_date"], values[3])
            self.assertEqual(
                provenance["configuration_coverage_count"],
                self.families[code]["configuration_count"],
            )
            self.assertEqual(provenance["missing_configuration_count"], 0)

    def test_every_provenance_entry_is_exact_and_configuration_bounded(self) -> None:
        relation_total = 0
        used_sources: set[str] = set()
        for family in self.summary["families"]:
            family_codes = set(family["configuration_codes"])
            provenance = family["provenance"]
            relation_total += provenance["relationship_count"]
            for source in provenance["sources"]:
                used_sources.add(source["source_code"])
                self.assertEqual(len(source["sha256"]), 64)
                self.assertRegex(source["sha256"], r"^[0-9a-f]{64}$")
                self.assertTrue(source["document_date"])
                self.assertEqual(source["status"], "active")
                self.assertTrue(set(source["configuration_codes"]).issubset(family_codes))
                self.assertEqual(
                    source["configuration_count"],
                    len(source["configuration_codes"]),
                )
        self.assertEqual(relation_total, 251)
        self.assertEqual(len(used_sources), 33)

    def test_reporting_scope_membership_is_reused_without_pair_expansion(self) -> None:
        self.assertEqual(self.families["sandero_iii"]["shared_scope_count"], 2)
        self.assertEqual(
            self.families["sandero_stepway_iii"]["shared_scope_count"], 2
        )
        self.assertEqual(self.families["jogger"]["shared_scope_count"], 0)
        self.assertIn(
            "sandero_ecog120_manual",
            self.families["sandero_iii"]["shared_scope_slugs"],
        )
        self.assertIn(
            "sandero_tce100_stepway_tce110_manual",
            self.families["sandero_stepway_iii"]["shared_scope_slugs"],
        )
        self.assertFalse(self.summary["summary"]["cross_scope_pairs_generated"])
        self.assertFalse(self.summary["summary"]["ranking_generated"])
        self.assertFalse(self.summary["summary"]["recommendations_generated"])
        self.assertFalse(self.summary["summary"]["inferred_values_generated"])

    def test_unknown_seat_values_remain_not_stated(self) -> None:
        for code in ("bigster", "duster_iii"):
            self.assertEqual(self.families[code]["recorded_seat_values"], [])
            self.assertEqual(self.families[code]["seat_summary_state"], "not_stated")
        self.assertEqual(self.families["spring"]["recorded_seat_values"], [4])
        self.assertEqual(self.families["jogger"]["recorded_seat_values"], [5, 7])

    def test_json_markdown_and_html_rendering_are_deterministic(self) -> None:
        json_text = render_json(self.summary)
        markdown = render_markdown(self.summary)
        html = render_html(self.summary)
        self.assertEqual(json_text, render_json(self.summary))
        self.assertEqual(markdown, render_markdown(self.summary))
        self.assertEqual(html, render_html(self.summary))
        self.assertEqual(json.loads(json_text), self.summary)
        self.assertTrue(markdown.startswith("# Portfolio Model Family Summary"))
        self.assertTrue(html.startswith("<!doctype html>"))

    def test_html_is_standalone_and_exposes_source_hashes(self) -> None:
        rendered = render_html(self.summary)
        self.assertNotIn("<script", rendered.lower())
        self.assertNotIn("<img", rendered.lower())
        self.assertNotIn("http://", rendered.lower())
        self.assertNotIn("https://", rendered.lower())
        self.assertEqual(rendered.count('class="family"'), 6)
        self.assertEqual(rendered.count("SHA-256 "), 37)
        self.assertIn('data-state="not_stated">nie podano</dd>', rendered)
        self.assertIn("nie tworzy par między zakresami", rendered.lower())

    def test_committed_reporting_artifacts_match_the_generator(self) -> None:
        base = REPOSITORY / "data/reporting/portfolio_model_family_summary"
        self.assertEqual(
            (base.with_suffix(".json")).read_text(encoding="utf-8"),
            render_json(self.summary),
        )
        self.assertEqual(
            (base.with_suffix(".md")).read_text(encoding="utf-8"),
            render_markdown(self.summary),
        )
        self.assertEqual(
            (base.with_suffix(".html")).read_text(encoding="utf-8"),
            render_html(self.summary),
        )

    def test_cli_writes_all_formats_and_reports_success(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            json_path = root / "summary.json"
            markdown_path = root / "summary.md"
            html_path = root / "summary.html"
            result = cli.main(
                [
                    "--json",
                    str(json_path),
                    "--markdown",
                    str(markdown_path),
                    "--html",
                    str(html_path),
                ],
                repository=REPOSITORY,
            )
            self.assertEqual(result, 0)
            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), self.summary)
            self.assertEqual(markdown_path.read_text(encoding="utf-8"), render_markdown(self.summary))
            self.assertEqual(html_path.read_text(encoding="utf-8"), render_html(self.summary))


if __name__ == "__main__":
    unittest.main()
