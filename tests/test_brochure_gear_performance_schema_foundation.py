from __future__ import annotations

import csv
import importlib.util
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import import_configuration_values as importer  # noqa: E402
from reporting.cargo_context import technical_context  # noqa: E402
from validators.gear_contexts import validate_gear_contexts  # noqa: E402

VALUE_PATH = ROOT / "data" / "master" / "configuration_attribute_values.csv"
EXPECTED_HEADER = [
    "id",
    "code",
    "configuration_code",
    "attribute_code",
    "fuel_type_code",
    "gear_number",
    "value",
    "observation_date",
    "source_code",
    "notes",
]


def read_values(path: Path = VALUE_PATH) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def load_import_fixture():
    path = ROOT / "tests" / "test_import_configuration_values.py"
    spec = importlib.util.spec_from_file_location("gear_import_fixture", path)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load import fixture")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fixture = module.ImportConfigurationValuesTests(methodName="runTest")
    fixture.setUp()
    return fixture


class BrochureGearPerformanceSchemaFoundationTests(unittest.TestCase):
    def test_master_schema_preserves_blank_gear_for_preexisting_rows(self) -> None:
        header, rows = read_values()
        self.assertEqual(header, EXPECTED_HEADER)
        self.assertGreaterEqual(len(rows), 2118)
        self.assertEqual({row["gear_number"] for row in rows[:2118]}, {""})

    def test_repository_gear_validation_passes(self) -> None:
        _, rows = read_values()
        checked, errors = validate_gear_contexts(ROOT)
        self.assertEqual(checked, len(rows))
        self.assertEqual(errors, [])

    def test_validator_rejects_noncanonical_gear_numbers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "data" / "master" / "configuration_attribute_values.csv"
            path.parent.mkdir(parents=True)
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=EXPECTED_HEADER, lineterminator="\n")
                writer.writeheader()
                for index, gear in enumerate(("0", "04", "-1", "4.0", "x"), start=1):
                    writer.writerow({
                        "id": str(index), "code": f"v{index}", "configuration_code": "cfg",
                        "attribute_code": "elasticity_80_120", "fuel_type_code": "",
                        "gear_number": gear, "value": "10.5", "observation_date": "2026-01-01",
                        "source_code": "src", "notes": "test",
                    })
            checked, errors = validate_gear_contexts(root)
        self.assertEqual(checked, 5)
        self.assertEqual(len(errors), 5)
        self.assertTrue(all("canonical positive integer" in error for error in errors))

    def test_validator_rejects_ineligible_attribute_and_duplicate_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "data" / "master" / "configuration_attribute_values.csv"
            path.parent.mkdir(parents=True)
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=EXPECTED_HEADER, lineterminator="\n")
                writer.writeheader()
                writer.writerows([
                    {"id":"1","code":"a","configuration_code":"cfg","attribute_code":"maximum_speed","fuel_type_code":"","gear_number":"4","value":"180","observation_date":"2026-01-01","source_code":"src","notes":"test"},
                    {"id":"2","code":"b","configuration_code":"cfg","attribute_code":"elasticity_80_120","fuel_type_code":"lpg","gear_number":"4","value":"10.1","observation_date":"2026-01-01","source_code":"src","notes":"test"},
                    {"id":"3","code":"c","configuration_code":"cfg","attribute_code":"elasticity_80_120","fuel_type_code":"lpg","gear_number":"4","value":"10.2","observation_date":"2026-01-01","source_code":"src","notes":"test"},
                ])
            checked, errors = validate_gear_contexts(root)
        self.assertEqual(checked, 3)
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("not allowed" in error for error in errors))
        self.assertTrue(any("duplicate selected-gear observation" in error for error in errors))

    def test_declarative_importer_remains_backward_compatible(self) -> None:
        fixture = load_import_fixture()
        self.addCleanup(fixture.tearDown)
        spec = importer.load_spec(fixture.spec_path)
        rows = importer.build_expected_rows(fixture.repository, spec)
        self.assertEqual({row["gear_number"] for row in rows}, {""})
        self.assertTrue(all("gear" not in row["code"] for row in rows))

    def test_importer_accepts_distinct_selected_gears_for_same_context(self) -> None:
        fixture = load_import_fixture()
        self.addCleanup(fixture.tearDown)
        attributes = fixture.master / "attributes.csv"
        with attributes.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["id", "code", "category", "name", "data_type", "unit", "description", "status"],
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerow({"id":"1","code":"elasticity_80_120","category":"Performance","name":"Elasticity 80-120","data_type":"decimal","unit":"s","description":"Selected-gear elasticity","status":"active"})
        payload = fixture._payload()
        payload["attribute_code"] = "elasticity_80_120"
        payload["attribute_contract"] = {"data_type":"decimal","unit":"s","status":"active"}
        rows = payload["rows"]
        assert isinstance(rows, list)
        rows[0]["value"] = "10.1"
        rows[0]["gear_number"] = "4"
        rows[1] = {
            "configuration_code": "configuration_a",
            "source_code": "source_a",
            "value": "12.3",
            "source_text": "80-120 km/h fifth gear 12.3 s",
            "gear_number": "5",
        }
        fixture._write_spec(payload)
        spec = importer.load_spec(fixture.spec_path)
        expected = importer.build_expected_rows(fixture.repository, spec)
        self.assertEqual({row["gear_number"] for row in expected}, {"4", "5"})
        self.assertEqual(
            {row["code"] for row in expected},
            {
                "configuration_a_elasticity_80_120_gear4_20260626",
                "configuration_a_elasticity_80_120_gear5_20260626",
            },
        )

    def test_technical_context_renders_selected_gear_without_inference(self) -> None:
        self.assertEqual(technical_context("lpg", None, "4"), "fuel_type_code=lpg;gear_number=4")
        self.assertEqual(technical_context("", None, ""), "fuel_type_code=")

    def test_sqlite_and_project_state_cover_new_column(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "dkb.sqlite"
            completed = subprocess.run(
                [sys.executable, "tools/dkb.py", "sqlite", "--output", str(database)],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            with sqlite3.connect(database) as connection:
                columns = [row[1] for row in connection.execute("PRAGMA table_info(configuration_attribute_values)")]
                populated = connection.execute(
                    "SELECT COUNT(*) FROM configuration_attribute_values WHERE gear_number <> ''"
                ).fetchone()[0]
        self.assertIn("gear_number", columns)
        _, rows = read_values()
        self.assertEqual(populated, sum(bool(row["gear_number"]) for row in rows))
        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 821)
        self.assertGreaterEqual(state["baseline"]["rows"], 8782)


if __name__ == "__main__":
    unittest.main()
