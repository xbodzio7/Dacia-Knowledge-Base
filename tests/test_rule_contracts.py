from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from tools.validators.rule_contracts import (
    RULES_PATH,
    SUBJECT_PATH,
    validate_rule_contracts,
)


class RuleContractValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

        self.write_csv(
            SUBJECT_PATH,
            ["id", "code", "category", "name"],
            [["1", "engine_power", "Engine", "Power"]],
        )

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

    def write_rules(
        self,
        rows: list[list[str]],
    ) -> None:
        self.write_csv(
            RULES_PATH,
            ["field", "rule", "severity", "message"],
            rows,
        )

    def test_accepts_simple_rules(self) -> None:
        self.write_rules(
            [
                ["id", "unique", "error", "ID must be unique"],
                ["name", "not_empty", "warning", "Name recommended"],
            ]
        )

        checked, errors = validate_rule_contracts(self.root)

        self.assertEqual(checked, 2)
        self.assertEqual(errors, [])

    def test_accepts_exists_rule(self) -> None:
        self.write_csv(
            "data/master/domains.csv",
            ["domain", "subdomain"],
            [["Vehicle", "Engine"]],
        )
        self.write_rules(
            [[
                "category",
                "exists(domains.csv.subdomain)",
                "error",
                "Category must exist",
            ]]
        )

        checked, errors = validate_rule_contracts(self.root)

        self.assertEqual(checked, 1)
        self.assertEqual(errors, [])

    def test_accepts_in_rule(self) -> None:
        self.write_rules(
            [[
                "category",
                "in(Engine|Vehicle)",
                "error",
                "Invalid category",
            ]]
        )

        checked, errors = validate_rule_contracts(self.root)

        self.assertEqual(checked, 1)
        self.assertEqual(errors, [])

    def test_rejects_unknown_subject_field(self) -> None:
        self.write_rules(
            [[
                "display_name",
                "not_empty",
                "error",
                "Required",
            ]]
        )

        _, errors = validate_rule_contracts(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "field 'display_name' does not exist",
            errors[0],
        )

    def test_rejects_unsupported_rule(self) -> None:
        self.write_rules(
            [["id", "positive", "error", "Must be positive"]]
        )

        _, errors = validate_rule_contracts(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "unsupported rule expression 'positive'",
            errors[0],
        )

    def test_rejects_invalid_severity(self) -> None:
        self.write_rules(
            [["id", "unique", "fatal", "Must be unique"]]
        )

        _, errors = validate_rule_contracts(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn("invalid severity 'fatal'", errors[0])

    def test_rejects_empty_message(self) -> None:
        self.write_rules(
            [["id", "unique", "error", ""]]
        )

        _, errors = validate_rule_contracts(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn("empty required message", errors[0])

    def test_rejects_duplicate_rule_definition(self) -> None:
        self.write_rules(
            [
                ["id", "unique", "error", "First"],
                ["id", "unique", "error", "Second"],
            ]
        )

        checked, errors = validate_rule_contracts(self.root)

        self.assertEqual(checked, 2)
        self.assertEqual(len(errors), 1)
        self.assertIn("duplicate rule 'unique'", errors[0])

    def test_reports_missing_rules_file(self) -> None:
        checked, errors = validate_rule_contracts(self.root)

        self.assertEqual(checked, 0)
        self.assertEqual(
            errors,
            [f"{RULES_PATH}: file not found"],
        )

    def test_reports_missing_required_column(self) -> None:
        self.write_csv(
            RULES_PATH,
            ["field", "rule", "severity"],
            [["id", "unique", "error"]],
        )

        checked, errors = validate_rule_contracts(self.root)

        self.assertEqual(checked, 0)
        self.assertEqual(
            errors,
            [f"{RULES_PATH}: missing column 'message'"],
        )

    def test_reports_missing_exists_target_file(self) -> None:
        self.write_rules(
            [[
                "category",
                "exists(domains.csv.subdomain)",
                "error",
                "Category must exist",
            ]]
        )

        _, errors = validate_rule_contracts(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "data/master/domains.csv: file not found",
            errors[0],
        )

    def test_reports_missing_exists_target_column(self) -> None:
        self.write_csv(
            "data/master/domains.csv",
            ["domain", "name"],
            [["Vehicle", "Engine"]],
        )
        self.write_rules(
            [[
                "category",
                "exists(domains.csv.subdomain)",
                "error",
                "Category must exist",
            ]]
        )

        _, errors = validate_rule_contracts(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "references missing column 'subdomain'",
            errors[0],
        )


if __name__ == "__main__":
    unittest.main()
