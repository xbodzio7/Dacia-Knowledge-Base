from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from tools.validators.year_ranges import (
    YEAR_RANGE_RULES,
    validate_year_range_file,
    validate_year_ranges,
)


class YearRangeValidationTests(unittest.TestCase):
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

    def test_accepts_closed_range(self) -> None:
        path = self.write_csv(
            "models.csv",
            ["production_from", "production_to"],
            [["2020", "2024"]],
        )

        checked, errors = validate_year_range_file(
            path,
            "production_from",
            "production_to",
        )

        self.assertEqual(checked, 1)
        self.assertEqual(errors, [])

    def test_accepts_open_range(self) -> None:
        path = self.write_csv(
            "models.csv",
            ["production_from", "production_to"],
            [["2024", ""]],
        )

        checked, errors = validate_year_range_file(
            path,
            "production_from",
            "production_to",
        )

        self.assertEqual(checked, 1)
        self.assertEqual(errors, [])

    def test_rejects_empty_required_start_year(self) -> None:
        path = self.write_csv(
            "models.csv",
            ["production_from", "production_to"],
            [["", "2024"]],
        )

        _, errors = validate_year_range_file(
            path,
            "production_from",
            "production_to",
        )

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "empty required year in 'production_from'",
            errors[0],
        )

    def test_rejects_invalid_start_year_format(self) -> None:
        path = self.write_csv(
            "models.csv",
            ["production_from", "production_to"],
            [["20A4", ""]],
        )

        _, errors = validate_year_range_file(
            path,
            "production_from",
            "production_to",
        )

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "must contain a four-digit year",
            errors[0],
        )
        self.assertIn("20A4", errors[0])

    def test_rejects_invalid_end_year_format(self) -> None:
        path = self.write_csv(
            "models.csv",
            ["production_from", "production_to"],
            [["2020", "24"]],
        )

        _, errors = validate_year_range_file(
            path,
            "production_from",
            "production_to",
        )

        self.assertEqual(len(errors), 1)
        self.assertIn("'production_to'", errors[0])
        self.assertIn("got '24'", errors[0])

    def test_rejects_reversed_range(self) -> None:
        path = self.write_csv(
            "models.csv",
            ["production_from", "production_to"],
            [["2024", "2020"]],
        )

        _, errors = validate_year_range_file(
            path,
            "production_from",
            "production_to",
        )

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "end year 2020",
            errors[0],
        )
        self.assertIn(
            "precedes start year 2024",
            errors[0],
        )

    def test_reports_missing_columns(self) -> None:
        path = self.write_csv(
            "models.csv",
            ["id", "name"],
            [["1", "Duster"]],
        )

        checked, errors = validate_year_range_file(
            path,
            "production_from",
            "production_to",
        )

        self.assertEqual(checked, 0)
        self.assertEqual(len(errors), 2)
        self.assertTrue(
            any(
                "missing column 'production_from'" in error
                for error in errors
            )
        )
        self.assertTrue(
            any(
                "missing column 'production_to'" in error
                for error in errors
            )
        )

    def test_reports_missing_file(self) -> None:
        path = self.root / "missing.csv"

        checked, errors = validate_year_range_file(
            path,
            "start_year",
            "end_year",
        )

        self.assertEqual(checked, 0)
        self.assertEqual(
            errors,
            [f"{path}: file not found"],
        )

    def test_scans_all_configured_files(self) -> None:
        for rule in YEAR_RANGE_RULES:
            self.write_csv(
                rule.path,
                [rule.start_column, rule.end_column],
                [["2020", "2024"]],
            )

        checked, errors = validate_year_ranges(self.root)

        self.assertEqual(
            checked,
            len(YEAR_RANGE_RULES),
        )
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
