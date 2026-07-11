from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from tools.reporting.statistics import (
    collect_statistics,
    read_csv_robust,
)


class StatisticsTests(unittest.TestCase):
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

    def test_collects_repository_totals(
        self,
    ) -> None:
        self.write_csv(
            "data/master/models.csv",
            ["id", "name"],
            [
                ["1", "Duster"],
                ["2", "Sandero"],
            ],
        )
        self.write_csv(
            "data/master/engines.csv",
            ["id", "code"],
            [["1", "tce90"]],
        )

        stats = collect_statistics(self.root)

        self.assertEqual(stats["csv_files"], 2)
        self.assertEqual(stats["rows"], 3)
        self.assertEqual(stats["empty_files"], 0)

    def test_calculates_completeness(
        self,
    ) -> None:
        self.write_csv(
            "data/master/models.csv",
            ["id", "name"],
            [
                ["1", "Duster"],
                ["2", ""],
            ],
        )

        stats = collect_statistics(self.root)
        dataset = stats["datasets"][0]

        self.assertEqual(
            dataset["completeness"],
            75.0,
        )
        self.assertEqual(dataset["columns"], 2)
        self.assertEqual(dataset["rows"], 2)

    def test_counts_header_only_file_as_empty(
        self,
    ) -> None:
        self.write_csv(
            "data/master/models.csv",
            ["id", "name"],
            [],
        )

        stats = collect_statistics(self.root)
        dataset = stats["datasets"][0]

        self.assertEqual(stats["empty_files"], 1)
        self.assertEqual(dataset["rows"], 0)
        self.assertEqual(
            dataset["completeness"],
            100.0,
        )

    def test_sorts_largest_dataset_first(
        self,
    ) -> None:
        self.write_csv(
            "data/master/small.csv",
            ["id"],
            [["1"]],
        )
        self.write_csv(
            "data/master/large.csv",
            ["id"],
            [
                ["1"],
                ["2"],
                ["3"],
            ],
        )

        stats = collect_statistics(self.root)

        self.assertEqual(
            [
                dataset["name"]
                for dataset in stats["datasets"]
            ],
            [
                "large.csv",
                "small.csv",
            ],
        )

    def test_accepts_utf8_bom(
        self,
    ) -> None:
        path = self.write_csv(
            "data/master/models.csv",
            ["id", "name"],
            [["1", "Duster"]],
            encoding="utf-8-sig",
        )

        rows, encoding = read_csv_robust(path)

        self.assertEqual(
            rows,
            [
                ["id", "name"],
                ["1", "Duster"],
            ],
        )
        self.assertEqual(encoding, "utf-8-sig")

    def test_ignores_git_directory(
        self,
    ) -> None:
        self.write_csv(
            "data/master/models.csv",
            ["id"],
            [["1"]],
        )
        self.write_csv(
            ".git/generated.csv",
            ["id"],
            [
                ["1"],
                ["2"],
            ],
        )

        stats = collect_statistics(self.root)

        self.assertEqual(stats["csv_files"], 1)
        self.assertEqual(stats["rows"], 1)


if __name__ == "__main__":
    unittest.main()
