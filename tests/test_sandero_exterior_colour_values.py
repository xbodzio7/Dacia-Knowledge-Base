from __future__ import annotations

import csv
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
MASTER = REPOSITORY / "data" / "master"
CATEGORIES_PATH = MASTER / "attribute_categories.csv"
ATTRIBUTES_PATH = MASTER / "attributes.csv"
VALUES_PATH = MASTER / "configuration_attribute_values.csv"
AVAILABILITY_PATH = MASTER / "configuration_attribute_availability.csv"
PRICES_PATH = MASTER / "configuration_prices.csv"
SOURCE_CONFIGURATIONS_PATH = MASTER / "source_configurations.csv"

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


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SanderoExteriorColourValueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.categories = read_rows(CATEGORIES_PATH)
        cls.attributes = read_rows(ATTRIBUTES_PATH)
        cls.all_values = read_rows(VALUES_PATH)
        cls.rows = [
            row
            for row in cls.all_values
            if 198 <= int(row["id"]) <= 204
        ]
        cls.availability = read_rows(AVAILABILITY_PATH)
        cls.prices = read_rows(PRICES_PATH)
        cls.source_configurations = read_rows(SOURCE_CONFIGURATIONS_PATH)

    def test_exterior_category_and_attribute_are_defined(self) -> None:
        categories = {
            row["name"]: row
            for row in self.categories
            if row["name"] == "Exterior"
        }
        self.assertEqual(set(categories), {"Exterior"})
        self.assertEqual(categories["Exterior"]["code"], "exterior")

        attributes = {
            row["code"]: row
            for row in self.attributes
            if row["code"] == "exterior_color"
        }
        self.assertEqual(set(attributes), {"exterior_color"})
        attribute = attributes["exterior_color"]
        self.assertEqual(attribute["id"], "354")
        self.assertEqual(attribute["category"], "Exterior")
        self.assertEqual(attribute["data_type"], "string")
        self.assertEqual(attribute["status"], "active")
        self.assertEqual(attribute["unit"], "")

    def test_package_ids_shape_and_count(self) -> None:
        self.assertGreaterEqual(len(self.categories), 29)
        self.assertGreaterEqual(len(self.attributes), 347)
        self.assertGreaterEqual(len(self.all_values), 204)
        self.assertEqual(len(self.rows), 7)
        self.assertEqual(
            {int(row["id"]) for row in self.rows},
            set(range(198, 205)),
        )
        self.assertEqual(
            list(self.rows[0]),
            [
                "id", "code", "configuration_code", "attribute_code",
                "fuel_type_code", "value", "observation_date",
                "source_code", "notes",
            ],
        )

    def test_manifest_matches_all_configurations_and_sources(self) -> None:
        actual = {
            row["configuration_code"]: row["source_code"]
            for row in self.rows
        }
        self.assertEqual(actual, EXPECTED)
        self.assertEqual(len(actual), 7)
        self.assertEqual(
            {row["observation_date"] for row in self.rows},
            {"2026-06-26"},
        )
        self.assertEqual(
            {row["fuel_type_code"] for row in self.rows},
            {""},
        )

    def test_values_and_notes_preserve_source_wording(self) -> None:
        self.assertEqual(
            {row["attribute_code"] for row in self.rows},
            {"exterior_color"},
        )
        self.assertEqual(
            {row["value"] for row in self.rows},
            {"biel alpejska"},
        )
        self.assertEqual(
            {row["notes"] for row in self.rows},
            {"Source page 2, section Kolor: biel alpejska 0 zł"},
        )

    def test_zero_price_is_provenance_not_configuration_value(self) -> None:
        self.assertTrue(all(row["value"] != "0 zł" for row in self.rows))
        self.assertTrue(all("0 zł" in row["notes"] for row in self.rows))
        self.assertEqual(
            len([
                row for row in self.prices
                if row["configuration_code"] in EXPECTED
            ]),
            7,
        )
        self.assertFalse(
            any("exterior_color" in row["code"] for row in self.prices)
        )

    def test_colour_is_not_equipment_availability(self) -> None:
        self.assertFalse(
            any(
                row["attribute_code"] == "exterior_color"
                for row in self.availability
            )
        )
        self.assertEqual(len(self.availability), 419)

    def test_source_configuration_mapping_matches_manifest(self) -> None:
        actual = {
            row["configuration_code"]: row["source_code"]
            for row in self.source_configurations
            if row["configuration_code"] in EXPECTED
        }
        self.assertEqual(actual, EXPECTED)

    def test_package_codes_are_unique(self) -> None:
        codes = [row["code"].casefold() for row in self.rows]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertTrue(
            all(code.endswith("_exterior_color_20260626") for code in codes)
        )


if __name__ == "__main__":
    unittest.main()
