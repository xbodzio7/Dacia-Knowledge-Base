from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from tools.validators.references import (
    ReferenceRule,
    validate_reference_rules,
)


class ReferenceValidationTests(unittest.TestCase):
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

    def rule(self) -> ReferenceRule:
        return ReferenceRule(
            "data/source.csv",
            "target_code",
            "data/target.csv",
        )

    def test_accepts_existing_reference(self) -> None:
        self.write_csv(
            "data/target.csv",
            ["code"],
            [["alpha"]],
        )
        self.write_csv(
            "data/source.csv",
            ["id", "target_code"],
            [["1", "alpha"]],
        )

        self.assertEqual(
            validate_reference_rules(self.root, [self.rule()]),
            [],
        )

    def test_reports_missing_reference(self) -> None:
        self.write_csv(
            "data/target.csv",
            ["code"],
            [["alpha"]],
        )
        self.write_csv(
            "data/source.csv",
            ["id", "target_code"],
            [["1", "missing"]],
        )

        errors = validate_reference_rules(
            self.root,
            [self.rule()],
        )

        self.assertEqual(len(errors), 1)
        self.assertIn("value 'missing'", errors[0])
        self.assertIn("data/target.csv.code", errors[0])

    def test_reports_empty_required_reference(self) -> None:
        self.write_csv(
            "data/target.csv",
            ["code"],
            [["alpha"]],
        )
        self.write_csv(
            "data/source.csv",
            ["id", "target_code"],
            [["1", ""]],
        )

        errors = validate_reference_rules(
            self.root,
            [self.rule()],
        )

        self.assertEqual(len(errors), 1)
        self.assertIn("empty reference", errors[0])

    def test_allows_empty_optional_reference(self) -> None:
        self.write_csv(
            "data/target.csv",
            ["code"],
            [["alpha"]],
        )
        self.write_csv(
            "data/source.csv",
            ["id", "target_code"],
            [["1", ""]],
        )

        rule = ReferenceRule(
            "data/source.csv",
            "target_code",
            "data/target.csv",
            allow_empty=True,
        )

        self.assertEqual(
            validate_reference_rules(self.root, [rule]),
            [],
        )

    def test_reports_duplicate_target_key_once(self) -> None:
        self.write_csv(
            "data/target.csv",
            ["code"],
            [["alpha"], ["alpha"]],
        )
        self.write_csv(
            "data/source.csv",
            ["id", "target_code", "second_code"],
            [["1", "alpha", "alpha"]],
        )

        rules = [
            self.rule(),
            ReferenceRule(
                "data/source.csv",
                "second_code",
                "data/target.csv",
            ),
        ]

        errors = validate_reference_rules(self.root, rules)

        duplicate_errors = [
            error
            for error in errors
            if "duplicate target key" in error
        ]

        self.assertEqual(len(duplicate_errors), 1)

    def test_reports_missing_source_column(self) -> None:
        self.write_csv(
            "data/target.csv",
            ["code"],
            [["alpha"]],
        )
        self.write_csv(
            "data/source.csv",
            ["id"],
            [["1"]],
        )

        errors = validate_reference_rules(
            self.root,
            [self.rule()],
        )

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "missing source column 'target_code'",
            errors[0],
        )


if __name__ == "__main__":
    unittest.main()
