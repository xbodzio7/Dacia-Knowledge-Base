from __future__ import annotations

import csv
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from tools.build_sqlite import (
    BuildError,
    build_sqlite_db,
    discover_csv_files,
)


class SqliteBuildTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.master = self.root / "data" / "master"
        self.master.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_csv(
        self,
        relative_path: str,
        header: list[str],
        rows: list[list[str]],
    ) -> Path:
        path = self.master / relative_path
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

    def test_builds_database_with_expected_data(self) -> None:
        self.write_csv(
            "models.csv",
            ["id", "code"],
            [
                ["1", "duster"],
                ["2", "sandero"],
            ],
        )

        database = self.root / "reports" / "test.sqlite"
        result = build_sqlite_db(self.root, database)

        self.assertEqual(result, database.resolve())
        self.assertTrue(database.is_file())

        with closing(
            sqlite3.connect(database)
        ) as connection:
            rows = connection.execute(
                "SELECT id, code FROM models ORDER BY id"
            ).fetchall()

        self.assertEqual(
            rows,
            [
                ("1", "duster"),
                ("2", "sandero"),
            ],
        )

    def test_creates_output_parent_directory(self) -> None:
        self.write_csv(
            "models.csv",
            ["id"],
            [["1"]],
        )

        database = (
            self.root
            / "nested"
            / "directory"
            / "test.sqlite"
        )

        build_sqlite_db(self.root, database)

        self.assertTrue(database.is_file())

    def test_rejects_duplicate_table_names(
        self,
    ) -> None:
        first = self.write_csv(
            "models.csv",
            ["id"],
            [["1"]],
        )
        second = self.write_csv(
            "enums/MODELS.csv",
            ["id"],
            [["2"]],
        )

        with self.assertRaisesRegex(
            BuildError,
            "duplicate SQLite table name",
        ):
            discover_csv_files(self.master)

        self.assertTrue(first.is_file())
        self.assertTrue(second.is_file())

    def test_preserves_existing_database_on_failure(
        self,
    ) -> None:
        self.write_csv(
            "models.csv",
            ["id", "code"],
            [["1", "duster"]],
        )

        database = self.root / "test.sqlite"
        database.write_bytes(b"existing database content")

        self.write_csv(
            "broken.csv",
            ["id", "ID"],
            [["1", "2"]],
        )

        with self.assertRaisesRegex(
            BuildError,
            "duplicate column name",
        ):
            build_sqlite_db(self.root, database)

        self.assertEqual(
            database.read_bytes(),
            b"existing database content",
        )
        self.assertFalse(
            database.with_name(
                f"{database.name}.tmp"
            ).exists()
        )

    def test_replaces_existing_database_after_success(
        self,
    ) -> None:
        self.write_csv(
            "models.csv",
            ["id", "code"],
            [["1", "duster"]],
        )

        database = self.root / "test.sqlite"
        database.write_bytes(b"old content")

        build_sqlite_db(self.root, database)

        self.assertNotEqual(
            database.read_bytes(),
            b"old content",
        )

        with closing(
            sqlite3.connect(database)
        ) as connection:
            integrity = connection.execute(
                "PRAGMA integrity_check"
            ).fetchone()

        self.assertEqual(integrity, ("ok",))


if __name__ == "__main__":
    unittest.main()
