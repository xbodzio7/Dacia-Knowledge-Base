from __future__ import annotations

import csv
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from tools.search import highlight, search


class SearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_csv(
        self,
        relative_path: str,
        headers: list[str],
        rows: list[list[str]],
        encoding: str = "utf-8",
    ) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open(
            "w",
            encoding=encoding,
            newline="",
        ) as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            writer.writerows(rows)

        return path

    def run_search(
        self,
        phrase: str,
        field: str | None = None,
        export: Path | None = None,
    ) -> tuple[tuple[int, int], str]:
        output = StringIO()

        with redirect_stdout(output):
            result = search(
                self.root,
                phrase,
                field,
                export,
            )

        return result, output.getvalue()

    def test_highlight_is_case_insensitive(self) -> None:
        self.assertEqual(
            highlight(
                "Duster duster DUSTER",
                "duster",
            ),
            "[Duster] [duster] [DUSTER]",
        )

    def test_searches_all_fields(self) -> None:
        self.write_csv(
            "data/master/models.csv",
            ["id", "name"],
            [
                ["1", "Duster"],
                ["2", "Sandero"],
            ],
        )

        result, output = self.run_search(
            "duster"
        )

        self.assertEqual(result, (1, 1))
        self.assertIn("[Duster]", output)
        self.assertIn(
            "Found 1 matching record(s) "
            "in 1 file(s).",
            output,
        )

    def test_limits_search_to_selected_field(
        self,
    ) -> None:
        self.write_csv(
            "data/master/models.csv",
            ["code", "name"],
            [["duster", "Sandero"]],
        )

        result, output = self.run_search(
            "duster",
            field="name",
        )

        self.assertEqual(result, (0, 0))
        self.assertIn(
            "No matching records found.",
            output,
        )

    def test_exports_consistent_union_of_columns(
        self,
    ) -> None:
        self.write_csv(
            "data/master/a_models.csv",
            ["id", "name"],
            [["1", "Duster"]],
        )
        self.write_csv(
            "data/master/b_engines.csv",
            ["id", "code", "power"],
            [["2", "duster_engine", "110"]],
        )

        export = (
            self.root
            / "reports"
            / "duster.csv"
        )

        result, _ = self.run_search(
            "duster",
            export=export,
        )

        with export.open(
            encoding="utf-8",
            newline="",
        ) as handle:
            rows = list(csv.reader(handle))

        self.assertEqual(result, (2, 2))
        self.assertEqual(
            rows[0],
            [
                "file",
                "row",
                "id",
                "name",
                "code",
                "power",
            ],
        )
        self.assertEqual(len(rows), 3)
        self.assertTrue(
            all(
                len(row) == len(rows[0])
                for row in rows
            )
        )

    def test_does_not_search_its_own_export(
        self,
    ) -> None:
        self.write_csv(
            "data/master/models.csv",
            ["id", "name"],
            [["1", "Duster"]],
        )

        export = (
            self.root
            / "reports"
            / "results.csv"
        )

        result, _ = self.run_search(
            "duster",
            export=export,
        )

        with export.open(
            encoding="utf-8",
            newline="",
        ) as handle:
            rows = list(csv.reader(handle))

        self.assertEqual(result, (1, 1))
        self.assertEqual(len(rows), 2)

    def test_accepts_utf8_bom(self) -> None:
        self.write_csv(
            "data/master/models.csv",
            ["id", "name"],
            [["1", "Duster"]],
            encoding="utf-8-sig",
        )

        result, output = self.run_search(
            "duster",
            field="name",
        )

        self.assertEqual(result, (1, 1))
        self.assertIn("[Duster]", output)


if __name__ == "__main__":
    unittest.main()
