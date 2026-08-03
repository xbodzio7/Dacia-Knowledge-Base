from __future__ import annotations

import csv
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))

import portfolio_model_family_comparison_matrix as cli  # noqa: E402
from reporting.portfolio_model_family_comparison_matrix import (  # noqa: E402
    CSV_COLUMNS,
    collect_matrix,
    render_csv,
    render_html,
    render_json,
)


class PortfolioModelFamilyComparisonMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = collect_matrix(REPOSITORY)
        cls.families = {
            item["model_code"]: item for item in cls.matrix["families"]
        }

    def test_matrix_matches_verified_repository_baseline(self) -> None:
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
                "active_configuration_count": 81,
                "reporting_scope_count": 22,
                "provenance_source_count": 33,
                "source_configuration_relationship_count": 251,
                "configurations_without_provenance_count": 0,
                "cross_scope_pairs_generated": False,
                "ranking_generated": False,
                "recommendations_generated": False,
                "inferred_values_generated": False,
            },
        )

    def test_exact_family_rows_and_unknown_state(self) -> None:
        self.assertEqual(
            [item["model_code"] for item in self.matrix["families"]],
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
            "sandero_iii": (7, 3, 63900, 80500, "recorded", [5]),
            "sandero_stepway_iii": (8, 3, 71700, 89400, "recorded", [5]),
            "jogger": (22, 4, 77900, 118050, "recorded", [5, 7]),
            "duster_iii": (27, 5, 82000, 123600, "not_stated", []),
            "bigster": (14, 4, 101400, 137600, "not_stated", []),
            "spring": (3, 3, 73500, 85900, "recorded", [4]),
        }
        for code, values in expected.items():
            family = self.families[code]
            price = family["catalog_price"]
            self.assertEqual(family["configuration_count"], values[0])
            self.assertEqual(family["version_count"], values[1])
            self.assertEqual(price["minimum"], values[2])
            self.assertEqual(price["maximum"], values[3])
            self.assertEqual(family["seat_summary_state"], values[4])
            self.assertEqual(family["recorded_seat_values"], values[5])

    def test_projection_preserves_lists_and_scope_boundaries(self) -> None:
        self.assertEqual(
            self.families["spring"]["transmission_values"],
            ["automatic"],
        )
        self.assertEqual(
            self.families["spring"]["powertrain_labels"],
            ["electric 100", "electric 70"],
        )
        self.assertEqual(
            self.families["duster_iii"]["powertrain_labels"],
            [
                "Eco-G 100 4x2",
                "Eco-G 120 4x2",
                "hybrid 140 4x2",
                "hybrid 155 4x2",
                "mild hybrid 130 4x2",
                "mild hybrid 130 4x4",
                "mild hybrid 140 4x2",
            ],
        )
        for family in self.matrix["families"]:
            self.assertEqual(
                family["reporting_scope_count"],
                family["exclusive_scope_count"] + family["shared_scope_count"],
            )
        self.assertEqual(self.families["sandero_iii"]["shared_scope_count"], 2)
        self.assertEqual(
            self.families["sandero_stepway_iii"]["shared_scope_count"],
            2,
        )

    def test_provenance_counts_and_coverage_are_exact(self) -> None:
        expected = {
            "sandero_iii": (8, 29, "2026-02-02", "2026-07-24"),
            "sandero_stepway_iii": (11, 36, "2026-02-02", "2026-07-24"),
            "jogger": (4, 88, "2025-12-17", "2026-07-24"),
            "duster_iii": (8, 62, "2025-10-20", "2026-07-25"),
            "bigster": (2, 28, "2025-12-10", "2026-07-03"),
            "spring": (4, 8, "2026-02-19", "2026-08-02"),
        }
        relationships = 0
        for code, values in expected.items():
            family = self.families[code]
            provenance = family["provenance"]
            self.assertEqual(provenance["source_count"], values[0])
            self.assertEqual(provenance["relationship_count"], values[1])
            self.assertEqual(provenance["earliest_document_date"], values[2])
            self.assertEqual(provenance["latest_document_date"], values[3])
            self.assertEqual(
                provenance["configuration_coverage_count"],
                family["configuration_count"],
            )
            self.assertEqual(provenance["missing_configuration_count"], 0)
            relationships += provenance["relationship_count"]
        self.assertEqual(relationships, 251)

    def test_json_csv_and_html_rendering_are_deterministic(self) -> None:
        json_text = render_json(self.matrix)
        csv_text = render_csv(self.matrix)
        html_text = render_html(self.matrix)
        self.assertEqual(json_text, render_json(self.matrix))
        self.assertEqual(csv_text, render_csv(self.matrix))
        self.assertEqual(html_text, render_html(self.matrix))
        self.assertEqual(json.loads(json_text), self.matrix)
        rows = list(csv.DictReader(io.StringIO(csv_text)))
        self.assertEqual(tuple(rows[0]), CSV_COLUMNS)
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[3]["seat_summary_state"], "not_stated")
        self.assertEqual(rows[3]["recorded_seat_values"], "")

    def test_html_is_standalone_and_non_inferential(self) -> None:
        rendered = render_html(self.matrix)
        lowered = rendered.lower()
        self.assertTrue(rendered.startswith("<!doctype html>"))
        self.assertNotIn("<script", lowered)
        self.assertNotIn("<img", lowered)
        self.assertNotIn("http://", lowered)
        self.assertNotIn("https://", lowered)
        self.assertEqual(rendered.count("<tr>"), 7)
        self.assertEqual(rendered.count('data-state="not_stated"'), 2)
        self.assertIn("creates no configuration pair", rendered)
        self.assertIn("ranking, recommendation or inferred value", rendered)

    def test_committed_artifacts_match_the_generator(self) -> None:
        base = REPOSITORY / "data/reporting/portfolio_model_family_comparison_matrix"
        self.assertEqual(
            base.with_suffix(".json").read_text(encoding="utf-8"),
            render_json(self.matrix),
        )
        self.assertEqual(
            base.with_suffix(".csv").read_text(encoding="utf-8"),
            render_csv(self.matrix),
        )
        self.assertEqual(
            base.with_suffix(".html").read_text(encoding="utf-8"),
            render_html(self.matrix),
        )

    def test_cli_writes_all_formats(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            json_path = root / "matrix.json"
            csv_path = root / "matrix.csv"
            html_path = root / "matrix.html"
            result = cli.main(
                [
                    "--json",
                    str(json_path),
                    "--csv",
                    str(csv_path),
                    "--html",
                    str(html_path),
                ],
                repository=REPOSITORY,
            )
            self.assertEqual(result, 0)
            self.assertEqual(
                json_path.read_text(encoding="utf-8"),
                render_json(self.matrix),
            )
            self.assertEqual(
                csv_path.read_text(encoding="utf-8"),
                render_csv(self.matrix),
            )
            self.assertEqual(
                html_path.read_text(encoding="utf-8"),
                render_html(self.matrix),
            )


if __name__ == "__main__":
    unittest.main()
