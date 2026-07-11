from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from tools.validators.association_intervals import (
    ASSOCIATION_INTERVAL_RULES,
    validate_association_interval_file,
    validate_association_intervals,
)


class AssociationIntervalValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.path = self.root / "relations.csv"

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_csv(
        self,
        path: Path,
        header: list[str],
        rows: list[list[str]],
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows(rows)

    def write_relations(self, rows: list[list[str]]) -> None:
        self.write_csv(
            self.path,
            [
                "model_code",
                "engine_code",
                "available_from",
                "available_to",
            ],
            rows,
        )

    def validate(self) -> tuple[int, list[str]]:
        return validate_association_interval_file(
            self.path,
            ("model_code", "engine_code"),
            display_path="relations.csv",
        )

    def test_accepts_distinct_pairs_with_same_interval(self) -> None:
        self.write_relations([
            ["model_a", "engine_a", "2020", "2024"],
            ["model_a", "engine_b", "2020", "2024"],
        ])
        checked, errors = self.validate()
        self.assertEqual(checked, 2)
        self.assertEqual(errors, [])

    def test_accepts_non_overlapping_repeated_pair(self) -> None:
        self.write_relations([
            ["model_a", "engine_a", "2020", "2021"],
            ["model_a", "engine_a", "2022", ""],
        ])
        checked, errors = self.validate()
        self.assertEqual(checked, 2)
        self.assertEqual(errors, [])

    def test_rejects_exact_duplicate_interval(self) -> None:
        self.write_relations([
            ["model_a", "engine_a", "2020", "2024"],
            ["model_a", "engine_a", "2020", "2024"],
        ])
        _, errors = self.validate()
        self.assertEqual(len(errors), 1)
        self.assertIn("duplicate interval 2020-2024", errors[0])

    def test_rejects_overlapping_closed_intervals(self) -> None:
        self.write_relations([
            ["model_a", "engine_a", "2020", "2023"],
            ["model_a", "engine_a", "2022", "2024"],
        ])
        _, errors = self.validate()
        self.assertEqual(len(errors), 1)
        self.assertIn("overlap", errors[0])

    def test_rejects_shared_boundary_year(self) -> None:
        self.write_relations([
            ["model_a", "engine_a", "2020", "2022"],
            ["model_a", "engine_a", "2022", "2024"],
        ])
        _, errors = self.validate()
        self.assertEqual(len(errors), 1)
        self.assertIn("overlap", errors[0])

    def test_rejects_interval_after_open_interval(self) -> None:
        self.write_relations([
            ["model_a", "engine_a", "2020", ""],
            ["model_a", "engine_a", "2025", ""],
        ])
        _, errors = self.validate()
        self.assertEqual(len(errors), 1)
        self.assertIn("2020-open", errors[0])

    def test_reports_empty_key_column(self) -> None:
        self.write_relations([
            ["model_a", "", "2020", "2024"],
        ])
        checked, errors = self.validate()
        self.assertEqual(checked, 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("empty 'engine_code'", errors[0])

    def test_reports_missing_column(self) -> None:
        self.write_csv(
            self.path,
            ["model_code", "engine_code", "available_from"],
            [["model_a", "engine_a", "2020"]],
        )
        checked, errors = self.validate()
        self.assertEqual(checked, 0)
        self.assertEqual(
            errors,
            ["relations.csv: missing column 'available_to'"],
        )

    def test_reports_missing_file(self) -> None:
        checked, errors = self.validate()
        self.assertEqual(checked, 0)
        self.assertEqual(
            errors,
            ["relations.csv: file not found"],
        )

    def test_rejects_reversed_interval(self) -> None:
        self.write_relations([
            ["model_a", "engine_a", "2024", "2023"],
        ])
        _, errors = self.validate()
        self.assertEqual(len(errors), 1)
        self.assertIn("precedes start year", errors[0])

    def test_scans_all_configured_files(self) -> None:
        for rule in ASSOCIATION_INTERVAL_RULES:
            self.write_csv(
                self.root / rule.path,
                [
                    *rule.key_columns,
                    rule.start_column,
                    rule.end_column,
                ],
                [["model_a", "related_a", "2020", ""]],
            )

        checked, errors = validate_association_intervals(
            self.root,
        )
        self.assertEqual(
            checked,
            len(ASSOCIATION_INTERVAL_RULES),
        )
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
