from __future__ import annotations

import csv
import json
import sqlite3
import tempfile
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from tools.build_sqlite import build_sqlite_db, discover_csv_files
from tools.validators.cargo_contexts import (
    validate_configuration_cargo_volume_contexts,
)
from tools.validators.references import REFERENCE_RULES
from tools.validators.statuses import ACTIVE_STATUSES, STATUS_RULES


ROOT = Path(__file__).resolve().parents[1]
_DATA_DICTIONARY_SPEC = spec_from_file_location(
    "dkb_data_dictionary",
    ROOT / "tools" / "reporting" / "data_dictionary.py",
)
if _DATA_DICTIONARY_SPEC is None or _DATA_DICTIONARY_SPEC.loader is None:
    raise RuntimeError("cannot load data dictionary module")
_DATA_DICTIONARY_MODULE = module_from_spec(_DATA_DICTIONARY_SPEC)
_DATA_DICTIONARY_SPEC.loader.exec_module(_DATA_DICTIONARY_MODULE)
generate_data_dictionary = _DATA_DICTIONARY_MODULE.generate_data_dictionary

MASTER = ROOT / "data" / "master"
RELATION = MASTER / "configuration_cargo_volume_contexts.csv"
ENUMS = MASTER / "enums"

EXPECTED_COLUMNS = [
    "id",
    "code",
    "configuration_attribute_value_code",
    "measurement_basis_code",
    "second_row_state_code",
    "third_row_state_code",
    "compartment_code",
    "spare_wheel_state_code",
    "tyre_repair_kit_state_code",
    "double_floor_state_code",
    "notes",
]

EXPECTED_DICTIONARIES = {
    "cargo_measurement_bases.csv": {"vda_iso_3832", "ordinary_litre"},
    "cargo_seat_states.csv": {
        "upright",
        "folded",
        "removed",
        "folded_or_removed",
    },
    "cargo_compartment_types.csv": {
        "main_luggage_compartment",
        "underfloor_compartment",
        "source_stated_total",
    },
    "context_presence_states.csv": {"present", "absent"},
}


