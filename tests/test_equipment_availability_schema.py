from __future__ import annotations

import csv
import unittest
from pathlib import Path

from tools.build_sqlite import discover_csv_files
from tools.validators.references import REFERENCE_RULES
from tools.validators.statuses import ACTIVE_STATUSES, STATUS_RULES


REPOSITORY = Path(__file__).resolve().parents[1]
MASTER = REPOSITORY / "data" / "master"
RELATION_PATH = MASTER / "configuration_attribute_availability.csv"
STATUS_PATH = MASTER / "enums" / "equipment_availability_statuses.csv"

EXPECTED_RELATION_COLUMNS = [
    "id",
    "code",
    "configuration_code",
    "attribute_code",
    "availability_status",
    "observation_date",
    "source_code",
    "notes",
]

EXPECTED_STATUSES = {
    "standard",
    "optional",
    "not_available",
    "unknown",
}


class EquipmentAvailabilitySchemaTests(unittest.TestCase):
    def read_rows(self, path: Path) -> tuple[list[str], list[dict[str, str]]]:
        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            reader = csv.DictReader(handle)
            self.assertIsNotNone(reader.fieldnames)
            return list(reader.fieldnames or []), list(reader)

    def test_relation_matches_d015_and_is_header_only(self) -> None:
        columns, rows = self.read_rows(RELATION_PATH)

        self.assertEqual(columns, EXPECTED_RELATION_COLUMNS)
        self.assertEqual(rows, [])

    def test_status_dictionary_contains_controlled_values(self) -> None:
        columns, rows = self.read_rows(STATUS_PATH)

        self.assertEqual(
            columns,
            ["code", "name", "description", "status"],
        )
        self.assertEqual(
            {row["code"] for row in rows},
            EXPECTED_STATUSES,
        )
        self.assertEqual(
            {row["status"] for row in rows},
            {"active"},
        )

    def test_declares_all_equipment_availability_references(self) -> None:
        rules = {
            rule.source_column: (
                rule.target_file,
                rule.target_column,
                rule.allow_empty,
            )
            for rule in REFERENCE_RULES
            if rule.source_file
            == "data/master/configuration_attribute_availability.csv"
        }

        self.assertEqual(
            rules,
            {
                "configuration_code": (
                    "data/master/configurations.csv",
                    "code",
                    False,
                ),
                "attribute_code": (
                    "data/master/attributes.csv",
                    "code",
                    False,
                ),
                "availability_status": (
                    "data/master/enums/"
                    "equipment_availability_statuses.csv",
                    "code",
                    False,
                ),
                "source_code": (
                    "data/master/sources.csv",
                    "code",
                    False,
                ),
            },
        )

    def test_declares_status_validation_for_dictionary(self) -> None:
        matching = [
            rule
            for rule in STATUS_RULES
            if rule.path
            == "data/master/enums/equipment_availability_statuses.csv"
        ]

        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0].allowed_statuses, ACTIVE_STATUSES)
        self.assertIsNone(matching[0].end_column)

    def test_sqlite_discovery_includes_new_schema_tables(self) -> None:
        table_names = {
            path.stem
            for path in discover_csv_files(MASTER)
        }

        self.assertIn(
            "configuration_attribute_availability",
            table_names,
        )
        self.assertIn(
            "equipment_availability_statuses",
            table_names,
        )


if __name__ == "__main__":
    unittest.main()
