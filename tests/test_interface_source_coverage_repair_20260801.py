from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))

import configuration_shortlist  # noqa: E402

SOURCE = "src_pl_sandero_stepway_price_my26_20260703"
EXPECTED_MAPPINGS = {
    ("sandero_rear_view_camera_option", "sandero_iii_expression_tce100_manual", "700"),
    ("sandero_rear_view_camera_option", "sandero_iii_expression_ecog120_automatic", "700"),
    ("sandero_media_nav_live_option", "sandero_iii_expression_tce100_manual", "1600"),
    ("sandero_media_nav_live_option", "sandero_iii_expression_ecog120_automatic", "1600"),
    ("sandero_media_nav_live_option", "sandero_stepway_iii_expression_tce110_manual", "1600"),
    ("sandero_glass_sunroof_option", "sandero_stepway_iii_extreme_tce110_manual", "2200"),
    ("sandero_comfort_auto_package", "sandero_iii_expression_ecog120_automatic", "2000"),
    ("sandero_thermo_package", "sandero_iii_expression_tce100_manual", "1900"),
    ("sandero_thermo_package", "sandero_iii_expression_ecog120_automatic", "1900"),
    ("sandero_thermo_package", "sandero_stepway_iii_expression_tce110_manual", "1900"),
    ("sandero_winter_package", "sandero_iii_journey_tce100_manual", "1200"),
    ("sandero_winter_package", "sandero_iii_journey_ecog120_automatic", "1200"),
    ("sandero_winter_package", "sandero_stepway_iii_extreme_tce110_manual", "1200"),
    ("sandero_media_nav_live_package", "sandero_iii_journey_tce100_manual", "1600"),
    ("sandero_media_nav_live_package", "sandero_iii_journey_ecog120_automatic", "1600"),
    ("sandero_media_nav_live_package", "sandero_stepway_iii_extreme_tce110_manual", "1600"),
    ("sandero_easy_package", "sandero_iii_journey_tce100_manual", "1600"),
    ("sandero_easy_package", "sandero_iii_journey_ecog120_automatic", "1600"),
    ("sandero_easy_package", "sandero_stepway_iii_extreme_tce110_manual", "1600"),
}


def read_csv(name: str) -> list[dict[str, str]]:
    path = REPOSITORY / "data" / "master" / name
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class InterfaceSourceCoverageRepairTests(unittest.TestCase):
    def test_spring_official_media_is_registered_and_applied(self) -> None:
        source_path = (
            REPOSITORY
            / "project/sources/dacia-pl-spring-model-media-20260801.json"
        )
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        spring = payload["models"]["spring"]
        self.assertTrue(spring["image_url"].startswith("https://www.dacia.pl/"))
        self.assertEqual(
            spring["source_page_url"],
            "https://www.dacia.pl/hybrydy-i-elektryczne/spring-miejski.html",
        )
        catalog = {
            "facets": {"models": [{"code": "spring", "media": {}}]},
            "configurations": [
                {"configuration_code": "spring_test", "model_code": "spring"}
            ],
        }
        configuration_shortlist._apply_supplemental_model_media(
            catalog,
            REPOSITORY,
        )
        self.assertEqual(
            catalog["configurations"][0]["model_media"]["image_url"],
            spring["image_url"],
        )
        self.assertEqual(
            catalog["facets"]["models"][0]["media"]["source_name"],
            "Dacia Polska",
        )

    def test_all_exact_sandero_price_mappings_are_materialized(self) -> None:
        rows = read_csv("commercial_item_configurations.csv")
        actual = {
            (
                row["commercial_item_code"],
                row["configuration_code"],
                row["amount"],
            )
            for row in rows
            if row["source_code"] == SOURCE
            and row["price_date"] == "2026-07-03"
        }
        self.assertTrue(EXPECTED_MAPPINGS.issubset(actual))
        for item_code, configuration_code, amount in EXPECTED_MAPPINGS:
            matches = [
                row
                for row in rows
                if row["commercial_item_code"] == item_code
                and row["configuration_code"] == configuration_code
                and row["amount"] == amount
                and row["source_code"] == SOURCE
            ]
            self.assertEqual(len(matches), 1, (item_code, configuration_code))
            self.assertEqual(matches[0]["availability_status"], "optional")
            self.assertEqual(matches[0]["currency_code"], "PLN")

    def test_sandero_tce100_direct_injection_remains_source_backed(self) -> None:
        rows = read_csv("configuration_attribute_values.csv")
        expected = {
            "sandero_iii_essential_tce100_manual",
            "sandero_iii_expression_tce100_manual",
            "sandero_iii_journey_tce100_manual",
        }
        matches = {
            row["configuration_code"]: row
            for row in rows
            if row["configuration_code"] in expected
            and row["attribute_code"] == "injection_type"
            and row["value"] == "direct_injection"
        }
        self.assertEqual(set(matches), expected)
        self.assertTrue(
            all(row["source_code"] == SOURCE for row in matches.values())
        )
        self.assertTrue(
            all(row["observation_date"] == "2026-07-03" for row in matches.values())
        )

    def test_interface_distinguishes_missing_states_and_provenance(self) -> None:
        selection = (
            REPOSITORY
            / "tools/reporting/configuration_shortlist_selection.js"
        ).read_text(encoding="utf-8")
        pricing = (
            REPOSITORY
            / "tools/reporting/configuration_shortlist_v12_pricing.js"
        ).read_text(encoding="utf-8")
        self.assertIn("brak wpisu w bazie", selection)
        self.assertIn("brak powiązania z cennikiem", selection)
        self.assertIn("cena niepodana w źródle", selection)
        self.assertIn("comparisonValueTitle", selection)
        self.assertIn("equipmentComparisonTitle", selection)
        self.assertIn("comparison-source-note", selection)
        self.assertIn("brak powiązania z cennikiem", pricing)
        self.assertIn("cena niepodana w źródle", pricing)
        self.assertNotIn("Nieznane dopłaty", pricing)


if __name__ == "__main__":
    unittest.main()
