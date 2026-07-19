from __future__ import annotations

import csv
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from tools import build_sqlite
from tools import import_configuration_value_ranges as importer
from tools.validators.value_ranges import RANGE_FIELDS, validate_configuration_value_ranges

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"


def write_csv(path: Path, fields: list[str] | tuple[str, ...], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(fields)
        writer.writerows(rows)


class ConfigurationValueRangeTests(unittest.TestCase):
    def fixture(self) -> tuple[Path, Path]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        repository = Path(temporary.name)
        master = repository / "data" / "master"
        write_csv(
            master / "attributes.csv",
            ["id", "code", "category", "name", "data_type", "unit", "description", "status"],
            [["1", "fuel_consumption", "Efficiency", "Fuel consumption", "decimal", "L/100 km", "Combined consumption", "active"]],
        )
        write_csv(
            master / "configurations.csv",
            ["id", "code", "status"],
            [["1", "example_configuration", "active"]],
        )
        write_csv(
            master / "sources.csv",
            ["id", "code", "source_type", "title", "publisher", "market", "document_date", "external_reference", "file_path", "sha256", "status", "notes"],
            [["1", "example_source", "catalogue", "Example", "Dacia", "PL", "2026-04-01", "", "data/sources/example.pdf", "0" * 64, "active", ""]],
        )
        write_csv(
            master / "source_configurations.csv",
            ["id", "code", "source_code", "configuration_code"],
            [["1", "example_link", "example_source", "example_configuration"]],
        )
        write_csv(
            master / "enums" / "fuel_types.csv",
            ["code", "name", "description", "status"],
            [["petrol", "Petrol", "Petrol", "active"]],
        )
        write_csv(
            master / "configuration_attribute_values.csv",
            ["id", "code", "configuration_code", "attribute_code", "fuel_type_code", "value", "observation_date", "source_code", "notes"],
            [],
        )
        write_csv(master / "configuration_attribute_value_ranges.csv", RANGE_FIELDS, [])
        spec = repository / "range.json"
        spec.write_text(
            json.dumps(
                {
                    "version": 1,
                    "kind": "configuration_attribute_value_ranges",
                    "id_start": 1,
                    "attribute_code": "fuel_consumption",
                    "attribute_contract": {
                        "data_type": "decimal",
                        "unit": "L/100 km",
                        "status": "active",
                    },
                    "observation_date": "2026-04-01",
                    "fuel_type_code": "petrol",
                    "source_page": 6,
                    "source_section": "SILNIKI",
                    "notes_template": "Source page {page}, section {section}: {source_text}",
                    "rows": [
                        {
                            "configuration_code": "example_configuration",
                            "source_code": "example_source",
                            "minimum_value": "5.7",
                            "maximum_value": "6.1",
                            "lower_inclusive": True,
                            "upper_inclusive": True,
                            "source_text": "5,7-6,1",
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return repository, spec

    def test_master_table_has_exact_empty_schema(self) -> None:
        path = MASTER / "configuration_attribute_value_ranges.csv"
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
        self.assertEqual(tuple(rows[0]), RANGE_FIELDS)
        self.assertEqual(rows[1:], [])

    def test_repository_empty_range_table_is_valid(self) -> None:
        checked, errors = validate_configuration_value_ranges(ROOT)
        self.assertEqual(checked, 0)
        self.assertEqual(errors, [])

    def test_strict_spec_loads_numeric_closed_range(self) -> None:
        _, spec_path = self.fixture()
        spec = importer.load_spec(spec_path)
        self.assertEqual(spec.data_type, "decimal")
        self.assertEqual(spec.rows[0].minimum_value, "5.7")
        self.assertEqual(spec.rows[0].maximum_value, "6.1")
        self.assertTrue(spec.rows[0].lower_inclusive)
        self.assertTrue(spec.rows[0].upper_inclusive)

    def test_import_is_append_only_and_idempotent(self) -> None:
        repository, spec_path = self.fixture()
        spec = importer.load_spec(spec_path)
        planned = importer.plan_import(repository, spec)
        first = importer.apply_import(repository, spec)
        second = importer.apply_import(repository, spec)
        self.assertEqual(len(planned.missing_rows), 1)
        self.assertEqual(len(first.missing_rows), 0)
        self.assertEqual(len(first.existing_rows), 1)
        self.assertEqual(len(second.missing_rows), 0)
        self.assertEqual(len(second.existing_rows), 1)
        checked, errors = validate_configuration_value_ranges(repository)
        self.assertEqual(checked, 1)
        self.assertEqual(errors, [])

    def test_spec_rejects_noncanonical_decimal_endpoint(self) -> None:
        _, spec_path = self.fixture()
        payload = json.loads(spec_path.read_text(encoding="utf-8"))
        payload["rows"][0]["minimum_value"] = "5.70"
        spec_path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(importer.ImportSpecError, "canonical decimal"):
            importer.load_spec(spec_path)

    def test_spec_rejects_reversed_or_degenerate_range(self) -> None:
        _, spec_path = self.fixture()
        payload = json.loads(spec_path.read_text(encoding="utf-8"))
        payload["rows"][0]["minimum_value"] = "6.1"
        payload["rows"][0]["maximum_value"] = "6.1"
        spec_path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(importer.ImportSpecError, "less than maximum"):
            importer.load_spec(spec_path)

    def test_validator_rejects_scalar_range_collision(self) -> None:
        repository, spec_path = self.fixture()
        write_csv(
            repository / "data/master/configuration_attribute_values.csv",
            ["id", "code", "configuration_code", "attribute_code", "fuel_type_code", "value", "observation_date", "source_code", "notes"],
            [["1", "scalar", "example_configuration", "fuel_consumption", "petrol", "5.9", "2026-04-01", "example_source", "source"]],
        )
        with self.assertRaisesRegex(importer.ImportSpecError, "conflicts with a scalar"):
            importer.plan_import(repository, importer.load_spec(spec_path))

    def test_validator_rejects_non_numeric_attribute(self) -> None:
        repository, spec_path = self.fixture()
        attributes = repository / "data/master/attributes.csv"
        text = attributes.read_text(encoding="utf-8").replace(",decimal,", ",string,")
        attributes.write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(importer.ImportSpecError, "attribute contract differs"):
            importer.plan_import(repository, importer.load_spec(spec_path))

    def test_validator_rejects_noncanonical_inclusivity_flag(self) -> None:
        repository, spec_path = self.fixture()
        importer.apply_import(repository, importer.load_spec(spec_path))
        path = repository / "data/master/configuration_attribute_value_ranges.csv"
        text = path.read_text(encoding="utf-8").replace(",true,true,", ",yes,true,")
        path.write_text(text, encoding="utf-8")
        _, errors = validate_configuration_value_ranges(repository)
        self.assertTrue(any("lower_inclusive must be true or false" in error for error in errors))

    def test_sqlite_builder_discovers_header_only_range_table(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            database = Path(temporary) / "dkb.sqlite"
            build_sqlite.build_sqlite_db(ROOT, database)
            with sqlite3.connect(database) as connection:
                columns = [
                    row[1]
                    for row in connection.execute(
                        "PRAGMA table_info(configuration_attribute_value_ranges)"
                    ).fetchall()
                ]
                count = connection.execute(
                    "SELECT COUNT(*) FROM configuration_attribute_value_ranges"
                ).fetchone()[0]
            self.assertEqual(tuple(columns), RANGE_FIELDS)
            self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
