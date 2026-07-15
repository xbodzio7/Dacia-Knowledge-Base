from __future__ import annotations

import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"

EXPECTED = {
    "sandero_iii_expression_ecog120_manual": (
        "373", "src_pl_sandero_expression_ecog120_mt_20260626",
    ),
    "sandero_iii_journey_ecog120_manual": (
        "371", "src_pl_sandero_journey_ecog120_mt_20260626",
    ),
    "sandero_stepway_iii_essential_ecog120_manual": (
        "385", "src_pl_sandero_stepway_essential_ecog120_mt_20260626",
    ),
    "sandero_stepway_iii_expression_ecog120_automatic": (
        "380", "src_pl_sandero_stepway_expression_ecog120_at_20260626",
    ),
    "sandero_stepway_iii_expression_ecog120_manual": (
        "376", "src_pl_sandero_stepway_expression_ecog120_mt_20260626",
    ),
    "sandero_stepway_iii_extreme_ecog120_automatic": (
        "377", "src_pl_sandero_stepway_extreme_ecog120_at_20260626",
    ),
    "sandero_stepway_iii_extreme_ecog120_manual": (
        "375", "src_pl_sandero_stepway_extreme_ecog120_mt_20260626",
    ),
}


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(
        "r", encoding="utf-8-sig", newline="",
    ) as handle:
        return list(csv.DictReader(handle))


class SanderoMaximumPayloadValueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.attributes = rows("attributes.csv")
        cls.all_values = rows("configuration_attribute_values.csv")
        cls.package = [
            row for row in cls.all_values
            if 240 <= int(row["id"]) <= 246
        ]
        cls.availability = rows("configuration_attribute_availability.csv")
        cls.prices = rows("configuration_prices.csv")
        cls.source_configurations = rows("source_configurations.csv")

    def test_existing_attribute_is_active_integer_weight(self) -> None:
        matches = [
            row for row in self.attributes
            if row["code"] == "maximum_payload"
        ]
        self.assertEqual(matches, [{
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
        }])

    def test_package_ids_shape_and_count(self) -> None:
        self.assertGreaterEqual(len(self.attributes), 350)
        self.assertGreaterEqual(len(self.all_values), 246)
        self.assertEqual(len(self.package), 7)
        self.assertEqual(
            {int(row["id"]) for row in self.package},
            set(range(240, 247)),
        )
        self.assertEqual(
            list(self.package[0]),
            [
                "id", "code", "configuration_code", "attribute_code",
                "fuel_type_code", "value", "observation_date",
                "source_code", "notes",
            ],
        )

    def test_sources_date_and_fuel_context(self) -> None:
        self.assertEqual(
            {
                row["configuration_code"]: (
                    row["value"], row["source_code"],
                )
                for row in self.package
            },
            EXPECTED,
        )
        self.assertEqual(
            {row["observation_date"] for row in self.package},
            {"2026-06-26"},
        )
        self.assertEqual(
            {row["fuel_type_code"] for row in self.package}, {""},
        )
        self.assertEqual(
            {
                row["configuration_code"]: row["source_code"]
                for row in self.source_configurations
            },
            {code: source for code, (_, source) in EXPECTED.items()},
        )

    def test_values_and_notes_preserve_exact_source_wording(self) -> None:
        self.assertEqual(
            {row["attribute_code"] for row in self.package},
            {"maximum_payload"},
        )
        self.assertEqual(
            {
                row["configuration_code"]: row["value"]
                for row in self.package
            },
            {code: value for code, (value, _) in EXPECTED.items()},
        )
        for row in self.package:
            self.assertEqual(
                row["notes"],
                (
                    "Source page 5, section Dopuszczalna masa "
                    "całkowita: Maksymalna Ładowność (Kg) "
                    f"{row['value']}"
                ),
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
                code.endswith("_maximum_payload_20260626")
                for code in codes
            ),
        )

    def test_existing_mass_values_are_not_rewritten(self) -> None:
        counts = {
            code: sum(
                row["attribute_code"] == code
                for row in self.all_values
            )
            for code in {
                "kerb_weight", "gross_vehicle_weight",
                "gross_train_weight", "braked_trailer_weight",
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

    def test_value_is_not_availability_or_price(self) -> None:
        self.assertFalse(
            any(
                row["attribute_code"] == "maximum_payload"
                for row in self.availability
            ),
        )
        self.assertEqual(len(self.availability), 419)
        self.assertEqual(len(self.prices), 7)
        self.assertFalse(
            any("maximum_payload" in row["code"] for row in self.prices),
        )


if __name__ == "__main__":
    unittest.main()
