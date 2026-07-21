from __future__ import annotations

import csv
import unittest
from collections import Counter
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
MASTER = REPOSITORY / "data" / "master"
ATTRIBUTES_PATH = MASTER / "attributes.csv"
AVAILABILITY_PATH = MASTER / "configuration_attribute_availability.csv"

EXPECTED_NEW_ATTRIBUTE_CODES = {
    "adjustable_boot_floor",
    "boot_compartment_lighting",
    "cruise_control",
    "electronic_parking_brake",
    "electronic_stability_control",
    "extended_grip",
    "fog_lights",
    "front_centre_armrest",
    "gear_shift_indicator",
    "heated_steering_wheel",
    "high_filtering_glass",
    "hill_start_assist",
    "instrument_cluster_colour_7",
    "instrument_cluster_tft_3_5",
    "led_headlights",
    "manual_day_night_rearview_mirror",
    "media_control_system",
    "media_display_system",
    "onboard_computer",
    "one_touch_turn_signals",
    "speed_limiter",
    "steering_wheel_height_adjustment",
    "steering_wheel_reach_adjustment",
    "third_brake_light",
    "wireless_smartphone_replication",
}

EXPECTED_CONFIGURATION_COUNTS = {
    "sandero_iii_expression_ecog120_manual": 59,
    "sandero_iii_journey_ecog120_manual": 63,
    "sandero_stepway_iii_essential_ecog120_manual": 53,
    "sandero_stepway_iii_expression_ecog120_automatic": 59,
    "sandero_stepway_iii_expression_ecog120_manual": 60,
    "sandero_stepway_iii_extreme_ecog120_automatic": 62,
    "sandero_stepway_iii_extreme_ecog120_manual": 63,
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SanderoCoreEquipmentAvailabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.attributes = read_rows(ATTRIBUTES_PATH)
        cls.rows = [
            row for row in read_rows(AVAILABILITY_PATH)
            if row["configuration_code"] in EXPECTED_CONFIGURATION_COUNTS
            and row["observation_date"] == "2026-06-26"
        ]

    def test_imported_attribute_definitions_are_boolean_active(self) -> None:
        imported = {
            row["code"]: row
            for row in self.attributes
            if row["code"] in EXPECTED_NEW_ATTRIBUTE_CODES
        }

        self.assertEqual(set(imported), EXPECTED_NEW_ATTRIBUTE_CODES)
        self.assertEqual(
            {row["data_type"] for row in imported.values()},
            {"boolean"},
        )
        self.assertEqual(
            {row["status"] for row in imported.values()},
            {"active"},
        )
        self.assertTrue(all(not row["unit"] for row in imported.values()))

    def test_availability_dataset_has_expected_shape_and_count(self) -> None:
        self.assertEqual(len(self.rows), 419)
        self.assertEqual(
            list(self.rows[0]),
            [
                "id",
                "code",
                "configuration_code",
                "attribute_code",
                "availability_status",
                "observation_date",
                "source_code",
                "notes",
            ],
        )

    def test_records_cover_all_configurations_and_sources(self) -> None:
        self.assertEqual(
            set(Counter(row["configuration_code"] for row in self.rows)),
            set(EXPECTED_CONFIGURATION_COUNTS),
        )
        self.assertEqual(
            len({row["source_code"] for row in self.rows}),
            7,
        )
        self.assertEqual(
            {row["observation_date"] for row in self.rows},
            {"2026-06-26"},
        )

    def test_availability_records_are_unique_per_observation(self) -> None:
        keys = [
            (
                row["configuration_code"],
                row["attribute_code"],
                row["observation_date"],
                row["source_code"],
            )
            for row in self.rows
        ]

        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len({row["id"] for row in self.rows}), len(self.rows))
        self.assertEqual(
            len({row["code"].casefold() for row in self.rows}),
            len(self.rows),
        )

    def test_status_counts_match_source_import(self) -> None:
        self.assertEqual(
            Counter(row["availability_status"] for row in self.rows),
            Counter({"standard": 389, "not_available": 30}),
        )

    def test_configuration_counts_match_source_import(self) -> None:
        self.assertEqual(
            Counter(row["configuration_code"] for row in self.rows),
            Counter(EXPECTED_CONFIGURATION_COUNTS),
        )

    def test_distinguishing_features_match_sources(self) -> None:
        matrix = {
            (row["configuration_code"], row["attribute_code"]):
            row["availability_status"]
            for row in self.rows
        }

        journey = "sandero_iii_journey_ecog120_manual"
        essential = "sandero_stepway_iii_essential_ecog120_manual"
        expression_at = (
            "sandero_stepway_iii_expression_ecog120_automatic"
        )
        expression_mt = "sandero_stepway_iii_expression_ecog120_manual"
        extreme_at = "sandero_stepway_iii_extreme_ecog120_automatic"
        extreme_mt = "sandero_stepway_iii_extreme_ecog120_manual"

        self.assertEqual(matrix[(journey, "keyless_entry")], "standard")
        self.assertEqual(
            matrix[(essential, "keyless_entry")],
            "not_available",
        )
        self.assertEqual(
            matrix[(expression_at, "electronic_parking_brake")],
            "standard",
        )
        self.assertNotIn(
            (expression_mt, "electronic_parking_brake"),
            matrix,
        )
        self.assertEqual(
            matrix[(extreme_at, "extended_grip")],
            "standard",
        )
        self.assertEqual(
            matrix[(extreme_mt, "extended_grip")],
            "standard",
        )
        self.assertEqual(
            matrix[(essential, "media_control_system")],
            "standard",
        )
        self.assertNotIn((essential, "media_display_system"), matrix)

    def test_notes_preserve_source_page_and_wording(self) -> None:
        self.assertTrue(
            all(
                row["notes"].startswith("Source page 3:")
                or row["notes"].startswith("Source page 4:")
                for row in self.rows
            )
        )
        self.assertTrue(
            all(len(row["notes"].split(":", 1)[1].strip()) > 0
                for row in self.rows)
        )


if __name__ == "__main__":
    unittest.main()
