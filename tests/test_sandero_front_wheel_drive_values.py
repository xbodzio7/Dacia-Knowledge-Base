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
    with (MASTER / name).open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        return list(csv.DictReader(handle))


class SanderoFrontWheelDriveValueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.attributes = rows("attributes.csv")
        cls.all_values = rows("configuration_attribute_values.csv")
        cls.package = [
            row
            for row in cls.all_values
            if 233 <= int(row["id"]) <= 239
        ]
        cls.availability = rows(
            "configuration_attribute_availability.csv"
        )
        cls.prices = rows("configuration_prices.csv")
        cls.source_configurations = rows("source_configurations.csv")
        cls.drive_types = rows("enums/drive_types.csv")

    def test_existing_attribute_and_dictionary_value_are_active(
        self,
    ) -> None:
        attributes = {
            row["code"]: row
            for row in self.attributes
            if row["code"] == "drive_type"
        }
        self.assertEqual(set(attributes), {"drive_type"})
        attribute = attributes["drive_type"]
        self.assertEqual(attribute["id"], "39")
        self.assertEqual(attribute["category"], "Drivetrain")
        self.assertEqual(attribute["name"], "Drive type")
        self.assertEqual(attribute["data_type"], "enum")
        self.assertEqual(attribute["unit"], "")
        self.assertEqual(attribute["status"], "active")

        drive_types = {
            row["code"]: row
            for row in self.drive_types
        }
        self.assertEqual(
            set(drive_types),
            {"fwd", "rwd", "awd", "4x4"},
        )
        self.assertEqual(
            drive_types["fwd"]["name"],
            "Front-wheel drive",
        )
        self.assertEqual(
            drive_types["fwd"]["description"],
            "Front axle driven",
        )
        self.assertEqual(drive_types["fwd"]["status"], "active")

    def test_package_ids_shape_and_count(self) -> None:
        self.assertGreaterEqual(len(self.attributes), 349)
        self.assertGreaterEqual(len(self.all_values), 239)
        self.assertEqual(len(self.package), 7)
        self.assertEqual(
            {int(row["id"]) for row in self.package},
            set(range(233, 240)),
        )
        self.assertEqual(
            list(self.package[0]),
            [
                "id",
                "code",
                "configuration_code",
                "attribute_code",
                "fuel_type_code",
                "value",
                "observation_date",
                "source_code",
                "notes",
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

    def test_values_and_notes_preserve_exact_source_meaning(
        self,
    ) -> None:
        self.assertEqual(
            {row["attribute_code"] for row in self.package},
            {"drive_type"},
        )
        self.assertEqual(
            {row["value"] for row in self.package},
            {"fwd"},
        )
        self.assertEqual(
            {row["notes"] for row in self.package},
            {
                "Source page 5, section Układ napędowy: "
                "Rodzaj Napędu przedni"
            },
        )

    def test_controlled_drive_type_is_not_duplicated_as_strings(
        self,
    ) -> None:
        source_codes = set(EXPECTED.values())
        self.assertFalse(
            any(
                row["attribute_code"]
                in {"drive_layout", "drivetrain_type"}
                and row["source_code"] in source_codes
                and row["observation_date"] == "2026-06-26"
                for row in self.all_values
            ),
        )

    def test_value_is_not_availability_or_price(self) -> None:
        self.assertFalse(
            any(
                row["attribute_code"] == "drive_type"
                for row in self.availability
            ),
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
            any("drive_type" in row["code"] for row in self.prices),
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
                code.endswith("_drive_type_20260626")
                for code in codes
            ),
        )


if __name__ == "__main__":
    unittest.main()
