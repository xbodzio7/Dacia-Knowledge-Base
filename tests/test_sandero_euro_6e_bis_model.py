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
SOURCES_PATH = MASTER / "sources.csv"
SOURCE_CONFIGURATIONS_PATH = MASTER / "source_configurations.csv"
EMISSION_STANDARDS_PATH = MASTER / "enums" / "emission_standards.csv"

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


class SanderoEuro6eBisModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.attributes = read_rows(ATTRIBUTES_PATH)
        cls.values = read_rows(VALUES_PATH)
        cls.availability = read_rows(AVAILABILITY_PATH)
        cls.prices = read_rows(PRICES_PATH)
        cls.sources = read_rows(SOURCES_PATH)
        cls.source_configurations = read_rows(SOURCE_CONFIGURATIONS_PATH)
        cls.standards = read_rows(EMISSION_STANDARDS_PATH)

    def test_existing_attribute_is_active_enum(self) -> None:
        attributes = {
            row["code"]: row
            for row in self.attributes
            if row["code"] == "emission_standard"
        }
        self.assertEqual(set(attributes), {"emission_standard"})
        attribute = attributes["emission_standard"]
        self.assertEqual(attribute["id"], "28")
        self.assertEqual(attribute["category"], "Engine")
        self.assertEqual(attribute["name"], "Emission standard")
        self.assertEqual(attribute["data_type"], "enum")
        self.assertEqual(attribute["unit"], "")
        self.assertEqual(attribute["status"], "active")

    def test_dictionary_contains_exact_active_bis_variant(self) -> None:
        standards = {row["code"]: row for row in self.standards}
        self.assertEqual(set(standards), {"euro_6", "euro_6e", "euro_6e_bis", "ev"})
        bis = standards["euro_6e_bis"]
        self.assertEqual(bis["name"], "Euro 6e BIS")
        self.assertEqual(bis["description"], "Euro 6e BIS emissions standard")
        self.assertEqual(bis["status"], "active")

    def test_bis_variant_remains_distinct_from_euro_6e(self) -> None:
        standards = {row["code"]: row for row in self.standards}
        self.assertNotEqual("euro_6e_bis", "euro_6e")
        self.assertNotEqual(
            standards["euro_6e_bis"]["name"],
            standards["euro_6e"]["name"],
        )
        self.assertEqual(standards["euro_6e"]["name"], "Euro 6e")

    def test_model_package_does_not_import_configuration_values(self) -> None:
        source_codes = set(EXPECTED.values())
        self.assertFalse(
            any(
                row["attribute_code"] == "emission_standard"
                and row["source_code"] in source_codes
                and row["observation_date"] == "2026-06-26"
                for row in self.values
            ),
        )
        self.assertEqual(len(self.values), 218)

    def test_model_package_does_not_change_other_data_tables(self) -> None:
        self.assertEqual(len(self.availability), 419)
        self.assertEqual(len(self.prices), 7)
        self.assertFalse(
            any("emission_standard" in row["code"] for row in self.prices),
        )

    def test_source_registry_and_mapping_are_unchanged(self) -> None:
        self.assertEqual(len(self.sources), 7)
        mapping = {
            row["configuration_code"]: row["source_code"]
            for row in self.source_configurations
        }
        self.assertEqual(mapping, EXPECTED)

    def test_dictionary_codes_are_unique_and_active(self) -> None:
        codes = [row["code"].casefold() for row in self.standards]
        self.assertEqual(len(codes), 4)
        self.assertEqual(len(codes), len(set(codes)))
        self.assertEqual({row["status"] for row in self.standards}, {"active"})


if __name__ == "__main__":
    unittest.main()
