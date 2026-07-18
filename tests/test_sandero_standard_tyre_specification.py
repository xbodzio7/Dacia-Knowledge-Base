from __future__ import annotations

import csv
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
MASTER = REPOSITORY / "data" / "master"
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


class SanderoStandardTyreSpecificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.attributes = read_rows(ATTRIBUTES_PATH)
        cls.all_values = read_rows(VALUES_PATH)
        cls.rows = [
            row
            for row in cls.all_values
            if 205 <= int(row["id"]) <= 211
        ]
        cls.availability = read_rows(AVAILABILITY_PATH)
        cls.prices = read_rows(PRICES_PATH)
        cls.source_configurations = read_rows(SOURCE_CONFIGURATIONS_PATH)

    def test_attribute_is_defined_as_active_string(self) -> None:
        attributes = {
            row["code"]: row
            for row in self.attributes
            if row["code"] == "standard_tyre_specification"
        }
        self.assertEqual(set(attributes), {"standard_tyre_specification"})
        attribute = attributes["standard_tyre_specification"]
        self.assertEqual(attribute["id"], "355")
        self.assertEqual(attribute["category"], "Wheels")
        self.assertEqual(attribute["name"], "Standard tyre specification")
        self.assertEqual(attribute["data_type"], "string")
        self.assertEqual(attribute["unit"], "")
        self.assertEqual(attribute["status"], "active")

    def test_package_ids_shape_and_count(self) -> None:
        self.assertGreaterEqual(len(self.attributes), 348)
        self.assertGreaterEqual(len(self.all_values), 211)
        self.assertEqual(len(self.rows), 7)
        self.assertEqual(
            {int(row["id"]) for row in self.rows},
            set(range(205, 212)),
        )
        self.assertEqual(
            list(self.rows[0]),
            [
                "id", "code", "configuration_code", "attribute_code",
                "fuel_type_code", "value", "observation_date",
                "source_code", "notes",
            ],
        )

    def test_manifest_matches_configurations_sources_and_date(self) -> None:
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
        source_mapping = {
            row["configuration_code"]: row["source_code"]
            for row in self.source_configurations
            if row["configuration_code"] in EXPECTED
        }
        self.assertEqual(source_mapping, EXPECTED)

    def test_values_and_notes_preserve_source_wording(self) -> None:
        self.assertEqual(
            {row["attribute_code"] for row in self.rows},
            {"standard_tyre_specification"},
        )
        self.assertEqual(
            {row["value"] for row in self.rows},
            {"205/60 R16 92H"},
        )
        self.assertEqual(
            {row["notes"] for row in self.rows},
            {
                "Source page 5, section Koła i opony: "
                "Opony Standardowe 205/60 R16 92H"
            },
        )

    def test_axle_neutral_source_does_not_populate_axle_attributes(self) -> None:
        forbidden = {"front_tyre_size", "rear_tyre_size"}
        source_codes = set(EXPECTED.values())
        self.assertFalse(
            any(
                row["attribute_code"] in forbidden
                and row["source_code"] in source_codes
                and row["observation_date"] == "2026-06-26"
                for row in self.all_values
            ),
        )

    def test_source_rating_is_not_modeled_as_maximum(self) -> None:
        forbidden = {"max_tyre_load_index", "max_tyre_speed_rating"}
        source_codes = set(EXPECTED.values())
        self.assertFalse(
            any(
                row["attribute_code"] in forbidden
                and row["source_code"] in source_codes
                and row["observation_date"] == "2026-06-26"
                for row in self.all_values
            ),
        )

    def test_complete_specification_is_separate_from_wheel_size(self) -> None:
        source_codes = set(EXPECTED.values())
        wheel_rows = [
            row
            for row in self.all_values
            if row["attribute_code"] == "wheel_size"
            and row["source_code"] in source_codes
            and row["observation_date"] == "2026-06-26"
        ]
        self.assertEqual(len(wheel_rows), 7)
        self.assertEqual({row["value"] for row in wheel_rows}, {'16"'})
        self.assertTrue(
            all(
                row["notes"].startswith("Source page 2, section Felgi:")
                or row["notes"].startswith(
                    "Source pages 2-3, sections Felgi/WYGLĄD:"
                )
                for row in wheel_rows
            ),
        )
        self.assertTrue(
            all(row["attribute_code"] != "wheel_size" for row in self.rows),
        )

    def test_value_is_not_equipment_availability_or_price(self) -> None:
        self.assertFalse(
            any(
                row["attribute_code"] == "standard_tyre_specification"
                for row in self.availability
            ),
        )
        self.assertEqual(len(self.availability), 419)
        self.assertEqual(len(self.prices), 7)
        self.assertFalse(
            any(
                "standard_tyre_specification" in row["code"]
                for row in self.prices
            ),
        )

    def test_package_codes_are_unique(self) -> None:
        codes = [row["code"].casefold() for row in self.rows]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertTrue(
            all(
                code.endswith("_standard_tyre_specification_20260626")
                for code in codes
            ),
        )


if __name__ == "__main__":
    unittest.main()
