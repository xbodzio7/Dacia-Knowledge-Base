from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from tools.validators.rule_execution import (
    RULES_PATH,
    SUBJECT_PATH,
    execute_data_rules,
)


class RuleExecutionTests(unittest.TestCase):
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
    ) -> None:
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

    def write_subject(
        self,
        rows: list[list[str]],
    ) -> None:
        self.write_csv(
            SUBJECT_PATH,
            [
                "id",
                "code",
                "category",
                "name",
                "status",
            ],
            rows,
        )

    def write_rules(
        self,
        rows: list[list[str]],
    ) -> None:
        self.write_csv(
            RULES_PATH,
            [
                "field",
                "rule",
                "severity",
                "message",
            ],
            rows,
        )

    def test_accepts_all_supported_rules(self) -> None:
        self.write_subject(
            [
                ["1", "alpha", "Engine", "Alpha", "active"],
                ["2", "beta", "Engine", "Beta", "draft"],
            ]
        )
        self.write_csv(
            "data/master/categories.csv",
            ["name"],
            [["Engine"]],
        )
        self.write_rules(
            [
                ["code", "unique", "error", "Unique"],
                ["name", "not_empty", "error", "Required"],
                [
                    "category",
                    "exists(categories.csv.name)",
                    "error",
                    "Known category",
                ],
                [
                    "status",
                    "in(active|draft)",
                    "error",
                    "Known status",
                ],
            ]
        )

        checked, records, errors, warnings = (
            execute_data_rules(self.root)
        )

        self.assertEqual(checked, 4)
        self.assertEqual(records, 2)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_reports_case_insensitive_unique_duplicate(
        self,
    ) -> None:
        self.write_subject(
            [
                ["1", "Alpha", "Engine", "First", "active"],
                ["2", "alpha", "Engine", "Second", "active"],
            ]
        )
        self.write_rules(
            [["code", "unique", "error", "Unique"]]
        )

        _, _, errors, warnings = execute_data_rules(
            self.root
        )

        self.assertEqual(len(errors), 1)
        self.assertIn("first seen at row 2", errors[0])
        self.assertEqual(warnings, [])

    def test_reports_not_empty_violation(self) -> None:
        self.write_subject(
            [["1", "alpha", "Engine", "", "active"]]
        )
        self.write_rules(
            [["name", "not_empty", "error", "Required"]]
        )

        _, _, errors, _ = execute_data_rules(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn("not_empty", errors[0])

    def test_classifies_warning_severity(self) -> None:
        self.write_subject(
            [["1", "alpha", "Engine", "", "active"]]
        )
        self.write_rules(
            [["name", "not_empty", "warning", "Recommended"]]
        )

        _, _, errors, warnings = execute_data_rules(
            self.root
        )

        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn("Recommended", warnings[0])

    def test_reports_missing_exists_value(self) -> None:
        self.write_subject(
            [["1", "alpha", "Unknown", "Alpha", "active"]]
        )
        self.write_csv(
            "data/master/categories.csv",
            ["name"],
            [["Engine"]],
        )
        self.write_rules(
            [[
                "category",
                "exists(categories.csv.name)",
                "error",
                "Known category",
            ]]
        )

        _, _, errors, _ = execute_data_rules(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn("value 'Unknown'", errors[0])

    def test_allows_empty_exists_value(self) -> None:
        self.write_subject(
            [["1", "alpha", "", "Alpha", "active"]]
        )
        self.write_csv(
            "data/master/categories.csv",
            ["name"],
            [["Engine"]],
        )
        self.write_rules(
            [[
                "category",
                "exists(categories.csv.name)",
                "warning",
                "Known category",
            ]]
        )

        _, _, errors, warnings = execute_data_rules(
            self.root
        )

        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_reports_invalid_in_value(self) -> None:
        self.write_subject(
            [["1", "alpha", "Engine", "Alpha", "archived"]]
        )
        self.write_rules(
            [[
                "status",
                "in(active|draft)",
                "error",
                "Known status",
            ]]
        )

        _, _, errors, _ = execute_data_rules(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn("value 'archived'", errors[0])

    def test_reports_missing_subject_file(self) -> None:
        self.write_rules(
            [["code", "unique", "error", "Unique"]]
        )

        checked, records, errors, warnings = (
            execute_data_rules(self.root)
        )

        self.assertEqual(checked, 0)
        self.assertEqual(records, 0)
        self.assertEqual(
            errors,
            [f"{SUBJECT_PATH}: file not found"],
        )
        self.assertEqual(warnings, [])

    def test_reports_missing_rules_file(self) -> None:
        self.write_subject(
            [["1", "alpha", "Engine", "Alpha", "active"]]
        )

        checked, records, errors, warnings = (
            execute_data_rules(self.root)
        )

        self.assertEqual(checked, 0)
        self.assertEqual(records, 0)
        self.assertEqual(
            errors,
            [f"{RULES_PATH}: file not found"],
        )
        self.assertEqual(warnings, [])

    def test_reports_missing_exists_target_file(self) -> None:
        self.write_subject(
            [["1", "alpha", "Engine", "Alpha", "active"]]
        )
        self.write_rules(
            [[
                "category",
                "exists(categories.csv.name)",
                "error",
                "Known category",
            ]]
        )

        _, _, errors, _ = execute_data_rules(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "data/master/categories.csv: file not found",
            errors[0],
        )

    def test_reports_missing_exists_target_column(self) -> None:
        self.write_subject(
            [["1", "alpha", "Engine", "Alpha", "active"]]
        )
        self.write_csv(
            "data/master/categories.csv",
            ["code"],
            [["engine"]],
        )
        self.write_rules(
            [[
                "category",
                "exists(categories.csv.name)",
                "error",
                "Known category",
            ]]
        )

        _, _, errors, _ = execute_data_rules(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "missing target column 'name'",
            errors[0],
        )

    def test_reports_unsupported_expression(self) -> None:
        self.write_subject(
            [["1", "alpha", "Engine", "Alpha", "active"]]
        )
        self.write_rules(
            [["code", "positive", "error", "Positive"]]
        )

        _, _, errors, _ = execute_data_rules(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "unsupported rule expression 'positive'",
            errors[0],
        )

    def test_reports_invalid_severity(self) -> None:
        self.write_subject(
            [["1", "alpha", "Engine", "Alpha", "active"]]
        )
        self.write_rules(
            [["code", "unique", "fatal", "Unique"]]
        )

        checked, _, errors, _ = execute_data_rules(
            self.root
        )

        self.assertEqual(checked, 0)
        self.assertEqual(len(errors), 1)
        self.assertIn("contract is not executable", errors[0])


if __name__ == "__main__":
    unittest.main()
