from __future__ import annotations

import csv
import json
import sys
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))

import configuration_shortlist  # noqa: E402

PRICE_SOURCE = "src_pl_sandero_stepway_price_my26_20260703"
TECHNICAL_SOURCE = "src_pl_sandero_stepway_catalog_tce_slice_20260703"
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
        self.assertTrue(
            spring["image_url"].startswith(
                configuration_shortlist._OFFICIAL_MEDIA_PREFIXES
            )
        )
        self.assertTrue(
            spring["image_url"].startswith("https://3dv2.renault.com/")
        )
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
            if row["source_code"] == PRICE_SOURCE
            and row["price_date"] == "2026-07-03"
        }
        self.assertTrue(EXPECTED_MAPPINGS.issubset(actual))

    def test_sandero_direct_injection_evidence_is_preserved(self) -> None:
        values = read_csv("configuration_attribute_values.csv")
        actual = {
            row["configuration_code"]
            for row in values
            if row["attribute_code"] == "fuel_injection_type"
            and row["value_enum"] == "direct_injection"
            and row["source_code"] == TECHNICAL_SOURCE
            and row["observation_date"] == "2026-07-03"
        }
        self.assertEqual(
            actual,
            {
                "sandero_iii_essential_tce100_manual",
                "sandero_iii_expression_tce100_manual",
                "sandero_iii_journey_tce100_manual",
            },
        )


if __name__ == "__main__":
    unittest.main()
