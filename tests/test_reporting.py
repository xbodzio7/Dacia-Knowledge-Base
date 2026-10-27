from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.reporting.data_dictionary import (
    generate_data_dictionary,
)
from tools.reporting.entity_catalog import (
    generate_entity_catalog,
)


class ReportingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = (
            tempfile.TemporaryDirectory()
        )
        self.root = Path(
            self.temporary_directory.name
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_csv(
        self,
        relative_path: str,
        content: str,
        encoding: str = "utf-8",
    ) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        path.write_text(
            content,
            encoding=encoding,
            newline="",
        )
        return path

    def test_entity_catalog_uses_only_master_data(
        self,
    ) -> None:
        self.write_csv(
            "data/master/models.csv",
            "id,name\n"
            "1,Duster\n"
            "2,Sandero\n",
        )
        self.write_csv(
            "data/generated/cache.csv",
            "id\n1\n2\n3\n",
        )
        self.write_csv(
            "reports/search_export.csv",
            "id\n1\n",
        )

        output = (
            self.root
            / "reports"
            / "entity_catalog.md"
        )

        generate_entity_catalog(
            self.root,
            output,
        )

        report = output.read_text(
            encoding="utf-8",
        )

        self.assertIn(
            "## data/master/models.csv",
            report,
        )
        self.assertIn("Rows: **2**", report)
        self.assertIn("- id", report)
        self.assertIn("- name", report)

        self.assertNotIn(
            "data/generated/cache.csv",
            report,
        )
        self.assertNotIn(
            "reports/search_export.csv",
            report,
        )

    def test_entity_catalog_handles_bom_and_empty_file(
        self,
    ) -> None:
        self.write_csv(
            "data/master/models.csv",
            "id,name\n1,Duster\n",
            encoding="utf-8-sig",
        )

        empty = (
            self.root
            / "data"
            / "master"
            / "empty.csv"
        )
        empty.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        empty.write_bytes(b"")

        output = self.root / "catalog.md"

        generate_entity_catalog(
            self.root,
            output,
        )

        report = output.read_text(
            encoding="utf-8",
        )

        self.assertIn("- id", report)
        self.assertNotIn("\ufeffid", report)
        self.assertIn("## data/master/empty.csv", report)
        self.assertIn("_No columns_", report)

    def test_data_dictionary_reports_coverage_statuses(
        self,
    ) -> None:
        self.write_csv(
            "data/master/models.csv",
            "id,name,notes\n"
            "1,Duster,\n"
            "2,,\n",
        )

        output = self.root / "dictionary.md"

        generate_data_dictionary(
            self.root,
            output,
        )

        report = output.read_text(
            encoding="utf-8",
        )

        empty_line = (
            "| notes | 0 | 0.0% | EMPTY |"
        )
        partial_line = (
            "| name | 1 | 50.0% | PARTIAL |"
        )
        complete_line = (
            "| id | 2 | 100.0% | OK |"
        )

        self.assertIn(empty_line, report)
        self.assertIn(partial_line, report)
        self.assertIn(complete_line, report)

        self.assertLess(
            report.index(empty_line),
            report.index(partial_line),
        )
        self.assertLess(
            report.index(partial_line),
            report.index(complete_line),
        )

    def test_data_dictionary_marks_header_only_columns_complete(
        self,
    ) -> None:
        self.write_csv(
            "data/master/units.csv",
            "id,symbol\n",
        )

        output = self.root / "dictionary.md"

        generate_data_dictionary(
            self.root,
            output,
        )

        report = output.read_text(
            encoding="utf-8",
        )

        self.assertIn("Rows: **0**", report)
        self.assertIn(
            "| id | 0 | 100.0% | OK |",
            report,
        )
        self.assertIn(
            "| symbol | 0 | 100.0% | OK |",
            report,
        )

    def test_data_dictionary_uses_master_data_and_accepts_bom(
        self,
    ) -> None:
        self.write_csv(
            "data/master/enums/fuels.csv",
            "id,name\n1,Petrol\n",
            encoding="utf-8-sig",
        )
        self.write_csv(
            "reports/export.csv",
            "id\n1\n2\n",
        )

        output = self.root / "dictionary.md"

        generate_data_dictionary(
            self.root,
            output,
        )

        report = output.read_text(
            encoding="utf-8",
        )

        self.assertIn(
            "## data/master/enums/fuels.csv",
            report,
        )
        self.assertIn(
            "| id | 1 | 100.0% | OK |",
            report,
        )
        self.assertNotIn("\ufeffid", report)
        self.assertNotIn(
            "reports/export.csv",
            report,
        )


if __name__ == "__main__":
    unittest.main()
