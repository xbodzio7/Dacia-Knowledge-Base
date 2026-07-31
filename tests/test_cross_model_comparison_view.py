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
        self.assertEqual(self.view["as_of"], "2026-07-25")
        self.assertEqual(
            self.view["summary"],
            {
                "model_family_count": 5,
                "reporting_scope_count": 20,
                "single_model_scope_count": 18,
                "mixed_model_scope_count": 2,
                "active_configuration_count": 78,
                "within_scope_pair_count": 129,
                "catalog_price_recorded_count": 78,
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
            ],
        )
        expected = {
            "sandero_iii": (7, 3, 63900, 80500, 7),
            "sandero_stepway_iii": (8, 3, 71700, 89400, 8),
            "jogger": (22, 4, 77900, 118050, 22),
            "duster_iii": (27, 5, 82000, 123600, 27),
            "bigster": (14, 4, 101400, 137600, 14),
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
        self.assertEqual(self.models["bigster"]["seat_summary_state"], "not_stated")
        self.assertEqual(self.models["duster_iii"]["recorded_seat_values"], [])
        self.assertEqual(self.models["duster_iii"]["seat_summary_state"], "not_stated")
        self.assertEqual(self.models["jogger"]["recorded_seat_values"], [5, 7])
        self.assertEqual(self.models["jogger"]["seat_summary_state"], "recorded")
        self.assertEqual(self.models["sandero_iii"]["recorded_seat_values"], [5])
        self.assertEqual(
            self.models["sandero_stepway_iii"]["recorded_seat_values"],
            [5],
        )

    def test_existing_mixed_sandero_stepway_scope_is_explicit_and_unchanged(self) -> None:
        mixed = [item for item in self.view["scopes"] if item["mixed_model"]]
        self.assertEqual(len(mixed), 2)
        scope = self.scopes["sandero_ecog120_manual"]
        self.assertEqual(scope["slug"], "sandero_ecog120_manual")
        self.assertEqual(
            scope["model_codes"],
            ["sandero_iii", "sandero_stepway_iii"],
        )
        self.assertEqual(scope["configuration_count"], 5)
        self.assertEqual(scope["pair_count"], 10)
        self.assertEqual(scope["technical_slot_count"], 60)
        self.assertEqual(self.models["sandero_iii"]["shared_scope_count"], 2)
        self.assertEqual(
            self.models["sandero_stepway_iii"]["shared_scope_count"],
            2,
        )
        tce_scope = self.scopes["sandero_tce100_stepway_tce110_manual"]
        self.assertEqual(tce_scope["configuration_count"], 6)
        self.assertEqual(tce_scope["pair_count"], 15)
        self.assertEqual(tce_scope["technical_slot_count"], 48)

    def test_every_configuration_occurs_once_and_pairs_stay_inside_scopes(self) -> None:
        codes = [
            code
            for scope in self.view["scopes"]
            for code in scope["configuration_codes"]
        ]
        self.assertEqual(len(codes), 80)
        self.assertEqual(len(codes), len(set(codes)))
        self.assertEqual(
            sum(scope["pair_count"] for scope in self.view["scopes"]),
            129,
        )
        self.assertTrue(
            all(
                scope["pair_count"]
                == scope["configuration_count"]
                * (scope["configuration_count"] - 1)
                // 2
                for scope in self.view["scopes"]
            )
        )
        self.assertFalse(self.view["summary"]["cross_scope_pairs_generated"])

    def test_scope_links_target_only_existing_bundle_outputs(self) -> None:
        for slug, scope in self.scopes.items():
            paths = scope["comparison_paths"]
            self.assertEqual(
                paths["html"],
                f"../comparison-bundle/{slug}.comparison.html",
            )
            self.assertEqual(
                paths["json"],
                f"../comparison-bundle/{slug}.comparison.json",
            )
            self.assertEqual(
                paths["markdown"],
                f"../comparison-bundle/{slug}.comparison.md",
            )
            self.assertEqual(
                paths["differences_csv"],
                f"../comparison-bundle/{slug}.differences.csv",
            )
        self.assertIn(
            "never generate a configuration pair",
            self.view["navigation"]["pair_generation_rule"],
        )

    def test_model_media_registry_is_reused_as_provenance_not_runtime_dependency(self) -> None:
        for model in self.view["models"]:
            media = model["model_media"]
            self.assertEqual(media["source_name"], "Dacia Polska")
            self.assertTrue(media["image_url"].startswith("https://"))
            self.assertTrue(media["source_page_url"].startswith("https://www.dacia.pl/"))
        html = render_html(self.view)
        self.assertNotIn("<img", html.lower())
        self.assertIn("oficjalna strona modelu", html)

    def test_json_and_html_rendering_are_deterministic(self) -> None:
        json_text = render_json(self.view)
        html_text = render_html(self.view)
        self.assertEqual(json_text, render_json(self.view))
        self.assertEqual(html_text, render_html(self.view))
        self.assertEqual(json.loads(json_text), self.view)
        self.assertTrue(html_text.startswith("<!doctype html>"))
        self.assertEqual(html_text.count('class="model-card"'), 5)
        self.assertEqual(html_text.count('class="scope-card"'), 20)
        self.assertEqual(html_text.count('class="badge mixed"'), 2)

    def test_html_is_standalone_scope_safe_and_marks_unknown_values(self) -> None:
        rendered = render_html(self.view)
        self.assertNotIn("<script", rendered.lower())
        self.assertNotIn("http://", rendered.lower())
        self.assertIn('data-state="not_stated">nie podano</dd>', rendered)
        self.assertIn("Nie tworzy par między niezależnymi zakresami", rendered)
        links = re.findall(r'href="([^"]+)"', rendered)
        comparison_links = [link for link in links if "comparison-bundle" in link]
        self.assertEqual(len(comparison_links), 60)
        self.assertTrue(
            all(link.startswith("../comparison-bundle/") for link in comparison_links)
        )
        self.assertNotIn("ranking", rendered.lower().split("<footer>")[0][-250:])

    def test_cli_writes_both_formats_and_reports_scope_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            json_path = root / "view.json"
            html_path = root / "view.html"
            result = cli.main(
                ["--json", str(json_path), "--html", str(html_path)],
                repository=REPOSITORY,
            )
            self.assertEqual(result, 0)
            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), self.view)
            self.assertEqual(html_path.read_text(encoding="utf-8"), render_html(self.view))


if __name__ == "__main__":
    unittest.main()
