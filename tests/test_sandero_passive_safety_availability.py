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
    "rear_seat_belt_pretensioners",
    "seat_belt_reminder",
    "driver_front_airbag",
    "passenger_front_airbag",
    "emergency_stop_signal",
    "rear_three_point_seat_belts",
    "emergency_call_ecall",
    "central_locking",
    "front_side_airbags",
    "curtain_airbags",
    "anti_lock_braking_system",
    "tyre_repair_kit",
    "front_seat_belt_pretensioners",
    "safe_distance_warning",
    "driver_seat_belt_height_adjustment",
    "automatic_door_locking",
    "alcohol_interlock_preparation",
}

EXPECTED_SOURCE_PHRASES = {
    "rear_seat_belt_pretensioners": 'napinacz tylnego pasa bezpieczeństwa',
    "seat_belt_reminder": 'ostrzeżenie o niezapięciu pasów',
    "driver_front_airbag": 'poduszka powietrzna czołowa kierowcy',
    "passenger_front_airbag": 'poduszka powietrzna czołowa pasażera',
    "emergency_stop_signal": 'automatyczny zapłon ostrzegawczy przy mocnym hamowaniu',
    "rear_three_point_seat_belts": '3 punktowe tylne pasy bezpieczeństwa z napinaczem pirotechnicznym na bocznych fotelach',
    "emergency_call_ecall": 'funkcja połączenia alarmowego e-Call',
    "central_locking": 'centralny zamek',
    "front_side_airbags": 'poduszki boczne z przodu + poduszki kurtynowe',
    "curtain_airbags": 'poduszki boczne z przodu + poduszki kurtynowe',
    "anti_lock_braking_system": 'ABS',
    "tyre_repair_kit": 'zestaw do naprawy uszkodzenia opony',
    "front_seat_belt_pretensioners": 'napinacze pirotechniczne pasów bezpieczeństwa przednich foteli',
    "safe_distance_warning": 'ostrzeżenie o bezpiecznej odległości',
    "driver_seat_belt_height_adjustment": 'pas bezpieczeństwa kierowcy bez regulacji wysokości',
    "automatic_door_locking": 'automatyczna blokada drzwi po ruszeniu',
    "alcohol_interlock_preparation": 'przystosowanie do montażu blokady alkoholowej',
}

EXPECTED_CONFIGURATIONS = {
    "sandero_iii_expression_ecog120_manual",
    "sandero_iii_journey_ecog120_manual",
    "sandero_stepway_iii_essential_ecog120_manual",
    "sandero_stepway_iii_expression_ecog120_automatic",
    "sandero_stepway_iii_expression_ecog120_manual",
    "sandero_stepway_iii_extreme_ecog120_automatic",
    "sandero_stepway_iii_extreme_ecog120_manual",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SanderoPassiveSafetyAvailabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.attributes = read_rows(ATTRIBUTES_PATH)
        cls.all_rows = read_rows(AVAILABILITY_PATH)
        cls.rows = [
            row for row in cls.all_rows if 301 <= int(row["id"]) <= 419
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

    def test_package_has_expected_ids_shape_and_count(self) -> None:
        self.assertEqual(
            len([
                row for row in self.all_rows
                if not row["configuration_code"].startswith(("duster_iii_", "jogger_"))
                and row["observation_date"] == "2026-06-26"
            ]),
            419,
        )
        self.assertEqual(len(self.rows), 119)
        self.assertEqual(
            {int(row["id"]) for row in self.rows},
            set(range(301, 420)),
        )
        self.assertEqual(
            list(self.rows[0]),
            [
                "id", "code", "configuration_code", "attribute_code",
                "availability_status", "observation_date",
                "source_code", "notes",
            ],
        )

    def test_package_status_counts_match_sources(self) -> None:
        self.assertEqual(
            Counter(row["availability_status"] for row in self.rows),
            Counter({"standard": 112, "not_available": 7}),
        )

    def test_package_covers_all_configurations_and_sources(self) -> None:
        self.assertEqual(
            Counter(row["configuration_code"] for row in self.rows),
            Counter({code: 17 for code in EXPECTED_CONFIGURATIONS}),
        )
        self.assertEqual(len({row["source_code"] for row in self.rows}), 7)
        self.assertEqual(
            {row["observation_date"] for row in self.rows},
            {"2026-06-26"},
        )

    def test_every_candidate_occurs_once_per_configuration(self) -> None:
        pairs = [
            (row["configuration_code"], row["attribute_code"])
            for row in self.rows
        ]
        self.assertEqual(len(pairs), len(set(pairs)))
        self.assertEqual(
            Counter(row["attribute_code"] for row in self.rows),
            Counter({code: 7 for code in EXPECTED_NEW_ATTRIBUTE_CODES}),
        )

    def test_explicit_negative_is_limited_to_height_adjustment(self) -> None:
        negatives = [
            row for row in self.rows
            if row["availability_status"] == "not_available"
        ]
        self.assertEqual(len(negatives), 7)
        self.assertEqual(
            {row["attribute_code"] for row in negatives},
            {"driver_seat_belt_height_adjustment"},
        )
        self.assertEqual(
            {row["configuration_code"] for row in negatives},
            EXPECTED_CONFIGURATIONS,
        )

    def test_notes_preserve_page_and_exact_source_wording(self) -> None:
        for row in self.rows:
            prefix, wording = row["notes"].split(":", 1)
            self.assertIn(prefix, {"Source page 3", "Source page 4"})
            self.assertEqual(
                wording.strip(),
                EXPECTED_SOURCE_PHRASES[row["attribute_code"]],
            )

    def test_trim_and_upholstery_remain_outside_this_package(self) -> None:
        forbidden = ("wheel_design", "wheel_material", "upholstery")
        self.assertFalse(
            any(
                fragment in row["attribute_code"]
                for row in self.rows
                for fragment in forbidden
            )
        )


if __name__ == "__main__":
    unittest.main()
