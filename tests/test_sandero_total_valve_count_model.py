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


class SanderoTotalValveCountModelTests(unittest.TestCase):
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
        cls.decisions = (
            ROOT / "project" / "DECISIONS.md"
        ).read_text(encoding="utf-8")

    def test_existing_engine_category_is_reused_without_a_new_unit(self) -> None:
        engine = [
            row
            for row in self.categories
            if row["code"] == "engine"
        ]
        self.assertEqual(
            engine,
            [{
                "code": "engine",
                "name": "Engine",
                "description": "Internal combustion engine specifications",
            }],
        )
        self.assertEqual(len(self.categories), 30)
        self.assertEqual(len(self.units), 26)

    def test_total_valve_count_is_an_active_integer_engine_attribute(self) -> None:
        matches = [
            row
            for row in self.attributes
            if row["code"] == "total_valve_count"
        ]
        self.assertEqual(
            matches,
            [{
                "id": "358",
                "code": "total_valve_count",
                "category": "Engine",
                "name": "Total valve count",
                "data_type": "integer",
                "unit": "",
                "description": (
                    "Total number of engine valves stated explicitly by the "
                    "source; distinct from valves per cylinder"
                ),
                "status": "active",
            }],
        )
        self.assertEqual(len(self.attributes), 354)

    def test_total_count_remains_distinct_from_related_engine_counts(self) -> None:
        expected = {
            "cylinder_count": ("Cylinder count", "integer", ""),
            "valves_per_cylinder": (
                "Valves per cylinder",
                "integer",
                "",
            ),
            "total_valve_count": (
                "Total valve count",
                "integer",
                "",
            ),
        }
        actual = {
            row["code"]: (
                row["name"],
                row["data_type"],
                row["unit"],
            )
            for row in self.attributes
            if row["code"] in expected
        }
        self.assertEqual(actual, expected)
        self.assertNotIn("valve_count", actual)
        self.assertNotIn("number_of_valves", actual)

    def test_import_uses_existing_total_valve_count_attribute(self) -> None:
        total_valve_values = [
            row
            for row in self.values
            if row["attribute_code"] == "total_valve_count"
            and row["configuration_code"] in EXPECTED_MAPPING
        ]
        self.assertEqual(len(total_valve_values), 7)
        self.assertEqual(
            {
                row["configuration_code"]
                for row in total_valve_values
            },
            set(EXPECTED_MAPPING),
        )
        self.assertEqual(
            {row["value"] for row in total_valve_values},
            {"12"},
        )
        self.assertEqual(
            {row["fuel_type_code"] for row in total_valve_values},
            {""},
        )

    def test_existing_engine_observations_are_not_rewritten(self) -> None:
        counts = {
            code: sum(
                row["attribute_code"] == code
                and row["configuration_code"] in EXPECTED_MAPPING
                for row in self.values
            )
            for code in {
                "cylinder_count",
                "valves_per_cylinder",
                "engine_power",
                "engine_torque",
            }
        }
        self.assertEqual(
            counts,
            {
                "cylinder_count": 7,
                "valves_per_cylinder": 0,
                "engine_power": 14,
                "engine_torque": 14,
            },
        )
        self.assertIn(
            "## D-022 — Source-stated total engine valve count",
            self.decisions,
        )
        self.assertIn("`Liczba Zaworów 12`", self.decisions)
        self.assertIn(
            "must not be calculated by dividing",
            self.decisions,
        )

    def test_availability_prices_and_source_mapping_are_unchanged(self) -> None:
        self.assertEqual(
            len([
                row for row in self.availability
                if not row["configuration_code"].startswith("duster_iii_")
            ]),
            419,
        )
        self.assertEqual(
            len([
                row for row in self.prices
                if row["configuration_code"] in EXPECTED_MAPPING
            ]),
            7,
        )
        expected_sources = set(EXPECTED_MAPPING.values())
        self.assertEqual(
            {row["code"] for row in self.sources if row["code"] in expected_sources},
            expected_sources,
        )
        self.assertEqual(
            {
                row["configuration_code"]: row["source_code"]
                for row in self.source_configurations
                if row["configuration_code"] in EXPECTED_MAPPING
            },
            EXPECTED_MAPPING,
        )


if __name__ == "__main__":
    unittest.main()
