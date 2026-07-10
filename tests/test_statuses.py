from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from tools.validators.statuses import (
    ACTIVE_STATUSES,
    LIFECYCLE_STATUSES,
    STATUS_RULES,
    validate_status_file,
    validate_statuses,
)


class StatusValidationTests(unittest.TestCase):
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

    def test_accepts_active_catalog_status(self) -> None:
        path = self.write_csv(
            "catalog.csv",
            ["id", "status"],
            [["1", "active"]],
        )

        checked, errors = validate_status_file(
            path,
            ACTIVE_STATUSES,
        )

        self.assertEqual(checked, 1)
        self.assertEqual(errors, [])

    def test_accepts_current_open_range(self) -> None:
        path = self.write_csv(
            "models.csv",
            ["status", "production_to"],
            [["current", ""]],
        )

        checked, errors = validate_status_file(
            path,
            LIFECYCLE_STATUSES,
            end_column="production_to",
        )

        self.assertEqual(checked, 1)
        self.assertEqual(errors, [])

    def test_accepts_archived_closed_range(self) -> None:
        path = self.write_csv(
            "models.csv",
            ["status", "production_to"],
            [["archived", "2020"]],
        )

        checked, errors = validate_status_file(
            path,
            LIFECYCLE_STATUSES,
            end_column="production_to",
        )

        self.assertEqual(checked, 1)
        self.assertEqual(errors, [])

    def test_rejects_empty_status(self) -> None:
        path = self.write_csv(
            "catalog.csv",
            ["id", "status"],
            [["1", ""]],
        )

        _, errors = validate_status_file(
            path,
            ACTIVE_STATUSES,
        )

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "empty required status",
            errors[0],
        )

    def test_rejects_unknown_status(self) -> None:
        path = self.write_csv(
            "models.csv",
            ["status"],
            [["deprecated"]],
        )

        _, errors = validate_status_file(
            path,
            LIFECYCLE_STATUSES,
        )

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "invalid status 'deprecated'",
            errors[0],
        )
        self.assertIn(
            "archived, current",
            errors[0],
        )

    def test_rejects_incorrect_status_case(self) -> None:
        path = self.write_csv(
            "models.csv",
            ["status"],
            [["Current"]],
        )

        _, errors = validate_status_file(
            path,
            LIFECYCLE_STATUSES,
        )

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "invalid status 'Current'",
            errors[0],
        )

    def test_rejects_current_closed_range(self) -> None:
        path = self.write_csv(
            "models.csv",
            ["status", "production_to"],
            [["current", "2024"]],
        )

        _, errors = validate_status_file(
            path,
            LIFECYCLE_STATUSES,
            end_column="production_to",
        )

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "status 'current' requires an empty",
            errors[0],
        )

    def test_rejects_archived_open_range(self) -> None:
        path = self.write_csv(
            "models.csv",
            ["status", "production_to"],
            [["archived", ""]],
        )

        _, errors = validate_status_file(
            path,
            LIFECYCLE_STATUSES,
            end_column="production_to",
        )

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "status 'archived' requires a non-empty",
            errors[0],
        )

    def test_reports_missing_status_column(self) -> None:
        path = self.write_csv(
            "catalog.csv",
            ["id", "name"],
            [["1", "Example"]],
        )

        checked, errors = validate_status_file(
            path,
            ACTIVE_STATUSES,
        )

        self.assertEqual(checked, 0)
        self.assertEqual(len(errors), 1)
        self.assertIn(
            "missing column 'status'",
            errors[0],
        )

    def test_reports_missing_end_column(self) -> None:
        path = self.write_csv(
            "models.csv",
            ["status"],
            [["current"]],
        )

        checked, errors = validate_status_file(
            path,
            LIFECYCLE_STATUSES,
            end_column="production_to",
        )

        self.assertEqual(checked, 0)
        self.assertEqual(len(errors), 1)
        self.assertIn(
            "missing column 'production_to'",
            errors[0],
        )

    def test_reports_missing_file(self) -> None:
        path = self.root / "missing.csv"

        checked, errors = validate_status_file(
            path,
            ACTIVE_STATUSES,
        )

        self.assertEqual(checked, 0)
        self.assertEqual(
            errors,
            [f"{path}: file not found"],
        )

    def test_scans_all_configured_files(self) -> None:
        for rule in STATUS_RULES:
            header = ["status"]
            row = ["active"]

            if rule.allowed_statuses == LIFECYCLE_STATUSES:
                row = ["current"]

            if rule.end_column is not None:
                header.append(rule.end_column)
                row.append("")

            self.write_csv(
                rule.path,
                header,
                [row],
            )

        checked, errors = validate_statuses(self.root)

        self.assertEqual(
            checked,
            len(STATUS_RULES),
        )
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
