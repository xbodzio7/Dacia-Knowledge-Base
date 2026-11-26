from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from tools.validators.association_ranges import (
    ASSOCIATION_RANGE_RULES,
    AssociationRangeRule,
    validate_association_range_rule,
    validate_association_ranges,
)


class AssociationRangeValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

        self.rule = AssociationRangeRule(
            relation_path="relations.csv",
            relation_code_column="model_code",
            relation_start_column="available_from",
            relation_end_column="available_to",
            parent_path="models.csv",
            parent_code_column="code",
            parent_start_column="production_from",
            parent_end_column="production_to",
            entity_label="model",
        )

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

    def write_parent(
        self,
        start: str = "2020",
        end: str = "",
    ) -> None:
        self.write_csv(
            "models.csv",
            ["code", "production_from", "production_to"],
            [["model_a", start, end]],
        )

    def write_relation(
        self,
        start: str = "2020",
        end: str = "",
        code: str = "model_a",
    ) -> None:
        self.write_csv(
            "relations.csv",
            ["model_code", "available_from", "available_to"],
            [[code, start, end]],
        )

    def test_accepts_range_inside_closed_parent(self) -> None:
        self.write_parent("2020", "2024")
        self.write_relation("2021", "2023")

        checked, errors = validate_association_range_rule(
            self.root,
            self.rule,
        )

        self.assertEqual(checked, 1)
        self.assertEqual(errors, [])

    def test_accepts_open_range_inside_open_parent(self) -> None:
        self.write_parent("2020", "")
        self.write_relation("2021", "")

        checked, errors = validate_association_range_rule(
            self.root,
            self.rule,
        )

        self.assertEqual(checked, 1)
        self.assertEqual(errors, [])

    def test_rejects_relation_start_before_parent(self) -> None:
        self.write_parent("2020", "")
        self.write_relation("2019", "2021")

        _, errors = validate_association_range_rule(
            self.root,
            self.rule,
        )

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "2019-2021 is outside parent lifetime 2020-open",
            errors[0],
        )

    def test_rejects_relation_end_after_parent(self) -> None:
        self.write_parent("2020", "2024")
        self.write_relation("2021", "2025")

        _, errors = validate_association_range_rule(
            self.root,
            self.rule,
        )

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "2021-2025 is outside parent lifetime 2020-2024",
            errors[0],
        )

    def test_rejects_open_relation_for_closed_parent(self) -> None:
        self.write_parent("2020", "2024")
        self.write_relation("2021", "")

        _, errors = validate_association_range_rule(
            self.root,
            self.rule,
        )

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "2021-open is outside parent lifetime 2020-2024",
            errors[0],
        )

    def test_reports_missing_parent_code(self) -> None:
        self.write_parent()
        self.write_relation(code="unknown")

        _, errors = validate_association_range_rule(
            self.root,
            self.rule,
        )

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "model 'unknown' not found",
            errors[0],
        )

    def test_reports_missing_relation_column(self) -> None:
        self.write_parent()
        self.write_csv(
            "relations.csv",
            ["model_code", "available_from"],
            [["model_a", "2020"]],
        )

        checked, errors = validate_association_range_rule(
            self.root,
            self.rule,
        )

        self.assertEqual(checked, 0)
        self.assertEqual(len(errors), 1)
        self.assertIn(
            "missing column 'available_to'",
            errors[0],
        )

    def test_reports_missing_parent_column(self) -> None:
        self.write_csv(
            "models.csv",
            ["code", "production_from"],
            [["model_a", "2020"]],
        )
        self.write_relation()

        checked, errors = validate_association_range_rule(
            self.root,
            self.rule,
        )

        self.assertEqual(checked, 0)
        self.assertEqual(len(errors), 1)
        self.assertIn(
            "missing column 'production_to'",
            errors[0],
        )

    def test_reports_missing_relation_file(self) -> None:
        self.write_parent()

        checked, errors = validate_association_range_rule(
            self.root,
            self.rule,
        )

        self.assertEqual(checked, 0)
        self.assertEqual(
            errors,
            ["relations.csv: file not found"],
        )

    def test_rejects_reversed_relation_range(self) -> None:
        self.write_parent()
        self.write_relation("2024", "2023")

        _, errors = validate_association_range_rule(
            self.root,
            self.rule,
        )

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "end year 2023 precedes start year 2024",
            errors[0],
        )

    def test_scans_all_configured_rules(self) -> None:
        self.write_csv(
            "data/master/models.csv",
            ["code", "production_from", "production_to"],
            [["model_a", "2020", ""]],
        )
        self.write_csv(
            "data/master/engines.csv",
            ["code", "start_year", "end_year"],
            [["engine_a", "2020", ""]],
        )
        self.write_csv(
            "data/master/model_engines.csv",
            [
                "model_code",
                "engine_code",
                "available_from",
                "available_to",
            ],
            [["model_a", "engine_a", "2020", ""]],
        )
        self.write_csv(
            "data/master/model_gearboxes.csv",
            [
                "model_code",
                "available_from",
                "available_to",
            ],
            [["model_a", "2020", ""]],
        )

        checked, errors = validate_association_ranges(
            self.root,
        )

        self.assertEqual(
            checked,
            len(ASSOCIATION_RANGE_RULES),
        )
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
