from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))

import cross_model_comparison_view as cli  # noqa: E402
from reporting.cross_model_comparison_view import (  # noqa: E402
    collect_view,
    render_html,
    render_json,
)


class CrossModelComparisonViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.view = collect_view(REPOSITORY)
        cls.models = {
            item["model_code"]: item
            for item in cls.view["models"]
        }
        cls.scopes = {
            item["slug"]: item
            for item in cls.view["scopes"]
        }

    def test_summary_matches_scope_preserving_repository_baseline(self) -> None:
        self.assertEqual(self.view["version"], 1)
        self.assertEqual(
            self.view["kind"],
            "scope_preserving_cross_model_comparison_view",
        )
        self.assertEqual(self.view["as_of"], "2026-08-02")
        self.assertEqual(
            self.view["summary"],
            {
                "model_family_count": 6,
                "reporting_scope_count": 22,
                "single_model_scope_count": 20,
                "mixed_model_scope_count": 2,
                "active_configuration_count": 81,
                "within_scope_pair_count": 130,
                "catalog_price_recorded_count": 81,
                "cross_scope_pairs_generated": False,
                "ranking_generated": False,
                "recommendations_generated": False,
                "inferred_values_generated": False,
            },
        )

    def test_model_cards_have_exact_order_counts_and_price_coverage(self) -> None:
        self.assertEqual(
            [item["model_code"] for item in self.view["models"]],
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
            "sandero_iii": (7, 3, 63900, 80500, 7),
            "sandero_stepway_iii": (8, 3, 71700, 89400, 8),
            "jogger": (22, 4, 77900, 118050, 22),
            "duster_iii": (27, 5, 82000, 123600, 27),
            "bigster": (14, 4, 101400, 137600, 14),
            "spring": (3, 3, 73500, 85900, 3),
        }
        for code, values in expected.items():
            model = self.models[code]
            price = model["catalog_price"]
            self.assertEqual(model["configuration_count"], values[0])
            self.assertEqual(model["version_count"], values[1])
            self.assertEqual(price["minimum"], values[2])
            self.assertEqual(price["maximum"], values[3])
            self.assertEqual(price["recorded_count"], values[4])
            self.assertEqual(price["missing_count"], 0)
            self.assertEqual(price["currency"], "PLN")

    def test_missing_seat_summaries_remain_not_stated(self) -> None:
        self.assertEqual(self.models["bigster"]["recorded_seat_values"], [])
        self.assertEqual(self.models["spring"]["recorded_seat_values"], [])
        self.assertEqual(self.models["bigster"]["seat_summary"], "not_stated")
        self.assertEqual(self.models["spring"]["seat_summary"], "not_stated")

    def test_scope_rows_preserve_single_scope_comparison_boundaries(self) -> None:
        self.assertEqual(
            self.scopes["sandero_iii_ecog120_manual"]["configuration_count"],
            3,
        )
        self.assertEqual(
            self.scopes["sandero_iii_ecog120_automatic"]["configuration_count"],
            2,
        )
        self.assertEqual(
            self.scopes["sandero_stepway_iii_ecog120_manual"]["configuration_count"],
            3,
        )
        self.assertEqual(
            self.scopes["sandero_stepway_iii_ecog120_automatic"]["configuration_count"],
            2,
        )
        self.assertEqual(
            self.scopes["spring_electric70_automatic"]["configuration_count"],
            2,
        )
        self.assertEqual(
            self.scopes["spring_electric100_automatic"]["configuration_count"],
            1,
        )

    def test_json_render_is_deterministic(self) -> None:
        first = render_json(self.view)
        second = render_json(collect_view(REPOSITORY))
        self.assertEqual(first, second)
        parsed = json.loads(first)
        self.assertEqual(parsed["kind"], self.view["kind"])

    def test_html_render_has_workspace_navigation_and_no_cross_scope_ranking(self) -> None:
        html = render_html(self.view)
        self.assertIn("Dacia Knowledge Base", html)
        self.assertIn("Porównanie modeli", html)
        self.assertIn("Wybierz zakres raportowania", html)
        self.assertNotIn("ranking", html.lower())
        self.assertNotIn("rekomend", html.lower())
        self.assertNotIn("cross-scope", html.lower())
        self.assertNotIn("cross_scope", html.lower())
        self.assertRegex(html, re.compile(r"href=\"[^\"]*configuration-comparison\.html"))

    def test_cli_writes_json_and_html(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            json_path = output_dir / "view.json"
            html_path = output_dir / "view.html"
            self.assertEqual(
                cli.main(
                    [
                        "--root",
                        str(REPOSITORY),
                        "--json-output",
                        str(json_path),
                        "--html-output",
                        str(html_path),
                    ]
                ),
                0,
            )
            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), self.view)
            self.assertIn("Porównanie modeli", html_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
