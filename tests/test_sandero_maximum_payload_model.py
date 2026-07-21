from __future__ import annotations

import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"

EXPECTED_MAPPING = {
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
    with (MASTER / name).open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        return list(csv.DictReader(handle))


class SanderoMaximumPayloadModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.categories = rows("attribute_categories.csv")
        cls.attributes = rows("attributes.csv")
        cls.units = rows("units.csv")
        cls.values = rows("configuration_attribute_values.csv")
        cls.availability = rows(
            "configuration_attribute_availability.csv"
        )
        cls.prices = rows("configuration_prices.csv")
        cls.sources = rows("sources.csv")
        cls.source_configurations = rows("source_configurations.csv")

    def test_existing_weight_category_and_mass_unit_are_reused(self) -> None:
        weights = [
            row
            for row in self.categories
            if row["code"] == "weights"
        ]
        self.assertEqual(
            weights,
            [{
                "code": "weights",
                "name": "Weights",
                "description": "Vehicle mass and gross weight ratings",
            }],
        )
        mass_kg = [
            row
            for row in self.units
            if row["code"] == "mass_kg"
        ]
        self.assertEqual(
            mass_kg,
            [{
                "code": "mass_kg",
                "symbol": "kg",
                "name": "Kilogram",
                "description": "Mass in kilograms",
            }],
        )
        self.assertEqual(len(self.categories), 30)
        self.assertEqual(len(self.units), 26)

    def test_maximum_payload_is_active_integer_weight(self) -> None:
        matches = [
            row
            for row in self.attributes
            if row["code"] == "maximum_payload"
        ]
        self.assertEqual(len(matches), 1)
        self.assertEqual(
            matches[0],
            {
                "id": "357",
                "code": "maximum_payload",
                "category": "Weights",
                "name": "Maximum payload",
                "data_type": "integer",
                "unit": "kg",
                "description": (
                    "Maximum permitted payload stated explicitly by the "
                    "source without deriving it from other mass values"
                ),
                "status": "active",
            },
        )
        self.assertGreaterEqual(len(self.attributes), 350)

    def test_payload_remains_distinct_from_other_mass_concepts(self) -> None:
        expected = {
            "roof_load": ("Capacities", "Maximum roof load"),
            "braked_trailer_weight": (
                "Towing",
                "Maximum braked trailer weight",
            ),
            "unbraked_trailer_weight": (
                "Towing",
                "Maximum unbraked trailer weight",
            ),
            "kerb_weight": ("Weights", "Kerb weight"),
            "gross_vehicle_weight": (
                "Weights",
                "Gross vehicle weight",
            ),
            "gross_train_weight": (
                "Weights",
                "Gross train weight",
            ),
            "maximum_payload": ("Weights", "Maximum payload"),
        }
        actual = {
            row["code"]: (row["category"], row["name"])
            for row in self.attributes
            if row["code"] in expected
        }
        self.assertEqual(actual, expected)
        self.assertNotIn("payload", actual)
        self.assertNotIn("cargo_payload", actual)

    def test_import_uses_existing_maximum_payload_attribute(self) -> None:
        payload_values = [
            row
            for row in self.values
            if row["attribute_code"] == "maximum_payload"
        ]
        self.assertEqual(len(payload_values), 7)
        self.assertEqual(
            {row["configuration_code"] for row in payload_values},
            set(EXPECTED_MAPPING),
        )
        self.assertGreaterEqual(len(self.values), 246)

    def test_existing_mass_values_are_not_rewritten(self) -> None:
        counts = {
            code: sum(
                row["attribute_code"] == code
                and row["configuration_code"] in EXPECTED_MAPPING
                for row in self.values
            )
            for code in {
                "kerb_weight",
                "gross_vehicle_weight",
                "gross_train_weight",
                "braked_trailer_weight",
                "unbraked_trailer_weight",
            }
        }
        self.assertEqual(
            counts,
            {
                "kerb_weight": 7,
                "gross_vehicle_weight": 7,
                "gross_train_weight": 7,
                "braked_trailer_weight": 7,
                "unbraked_trailer_weight": 7,
            },
        )

    def test_model_package_does_not_change_availability_or_prices(
        self,
    ) -> None:
        self.assertEqual(
            len([
                row for row in self.availability
                if not row["configuration_code"].startswith(("duster_iii_", "jogger_"))
                and row["observation_date"] == "2026-06-26"
            ]),
            419,
        )
        self.assertEqual(
            len([
                row for row in self.prices
                if row["configuration_code"] in EXPECTED_MAPPING
                and row["price_date"] == "2026-06-26"
            ]),
            7,
        )
        self.assertFalse(
            any(
                "maximum_payload" in row["code"]
                for row in self.prices
            ),
        )

    def test_source_registry_and_mapping_are_unchanged(self) -> None:
        expected_sources = set(EXPECTED_MAPPING.values())
        self.assertEqual(
            {row["code"] for row in self.sources if row["code"] in expected_sources},
            expected_sources,
        )
        registered_pairs = {
            (row["configuration_code"], row["source_code"])
            for row in self.source_configurations
        }
        self.assertTrue(set(EXPECTED_MAPPING.items()) <= registered_pairs)


if __name__ == "__main__":
    unittest.main()
