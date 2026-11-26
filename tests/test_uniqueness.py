import csv
import tempfile
import unittest
from pathlib import Path

from tools.validators.uniqueness import (
    validate_unique_columns,
    validate_unique_keys,
)


class UniqueColumnValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_csv(
        self,
        relative_path: str,
        header: list[str],
        rows: list[list[str]],
    ) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows(rows)

        return path

    def test_accepts_unique_id_and_code(self) -> None:
        path = self.write_csv(
            "data.csv",
            ["id", "code", "name"],
            [
                ["1", "duster", "Duster"],
                ["2", "sandero", "Sandero"],
            ],
        )

        checked_columns, errors = validate_unique_columns(path)

        self.assertEqual(checked_columns, 2)
        self.assertEqual(errors, [])

    def test_reports_duplicate_id(self) -> None:
        path = self.write_csv(
            "data.csv",
            ["id", "code"],
            [
                ["1", "duster"],
                ["1", "sandero"],
            ],
        )

        _, errors = validate_unique_columns(path)

        self.assertEqual(len(errors), 1)
        self.assertIn("duplicate id '1'", errors[0])
        self.assertIn("row 3", errors[0])
        self.assertIn("row 2", errors[0])

    def test_reports_case_insensitive_duplicate_code(self) -> None:
        path = self.write_csv(
            "data.csv",
            ["id", "code"],
            [
                ["1", "Duster"],
                ["2", "duster"],
            ],
        )

        _, errors = validate_unique_columns(path)

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "duplicate code 'duster'",
            errors[0],
        )

    def test_reports_empty_id(self) -> None:
        path = self.write_csv(
            "data.csv",
            ["id", "code"],
            [["", "duster"]],
        )

        _, errors = validate_unique_columns(path)

        self.assertEqual(
            errors,
            [f"{path}: row 2: empty key in 'id'"],
        )

    def test_reports_empty_code(self) -> None:
        path = self.write_csv(
            "data.csv",
            ["id", "code"],
            [["1", ""]],
        )

        _, errors = validate_unique_columns(path)

        self.assertEqual(
            errors,
            [f"{path}: row 2: empty key in 'code'"],
        )

    def test_checks_file_with_only_code(self) -> None:
        path = self.write_csv(
            "enum.csv",
            ["code", "name"],
            [
                ["petrol", "Petrol"],
                ["diesel", "Diesel"],
            ],
        )

        checked_columns, errors = validate_unique_columns(path)

        self.assertEqual(checked_columns, 1)
        self.assertEqual(errors, [])

    def test_ignores_file_without_key_columns(self) -> None:
        path = self.write_csv(
            "rules.csv",
            ["field", "rule"],
            [["status", "required"]],
        )

        checked_columns, errors = validate_unique_columns(path)

        self.assertEqual(checked_columns, 0)
        self.assertEqual(errors, [])

    def test_scans_all_master_csv_files(self) -> None:
        self.write_csv(
            "data/master/models.csv",
            ["id", "code", "name"],
            [
                ["1", "duster", "Duster"],
                ["2", "sandero", "Sandero"],
            ],
        )
        self.write_csv(
            "data/master/enums/fuel_types.csv",
            ["code", "name"],
            [
                ["petrol", "Petrol"],
                ["PETROL", "Duplicate"],
            ],
        )
        self.write_csv(
            "data/master/validation_rules.csv",
            ["field", "rule"],
            [["status", "required"]],
        )

        checked_columns, errors = validate_unique_keys(
            self.root
        )

        self.assertEqual(checked_columns, 3)
        self.assertEqual(len(errors), 1)
        self.assertIn(
            "data/master/enums/fuel_types.csv",
            errors[0],
        )
        self.assertIn(
            "duplicate code 'PETROL'",
            errors[0],
        )


if __name__ == "__main__":
    unittest.main()
