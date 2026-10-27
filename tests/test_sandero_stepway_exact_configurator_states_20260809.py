from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = (
    ROOT
    / "project/sources/dacia-pl-sandero-stepway-exact-configurator-states-20260809.json"
)
SCOPE = (
    ROOT
    / "project/sources/dacia-pl-sandero-stepway-current-configurator-scope-20260808.json"
)


class SanderoStepwayExactConfiguratorStatesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
        cls.scope = json.loads(SCOPE.read_text(encoding="utf-8"))
        with (ROOT / "data/master/configuration_prices.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            cls.prices = list(csv.DictReader(handle))

    def test_all_current_scope_configurations_have_one_exact_state(self) -> None:
        expected = {
            configuration["configuration_code"]
            for page in self.scope["official_pages"]
            for configuration in page["configurations"]
        }
        observed = [
            configuration["configuration_code"]
            for configuration in self.capture["configurations"]
        ]
        self.assertEqual(len(observed), 15)
        self.assertEqual(len(set(observed)), 15)
        self.assertEqual(set(observed), expected)

    def test_reopened_surface_summary_is_exact(self) -> None:
        self.assertEqual(
            self.capture["summary"],
            {
                "exact_configuration_surfaces": 15,
                "sandero_surfaces": 7,
                "sandero_stepway_surfaces": 8,
                "formerly_source_blocked_surfaces_reopened": 13,
                "surfaces_with_stable_conf_url": 15,
                "surfaces_with_complete_visible_colour_list": 15,
                "surfaces_with_visible_wheel_list": 15,
                "surfaces_with_visible_upholstery_list": 15,
                "surfaces_with_visible_factory_option_list": 15,
                "master_rows_created": 0,
            },
        )

    def test_every_surface_is_exact_and_nonempty(self) -> None:
        for configuration in self.capture["configurations"]:
            with self.subTest(configuration=configuration["configuration_code"]):
                self.assertIn("?conf=", configuration["exact_state_url"])
                self.assertTrue(configuration["grade"])
                self.assertTrue(configuration["engine"])
                self.assertTrue(configuration["descriptor"])
                self.assertTrue(configuration["colours"])
                self.assertTrue(configuration["wheels"])
                self.assertTrue(configuration["upholsteries"])
                self.assertIn(
                    configuration["selected_colour"], configuration["colours"]
                )
                self.assertIn(
                    configuration["selected_wheel"], configuration["wheels"]
                )
                self.assertIn(
                    configuration["selected_upholstery"],
                    configuration["upholsteries"],
                )
                self.assertTrue(configuration["factory_options"])
                self.assertTrue(configuration["technical_highlights"])
                self.assertNotIn("accessories", configuration)

    def test_captured_prices_match_current_canonical_prices(self) -> None:
        current_prices = {
            row["configuration_code"]: int(row["amount"])
            for row in self.prices
            if row["price_type"] == "catalog_gross"
        }
        self.assertEqual(
            {
                item["configuration_code"]: item["catalog_price_pln"]
                for item in self.capture["configurations"]
            },
            {
                item["configuration_code"]: current_prices[item["configuration_code"]]
                for item in self.capture["configurations"]
            },
        )

    def test_capture_preserves_non_projection_boundaries(self) -> None:
        self.assertEqual(self.capture["observed_on"], "2026-08-09")
        self.assertEqual(self.capture["market"], "PL")
        self.assertEqual(self.capture["publisher"], "Dacia")
        self.assertIn(
            "No appearance, option or technical observation is projected to another configuration.",
            self.capture["normalization_boundaries"],
        )


if __name__ == "__main__":
    unittest.main()