class BrochureCargoContextSchemaFoundationTests(unittest.TestCase):
    def read_rows(self, path: Path) -> tuple[list[str], list[dict[str, str]]]:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            self.assertIsNotNone(reader.fieldnames)
            return list(reader.fieldnames or []), list(reader)

    def write_csv(
        self,
        root: Path,
        relative: str,
        columns: list[str],
        rows: list[list[str]],
    ) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(columns)
            writer.writerows(rows)

    def test_relation_matches_d023_and_remains_one_to_one(self) -> None:
        columns, rows = self.read_rows(RELATION)
        self.assertEqual(columns, EXPECTED_COLUMNS)
        value_codes = [
            row["configuration_attribute_value_code"] for row in rows
        ]
        self.assertEqual(len(value_codes), len(set(value_codes)))

    def test_controlled_dictionaries_have_exact_active_codes(self) -> None:
        for filename, expected_codes in EXPECTED_DICTIONARIES.items():
            columns, rows = self.read_rows(ENUMS / filename)
            self.assertEqual(columns, ["code", "name", "description", "status"])
            self.assertEqual({row["code"] for row in rows}, expected_codes)
            self.assertEqual({row["status"] for row in rows}, {"active"})

    def test_reference_rules_cover_every_context_dimension(self) -> None:
        rules = {
            rule.source_column: (
                rule.target_file,
                rule.target_column,
                rule.allow_empty,
            )
            for rule in REFERENCE_RULES
            if rule.source_file
            == "data/master/configuration_cargo_volume_contexts.csv"
        }
        self.assertEqual(
            rules,
            {
                "configuration_attribute_value_code": (
                    "data/master/configuration_attribute_values.csv",
                    "code",
                    False,
                ),
                "measurement_basis_code": (
                    "data/master/enums/cargo_measurement_bases.csv",
                    "code",
                    False,
                ),
                "second_row_state_code": (
                    "data/master/enums/cargo_seat_states.csv",
                    "code",
                    True,
                ),
                "third_row_state_code": (
                    "data/master/enums/cargo_seat_states.csv",
                    "code",
                    True,
                ),
                "compartment_code": (
                    "data/master/enums/cargo_compartment_types.csv",
                    "code",
                    False,
                ),
                "spare_wheel_state_code": (
                    "data/master/enums/context_presence_states.csv",
                    "code",
                    True,
                ),
                "tyre_repair_kit_state_code": (
                    "data/master/enums/context_presence_states.csv",
                    "code",
                    True,
                ),
                "double_floor_state_code": (
                    "data/master/enums/context_presence_states.csv",
                    "code",
                    True,
                ),
            },
        )

    def test_status_rules_cover_all_context_dictionaries(self) -> None:
        expected_paths = {
            f"data/master/enums/{filename}"
            for filename in EXPECTED_DICTIONARIES
        }
        matching = {
            rule.path: rule
            for rule in STATUS_RULES
            if rule.path in expected_paths
        }
        self.assertEqual(set(matching), expected_paths)
        self.assertTrue(
            all(rule.allowed_statuses == ACTIVE_STATUSES for rule in matching.values())
        )
        self.assertTrue(all(rule.end_column is None for rule in matching.values()))

    def test_semantic_validator_accepts_empty_foundation_relation(self) -> None:
        checked, errors = validate_configuration_cargo_volume_contexts(ROOT)
        self.assertEqual(checked, 0)
        self.assertEqual(errors, [])

    def test_semantic_validator_rejects_duplicate_value_context(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_csv(
                root,
                "data/master/configuration_attribute_values.csv",
                ["code", "attribute_code"],
                [["cargo_value", "boot_capacity"]],
            )
            self.write_csv(
                root,
                "data/master/configuration_cargo_volume_contexts.csv",
                ["configuration_attribute_value_code"],
                [["cargo_value"], ["cargo_value"]],
            )
            checked, errors = validate_configuration_cargo_volume_contexts(root)
        self.assertEqual(checked, 2)
        self.assertEqual(len(errors), 1)
        self.assertIn("duplicate cargo context", errors[0])

    def test_semantic_validator_rejects_non_boot_capacity_value(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_csv(
                root,
                "data/master/configuration_attribute_values.csv",
                ["code", "attribute_code"],
                [["length_value", "vehicle_length"]],
            )
            self.write_csv(
                root,
                "data/master/configuration_cargo_volume_contexts.csv",
                ["configuration_attribute_value_code"],
                [["length_value"]],
            )
            checked, errors = validate_configuration_cargo_volume_contexts(root)
        self.assertEqual(checked, 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("expected 'boot_capacity'", errors[0])

    def test_sqlite_includes_relation_and_context_dictionaries(self) -> None:
        names = {path.stem for path in discover_csv_files(MASTER)}
        expected = {
            "configuration_cargo_volume_contexts",
            "cargo_measurement_bases",
            "cargo_seat_states",
            "cargo_compartment_types",
            "context_presence_states",
        }
        self.assertTrue(expected <= names)
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "dkb.sqlite"
            build_sqlite_db(ROOT, database)
            with sqlite3.connect(database) as connection:
                tables = {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type = 'table'"
                    )
                }
                relation_rows = connection.execute(
                    "SELECT COUNT(*) FROM configuration_cargo_volume_contexts"
                ).fetchone()
        self.assertTrue(expected <= tables)
        self.assertEqual(relation_rows, (0,))

    def test_data_dictionary_discovers_context_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "data_dictionary.md"
            generate_data_dictionary(ROOT, output)
            text = output.read_text(encoding="utf-8")
        self.assertIn(
            "## data/master/configuration_cargo_volume_contexts.csv",
            text,
        )
        for filename in EXPECTED_DICTIONARIES:
            self.assertIn(f"## data/master/enums/{filename}", text)
        self.assertIn("| measurement_basis_code |", text)
        self.assertIn("| configuration_attribute_value_code |", text)

    def test_state_and_master_baseline_expose_schema_only_package(self) -> None:
        state = json.loads(
            (ROOT / "project" / "state.json").read_text(encoding="utf-8")
        )
        self.assertTrue(state["phase"])
        self.assertGreaterEqual(state["baseline"]["tests"], 776)
        self.assertGreaterEqual(state["baseline"]["csv_files"], 46)
        self.assertGreaterEqual(state["baseline"]["rows"], 8156)
        self.assertEqual(state["baseline"]["configuration_values"], 1831)
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertTrue(state["next_package"]["name"])


if __name__ == "__main__":
    unittest.main()
