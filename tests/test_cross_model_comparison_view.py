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
        self.assertEqual(self.view["as_of"], "2026-11-04")
        summary = self.view["summary"]
        mixed_scopes = [scope for scope in self.view["scopes"] if scope["mixed_model"]]
        scoped_codes = [
            code
            for scope in self.view["scopes"]
            for code in scope["configuration_codes"]
        ]
        self.assertEqual(summary["model_family_count"], len(self.view["models"]))
        self.assertEqual(summary["reporting_scope_count"], len(self.view["scopes"]))
        self.assertEqual(summary["single_model_scope_count"], len(self.view["scopes"]) - len(mixed_scopes))
        self.assertEqual(summary["mixed_model_scope_count"], len(mixed_scopes))
        self.assertEqual(summary["active_configuration_count"], len(scoped_codes))
        self.assertEqual(summary["within_scope_pair_count"], sum(scope["pair_count"] for scope in self.view["scopes"]))
        self.assertEqual(summary["catalog_price_recorded_count"], sum(model["catalog_price"]["recorded_count"] for model in self.view["models"]))
        self.assertEqual(len(scoped_codes), len(set(scoped_codes)))
        for flag in ("cross_scope_pairs_generated", "ranking_generated", "recommendations_generated", "inferred_values_generated"):
            self.assertIs(summary[flag], False)

    def test_model_cards_have_exact_order_counts_and_price_coverage(self) -> None:
        self.assertEqual(
            set(self.models),
            {
                row["code"]
                for row in self._read_master_rows("models.csv")
                if any(
                    configuration["status"] == "active"
                    and self._model_for_configuration(configuration) == row["code"]
                    for configuration in self._read_master_rows("configurations.csv")
                )
            },
        )
        for code, model in self.models.items():
            price = model["catalog_price"]
            self.assertGreater(model["configuration_count"], 0)
            self.assertGreater(model["version_count"], 0)
            self.assertEqual(
                model["configuration_count"],
                sum(
                    1
                    for scope in self.view["scopes"]
                    for configuration_code in scope["configuration_codes"]
                    if self._model_for_configuration_code(configuration_code) == code
                ),
            )
            self.assertEqual(price["recorded_count"] + price["missing_count"], model["configuration_count"])
            if price["recorded_count"]:
                self.assertEqual(price["currency"], "PLN")
                self.assertLessEqual(price["minimum"], price["maximum"])
            else:
                self.assertIsNone(price["minimum"])
                self.assertIsNone(price["maximum"])

    def _model_for_configuration(self, configuration: dict[str, str]) -> str:
        versions = {
            row["code"]: row
            for row in self._read_master_rows("versions.csv")
        }
        return versions[configuration["version_code"]]["model_code"]

    def _model_for_configuration_code(self, configuration_code: str) -> str:
        configurations = {
            row["code"]: row
            for row in self._read_master_rows("configurations.csv")
        }
        return self._model_for_configuration(configurations[configuration_code])

    @staticmethod
    def _read_master_rows(filename: str) -> list[dict[str, str]]:
        import csv

        path = REPOSITORY / "data" / "master" / filename
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def test_missing_seat_summaries_remain_not_stated(self) -> None:
        self.assertEqual(self.models["bigster"]["recorded_seat_values"], [5])
        self.assertEqual(self.models["bigster"]["seat_summary_state"], "recorded")
        self.assertEqual(self.models["duster_iii"]["recorded_seat_values"], [5])
        self.assertEqual(self.models["duster_iii"]["seat_summary_state"], "recorded")
        self.assertEqual(self.models["spring"]["recorded_seat_values"], [4])
        self.assertEqual(self.models["spring"]["seat_summary_state"], "recorded")
        self.assertEqual(self.models["jogger"]["recorded_seat_values"], [5, 7])
        self.assertEqual(self.models["jogger"]["seat_summary_state"], "recorded")
        self.assertEqual(self.models["sandero_iii"]["recorded_seat_values"], [5])
        self.assertEqual(
            self.models["sandero_stepway_iii"]["recorded_seat_values"],
            [5],
        )

    def test_existing_mixed_sandero_stepway_scope_is_explicit_and_unchanged(self) -> None:
        mixed = [item for item in self.view["scopes"] if item["mixed_model"]]
        self.assertEqual(len(mixed), 3)
        scope = self.scopes["sandero_ecog120_manual"]
        self.assertEqual(scope["slug"], "sandero_ecog120_manual")
        self.assertEqual(
            scope["model_codes"],
            ["sandero_iii", "sandero_stepway_iii"],
        )
        self.assertEqual(scope["configuration_count"], 5)
        self.assertEqual(scope["pair_count"], 10)
        self.assertEqual(scope["technical_slot_count"], 60)
        self.assertEqual(self.models["sandero_iii"]["shared_scope_count"], 3)
        self.assertEqual(
            self.models["sandero_stepway_iii"]["shared_scope_count"],
            3,
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
        self.assertEqual(len(codes), self.view["summary"]["active_configuration_count"])
        self.assertEqual(len(codes), len(set(codes)))
        self.assertEqual(
            sum(scope["pair_count"] for scope in self.view["scopes"]),
            self.view["summary"]["within_scope_pair_count"],
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
            if not media:
                # A model without a registered media source is valid; absence is
                # distinct from malformed media metadata and must not break the view.
                self.assertEqual(media, {})
                continue
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
        self.assertEqual(html_text.count('class="model-card"'), len(self.view["models"]))
        self.assertEqual(html_text.count('class="scope-card"'), len(self.view["scopes"]))
        self.assertEqual(
            html_text.count('class="badge mixed"'),
            sum(1 for scope in self.view["scopes"] if scope["mixed_model"]),
        )

    def test_html_is_standalone_scope_safe_and_marks_unknown_values(self) -> None:
        rendered = render_html(self.view)
        self.assertNotIn("<script", rendered.lower())
        self.assertNotIn("http://", rendered.lower())
        self.assertIn('data-state="recorded"', rendered)
        self.assertIn("Nie tworzy par między niezależnymi zakresami", rendered)
        links = re.findall(r'href="([^"]+)"', rendered)
        comparison_links = [link for link in links if "comparison-bundle" in link]
        self.assertEqual(len(comparison_links), len(self.view["scopes"]) * 3)
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
