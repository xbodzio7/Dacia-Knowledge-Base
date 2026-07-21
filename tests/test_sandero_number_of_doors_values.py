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


class SanderoNumberOfDoorsValueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.attributes = rows("attributes.csv")
        cls.all_values = rows("configuration_attribute_values.csv")
        cls.package = [
            row for row in cls.all_values
            if 212 <= int(row["id"]) <= 218
        ]
        cls.availability = rows("configuration_attribute_availability.csv")
        cls.prices = rows("configuration_prices.csv")
        cls.source_configurations = rows("source_configurations.csv")

    def test_existing_attribute_is_active_unitless_integer(self) -> None:
        matches = [
            row for row in self.attributes
            if row["code"] == "number_of_doors"
        ]
        self.assertEqual(len(matches), 1)
        attribute = matches[0]
        self.assertEqual(attribute["id"], "194")
        self.assertEqual(attribute["category"], "Doors")
        self.assertEqual(attribute["name"], "Number of doors")
        self.assertEqual(attribute["data_type"], "integer")
        self.assertEqual(attribute["unit"], "")
        self.assertEqual(attribute["status"], "active")

    def test_package_ids_shape_and_count(self) -> None:
        self.assertGreaterEqual(len(self.attributes), 348)
        self.assertGreaterEqual(len(self.all_values), 218)
        self.assertEqual(len(self.package), 7)
        self.assertEqual(
            {int(row["id"]) for row in self.package},
            set(range(212, 219)),
        )
        self.assertEqual(
            list(self.package[0]),
            [
                "id", "code", "configuration_code", "attribute_code",
                "fuel_type_code", "value", "observation_date",
                "source_code", "notes",
            ],
        )

    def test_manifest_sources_date_and_fuel_context(self) -> None:
        self.assertEqual(
            {
                row["configuration_code"]: row["source_code"]
                for row in self.package
            },
            EXPECTED,
        )
        self.assertEqual(
            {row["observation_date"] for row in self.package},
            {"2026-06-26"},
        )
        self.assertEqual(
            {row["fuel_type_code"] for row in self.package},
            {""},
        )
        registered_pairs = {
            (row["configuration_code"], row["source_code"])
            for row in self.source_configurations
        }
        self.assertTrue(set(EXPECTED.items()) <= registered_pairs)

    def test_values_and_notes_preserve_source_wording(self) -> None:
        self.assertEqual(
            {row["attribute_code"] for row in self.package},
            {"number_of_doors"},
        )
        self.assertEqual({row["value"] for row in self.package}, {"5"})
        self.assertEqual(
            {row["notes"] for row in self.package},
            {"Source page 5, section Typ nadwozia: Liczba Drzwi 5"},
        )

    def test_total_count_does_not_populate_side_door_count(self) -> None:
        source_codes = set(EXPECTED.values())
        self.assertFalse(
            any(
                row["attribute_code"] == "number_of_side_doors"
                and row["source_code"] in source_codes
                and row["observation_date"] == "2026-06-26"
                for row in self.all_values
            )
        )

    def test_value_is_not_availability_or_price(self) -> None:
        self.assertFalse(
            any(
                row["attribute_code"] == "number_of_doors"
                for row in self.availability
            )
        )
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
            any("number_of_doors" in row["code"] for row in self.prices)
        )

    def test_each_configuration_has_exactly_one_value(self) -> None:
        for configuration_code in EXPECTED:
            self.assertEqual(
                sum(
                    row["configuration_code"] == configuration_code
                    for row in self.package
                ),
                1,
            )

    def test_codes_are_unique_and_dated(self) -> None:
        codes = [row["code"].casefold() for row in self.package]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertTrue(
            all(
                code.endswith("_number_of_doors_20260626")
                for code in codes
            )
        )


if __name__ == "__main__":
    unittest.main()
