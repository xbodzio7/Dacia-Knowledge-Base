from __future__ import annotations

import csv
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))
sys.path.insert(0, str(REPOSITORY / "tests"))

import portfolio_model_family_comparison_matrix as matrix_cli  # noqa: E402
import portfolio_model_family_summary as summary_cli  # noqa: E402
from version_matrix_checks import run_version_matrix_checks  # noqa: E402
from reporting.portfolio_model_family_comparison_matrix import (  # noqa: E402
    CSV_COLUMNS,
    collect_matrix,
    render_csv as render_matrix_csv,
    render_html as render_matrix_html,
    render_json as render_matrix_json,
)
from reporting.portfolio_model_family_summary import (  # noqa: E402
    collect_summary,
    render_html as render_summary_html,
    render_json as render_summary_json,
    render_markdown,
)


class PortfolioModelFamilySummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = collect_summary(REPOSITORY)
        cls.families = {
            item["model_code"]: item for item in cls.summary["families"]
        }
        cls.matrix = collect_matrix(REPOSITORY)
        cls.matrix_families = {
            item["model_code"]: item for item in cls.matrix["families"]
        }

    def test_portfolio_summary_matches_verified_repository_baseline(self) -> None:
        self.assertEqual(self.summary["version"], 1)
        self.assertEqual(self.summary["kind"], "portfolio_model_family_summary")
        self.assertEqual(self.summary["as_of"], "2026-08-02")
        self.assertEqual(
            self.summary["summary"],
            {
                "model_family_count": 6,
                "reporting_scope_count": 23,
                "single_model_scope_count": 21,
                "mixed_model_scope_count": 2,
                "active_configuration_count": 84,
                "within_scope_pair_count": 133,
                "provenance_source_count": 33,
                "source_configuration_relationship_count": 254,
                "configurations_with_provenance_count": 84,
                "configurations_without_provenance_count": 0,
                "cross_scope_pairs_generated": False,
                "ranking_generated": False,
                "recommendations_generated": False,
                "inferred_values_generated": False,
            },
        )
        self.assertEqual(self.matrix["version"], 1)
        self.assertEqual(
            self.matrix["kind"],
            "portfolio_model_family_comparison_matrix",
        )
        self.assertEqual(self.matrix["as_of"], "2026-08-02")
        self.assertEqual(
            self.matrix["source_product"],
            {
                "kind": "portfolio_model_family_summary",
                "version": 1,
                "path": "data/reporting/portfolio_model_family_summary.json",
            },
        )
        self.assertEqual(
            self.matrix["summary"],
            {
                "model_family_count": 6,
                "active_configuration_count": 84,
                "reporting_scope_count": 23,
                "provenance_source_count": 33,
                "source_configuration_relationship_count": 254,
                "configurations_without_provenance_count": 0,
                "cross_scope_pairs_generated": False,
                "ranking_generated": False,
                "recommendations_generated": False,
                "inferred_values_generated": False,
            },
        )

        run_version_matrix_checks(self, REPOSITORY)

    def test_family_order_and_commercial_counts_are_exact(self) -> None:
        expected_order = [
            "sandero_iii",
            "sandero_stepway_iii",
            "jogger",
            "duster_iii",
            "bigster",
            "spring",
        ]
        self.assertEqual(
            [item["model_code"] for item in self.summary["families"]],
            expected_order,
        )
        self.assertEqual(
            [item["model_code"] for item in self.matrix["families"]],
            expected_order,
        )
        expected = {
            "sandero_iii": (7, 3, 63900, 80500, "recorded", [5], 7, 0),
            "sandero_stepway_iii": (8, 3, 71700, 89400, "recorded", [5], 8, 0),
            "jogger": (22, 4, 77900, 118050, "recorded", [5, 7], 22, 0),
            "duster_iii": (30, 5, 82000, 126100, "not_stated", [], 30, 0),
            "bigster": (14, 4, 101400, 137600, "not_stated", [], 14, 0),
            "spring": (3, 3, 73500, 85900, "recorded", [4], 3, 0),
        }
        for code, values in expected.items():
            family = self.families[code]
            price = family["catalog_price"]
            self.assertEqual(family["configuration_count"], values[0])
            self.assertEqual(family["version_count"], values[1])
            self.assertEqual(price["minimum"], values[2])
            self.assertEqual(price["maximum"], values[3])
            self.assertEqual(price["recorded_count"], values[6])
            self.assertEqual(price["missing_count"], values[7])

            matrix_family = self.matrix_families[code]
            matrix_price = matrix_family["catalog_price"]
            self.assertEqual(matrix_family["configuration_count"], values[0])
            self.assertEqual(matrix_family["version_count"], values[1])
            self.assertEqual(matrix_price["minimum"], values[2])
            self.assertEqual(matrix_price["maximum"], values[3])
            self.assertEqual(matrix_family["seat_summary_state"], values[4])
            self.assertEqual(matrix_family["recorded_seat_values"], values[5])

    def test_exact_provenance_counts_and_date_ranges_are_preserved(self) -> None:
        expected = {
            "sandero_iii": (8, 29, "2026-02-02", "2026-07-24"),
            "sandero_stepway_iii": (11, 36, "2026-02-02", "2026-07-24"),
            "jogger": (4, 88, "2025-12-17", "2026-07-24"),
            "duster_iii": (8, 65, "2025-10-20", "2026-07-25"),
            "bigster": (2, 28, "2025-12-10", "2026-07-03"),
            "spring": (4, 8, "2026-02-19", "2026-08-02"),
        }
        matrix_relationship_total = 0
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

            matrix_provenance = self.matrix_families[code]["provenance"]
            self.assertEqual(matrix_provenance["source_count"], values[0])
            self.assertEqual(matrix_provenance["relationship_count"], values[1])
            self.assertEqual(
                matrix_provenance["earliest_document_date"], values[2]
            )
            self.assertEqual(
                matrix_provenance["latest_document_date"], values[3]
            )
            self.assertEqual(
                matrix_provenance["configuration_coverage_count"],
                self.matrix_families[code]["configuration_count"],
            )
            self.assertEqual(
                matrix_provenance["missing_configuration_count"], 0
            )
            matrix_relationship_total += matrix_provenance["relationship_count"]
        self.assertEqual(matrix_relationship_total, 254)

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
                self.assertTrue(
                    set(source["configuration_codes"]).issubset(family_codes)
                )
                self.assertEqual(
                    source["configuration_count"],
                    len(source["configuration_codes"]),
                )
        self.assertEqual(relation_total, 254)
        self.assertEqual(len(used_sources), 33)
        self.assertEqual(
            self.matrix_families["spring"]["transmission_values"],
            ["automatic"],
        )
        self.assertEqual(
            self.matrix_families["spring"]["powertrain_labels"],
            ["electric 100", "electric 70"],
        )
        self.assertEqual(
            self.matrix_families["duster_iii"]["powertrain_labels"],
            [
                "Eco-G 100 4x2",
                "Eco-G 120 4x2",
                "hybrid 140 4x2",
                "hybrid 155 4x2",
                "hybrid-G 150 4x4",
                "mild hybrid 130 4x2",
                "mild hybrid 130 4x4",
                "mild hybrid 140 4x2",
            ],
        )

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
        for family in self.matrix["families"]:
            self.assertEqual(
                family["reporting_scope_count"],
                family["exclusive_scope_count"] + family["shared_scope_count"],
            )
        self.assertEqual(
            self.matrix_families["sandero_iii"]["shared_scope_count"], 2
        )
        self.assertEqual(
            self.matrix_families["sandero_stepway_iii"]["shared_scope_count"], 2
        )
        self.assertFalse(
            self.matrix["summary"]["cross_scope_pairs_generated"]
        )
        self.assertFalse(self.matrix["summary"]["ranking_generated"])
        self.assertFalse(self.matrix["summary"]["recommendations_generated"])
        self.assertFalse(self.matrix["summary"]["inferred_values_generated"])

    def test_unknown_seat_values_remain_not_stated(self) -> None:
        for code in ("bigster", "duster_iii"):
            self.assertEqual(self.families[code]["recorded_seat_values"], [])
            self.assertEqual(
                self.families[code]["seat_summary_state"], "not_stated"
            )
            self.assertEqual(
                self.matrix_families[code]["recorded_seat_values"], []
            )
            self.assertEqual(
                self.matrix_families[code]["seat_summary_state"], "not_stated"
            )
        self.assertEqual(self.families["spring"]["recorded_seat_values"], [4])
        self.assertEqual(self.families["jogger"]["recorded_seat_values"], [5, 7])
        self.assertEqual(
            self.matrix_families["spring"]["recorded_seat_values"], [4]
        )
        self.assertEqual(
            self.matrix_families["jogger"]["recorded_seat_values"], [5, 7]
        )

    def test_json_markdown_and_html_rendering_are_deterministic(self) -> None:
        summary_json = render_summary_json(self.summary)
        markdown = render_markdown(self.summary)
        summary_html = render_summary_html(self.summary)
        self.assertEqual(summary_json, render_summary_json(self.summary))
        self.assertEqual(markdown, render_markdown(self.summary))
        self.assertEqual(summary_html, render_summary_html(self.summary))
        self.assertEqual(json.loads(summary_json), self.summary)
        self.assertTrue(markdown.startswith("# Portfolio Model Family Summary"))
        self.assertTrue(summary_html.startswith("<!doctype html>"))

        matrix_json = render_matrix_json(self.matrix)
        matrix_csv = render_matrix_csv(self.matrix)
        matrix_html = render_matrix_html(self.matrix)
        self.assertEqual(matrix_json, render_matrix_json(self.matrix))
        self.assertEqual(matrix_csv, render_matrix_csv(self.matrix))
        self.assertEqual(matrix_html, render_matrix_html(self.matrix))
        self.assertEqual(json.loads(matrix_json), self.matrix)
        rows = list(csv.DictReader(io.StringIO(matrix_csv)))
        self.assertEqual(tuple(rows[0]), CSV_COLUMNS)
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[3]["seat_summary_state"], "not_stated")
        self.assertEqual(rows[3]["recorded_seat_values"], "")

    def test_html_is_standalone_and_exposes_source_hashes(self) -> None:
        summary_rendered = render_summary_html(self.summary)
        self.assertNotIn("<script", summary_rendered.lower())
        self.assertNotIn("<img", summary_rendered.lower())
        self.assertNotIn("http://", summary_rendered.lower())
        self.assertNotIn("https://", summary_rendered.lower())
        self.assertEqual(summary_rendered.count('class="family"'), 6)
        self.assertEqual(summary_rendered.count("SHA-256 "), 37)
        self.assertIn(
            'data-state="not_stated">nie podano</dd>', summary_rendered
        )
        self.assertIn(
            "nie tworzy par między zakresami", summary_rendered.lower()
        )

        matrix_rendered = render_matrix_html(self.matrix)
        lowered = matrix_rendered.lower()
        self.assertTrue(matrix_rendered.startswith("<!doctype html>"))
        self.assertNotIn("<script", lowered)
        self.assertNotIn("<img", lowered)
        self.assertNotIn("http://", lowered)
        self.assertNotIn("https://", lowered)
        self.assertEqual(matrix_rendered.count("<tr>"), 7)
        self.assertEqual(
            matrix_rendered.count('data-state="not_stated"'), 2
        )
        self.assertIn("creates no configuration pair", matrix_rendered)
        self.assertIn(
            "ranking, recommendation or inferred value", matrix_rendered
        )

    def test_committed_reporting_artifacts_match_the_generator(self) -> None:
        summary_base = REPOSITORY / "data/reporting/portfolio_model_family_summary"
        self.assertEqual(
            summary_base.with_suffix(".json").read_text(encoding="utf-8"),
            render_summary_json(self.summary),
        )
        self.assertEqual(
            summary_base.with_suffix(".md").read_text(encoding="utf-8"),
            render_markdown(self.summary),
        )
        self.assertEqual(
            summary_base.with_suffix(".html").read_text(encoding="utf-8"),
            render_summary_html(self.summary),
        )

        matrix_base = (
            REPOSITORY
            / "data/reporting/portfolio_model_family_comparison_matrix"
        )
        self.assertEqual(
            matrix_base.with_suffix(".json").read_text(encoding="utf-8"),
            render_matrix_json(self.matrix),
        )
        self.assertEqual(
            matrix_base.with_suffix(".csv").read_text(encoding="utf-8"),
            render_matrix_csv(self.matrix),
        )
        self.assertEqual(
            matrix_base.with_suffix(".html").read_text(encoding="utf-8"),
            render_matrix_html(self.matrix),
        )

    def test_cli_writes_all_formats_and_reports_success(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            summary_json_path = root / "summary.json"
            markdown_path = root / "summary.md"
            summary_html_path = root / "summary.html"
            result = summary_cli.main(
                [
                    "--json",
                    str(summary_json_path),
                    "--markdown",
                    str(markdown_path),
                    "--html",
                    str(summary_html_path),
                ],
                repository=REPOSITORY,
            )
            self.assertEqual(result, 0)
            self.assertEqual(
                json.loads(summary_json_path.read_text(encoding="utf-8")),
                self.summary,
            )
            self.assertEqual(
                markdown_path.read_text(encoding="utf-8"),
                render_markdown(self.summary),
            )
            self.assertEqual(
                summary_html_path.read_text(encoding="utf-8"),
                render_summary_html(self.summary),
            )

            matrix_json_path = root / "matrix.json"
            matrix_csv_path = root / "matrix.csv"
            matrix_html_path = root / "matrix.html"
            matrix_result = matrix_cli.main(
                [
                    "--json",
                    str(matrix_json_path),
                    "--csv",
                    str(matrix_csv_path),
                    "--html",
                    str(matrix_html_path),
                ],
                repository=REPOSITORY,
            )
            self.assertEqual(matrix_result, 0)
            self.assertEqual(
                matrix_json_path.read_text(encoding="utf-8"),
                render_matrix_json(self.matrix),
            )
            self.assertEqual(
                matrix_csv_path.read_text(encoding="utf-8"),
                render_matrix_csv(self.matrix),
            )
            self.assertEqual(
                matrix_html_path.read_text(encoding="utf-8"),
                render_matrix_html(self.matrix),
            )


if __name__ == "__main__":
    unittest.main()
