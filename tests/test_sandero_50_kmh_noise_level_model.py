from __future__ import annotations

import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"

EXPECTED = {
    "sandero_iii_expression_ecog120_manual":
        "src_pl_sandero_expression_ecog120_mt_20260626",
    "sandero_iii_journey_ecog120_manual":
        "src_pl_sandero_journey_ecog120_mt_20260626",
    "sandero_stepway_iii_essential_ecog120_manual":
        "src_pl_sandero_stepway_essential_ecog120_mt_20260626",
    "sandero_stepway_iii_expression_ecog120_automatic":
        "src_pl_sandero_stepway_expression_ecog120_at_20260626",
    "sandero_stepway_iii_expression_ecog120_manual":
        "src_pl_sandero_stepway_expression_ecog120_mt_20260626",
    "sandero_stepway_iii_extreme_ecog120_automatic":
        "src_pl_sandero_stepway_extreme_ecog120_at_20260626",
    "sandero_stepway_iii_extreme_ecog120_manual":
        "src_pl_sandero_stepway_extreme_ecog120_mt_20260626",
}


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class Sandero50KmhNoiseLevelModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.categories = rows("attribute_categories.csv")
        cls.attributes = rows("attributes.csv")
        cls.units = rows("units.csv")
        cls.values = rows("configuration_attribute_values.csv")
        cls.availability = rows("configuration_attribute_availability.csv")
        cls.prices = rows("configuration_prices.csv")
        cls.sources = rows("sources.csv")
        cls.source_configurations = rows("source_configurations.csv")

    def test_acoustics_category_is_defined(self) -> None:
        matches = [
            row for row in self.categories
            if row["code"] == "acoustics"
        ]
        self.assertEqual(
            matches,
            [{
                "code": "acoustics",
                "name": "Acoustics",
                "description": "Vehicle noise and acoustic measurements",
            }],
        )
        self.assertEqual(len(self.categories), 30)

    def test_decibel_unit_is_defined(self) -> None:
        matches = [
            row for row in self.units
            if row["code"] == "sound_level_db"
        ]
        self.assertEqual(
            matches,
            [{
                "code": "sound_level_db",
                "symbol": "dB",
                "name": "Decibel",
                "description": "Noise or sound level in decibels",
            }],
        )
        self.assertEqual(len(self.units), 26)

    def test_speed_specific_attribute_is_active_decimal(self) -> None:
        matches = [
            row for row in self.attributes
            if row["code"] == "noise_level_at_50_kmh"
        ]
        self.assertEqual(len(matches), 1)
        attribute = matches[0]
        self.assertEqual(attribute["id"], "356")
        self.assertEqual(attribute["category"], "Acoustics")
        self.assertEqual(attribute["name"], "Noise level at 50 km/h")
        self.assertEqual(attribute["data_type"], "decimal")
        self.assertEqual(attribute["unit"], "dB")
        self.assertEqual(attribute["status"], "active")
        self.assertGreaterEqual(len(self.attributes), 349)

    def test_speed_condition_is_not_reduced_to_generic_noise(self) -> None:
        noise_codes = {
            row["code"]
            for row in self.attributes
            if "noise" in row["code"]
        }
        self.assertEqual(noise_codes, {"noise_level_at_50_kmh"})
        self.assertNotIn("noise_level", noise_codes)
        self.assertNotIn("interior_noise_level", noise_codes)
        self.assertNotIn("exterior_noise_level", noise_codes)

    def test_configuration_values_preserve_speed_specific_attribute(self) -> None:
        noise_values = [
            row
            for row in self.values
            if row["attribute_code"] == "noise_level_at_50_kmh"
        ]
        self.assertEqual(len(noise_values), 7)
        self.assertEqual(
            {row["value"] for row in noise_values},
            {"67"},
        )
        self.assertFalse(
            any(
                row["attribute_code"] in {
                    "noise_level",
                    "interior_noise_level",
                    "exterior_noise_level",
                }
                for row in self.values
            ),
        )
        self.assertGreaterEqual(len(self.values), 232)

    def test_model_package_does_not_change_availability_or_prices(self) -> None:
        self.assertEqual(
            len([
                row for row in self.availability
                if not row["configuration_code"].startswith(("duster_iii_", "jogger_"))
            ]),
            419,
        )
        self.assertEqual(
            len([
                row for row in self.prices
                if row["configuration_code"] in EXPECTED
            ]),
            7,
        )
        self.assertFalse(
            any(
                "noise_level_at_50_kmh" in row["code"]
                for row in self.prices
            ),
        )

    def test_source_registry_and_mapping_are_unchanged(self) -> None:
        expected_sources = set(EXPECTED.values())
        self.assertEqual(
            {row["code"] for row in self.sources if row["code"] in expected_sources},
            expected_sources,
        )
        self.assertEqual(
            {
                row["configuration_code"]: row["source_code"]
                for row in self.source_configurations
                if row["configuration_code"] in EXPECTED
            },
            EXPECTED,
        )


if __name__ == "__main__":
    unittest.main()
