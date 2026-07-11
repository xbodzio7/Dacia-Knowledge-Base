from __future__ import annotations

import csv
import sqlite3
from contextlib import closing
import tempfile
import unittest
from pathlib import Path

from tools.build_sqlite import build_sqlite_db
from tools.verify_sqlite import (
    VerificationError,
    main,
    verify_sqlite_db,
)


class SqliteVerificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.master = self.root / "data" / "master"
        self.master.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_csv(
        self,
        name: str,
        header: list[str],
        rows: list[list[str]],
    ) -> None:
        path = self.master / name

        with path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows(rows)

    def build_database(self) -> Path:
        database = self.root / "test.sqlite"
        return build_sqlite_db(self.root, database)

    def create_valid_database(self) -> Path:
        self.write_csv(
            "models.csv",
            ["id", "code"],
            [
                ["1", "duster"],
                ["2", "sandero"],
            ],
        )
        self.write_csv(
            "attributes.csv",
            ["id", "code"],
            [
                ["1", "engine_power"],
            ],
        )
        return self.build_database()

    def test_accepts_matching_database(self) -> None:
        database = self.create_valid_database()

        table_count, row_count = verify_sqlite_db(
            self.root,
            database,
        )

        self.assertEqual(table_count, 2)
        self.assertEqual(row_count, 3)

    def test_reports_missing_database(self) -> None:
        with self.assertRaisesRegex(
            VerificationError,
            "does not exist",
        ):
            verify_sqlite_db(
                self.root,
                self.root / "missing.sqlite",
            )

    def test_reports_missing_table(self) -> None:
        database = self.create_valid_database()

        with closing(
            sqlite3.connect(database)
        ) as connection:
            connection.execute(
                "DROP TABLE attributes"
            )

        with self.assertRaisesRegex(
            VerificationError,
            "missing SQLite tables: attributes",
        ):
            verify_sqlite_db(
                self.root,
                database,
            )

    def test_reports_unexpected_table(self) -> None:
        database = self.create_valid_database()

        with closing(
            sqlite3.connect(database)
        ) as connection:
            connection.execute(
                "CREATE TABLE unexpected (id TEXT)"
            )

        with self.assertRaisesRegex(
            VerificationError,
            "unexpected SQLite tables: unexpected",
        ):
            verify_sqlite_db(
                self.root,
                database,
            )

    def test_reports_row_count_mismatch(self) -> None:
        database = self.create_valid_database()

        with closing(
            sqlite3.connect(database)
        ) as connection:
            connection.execute(
                "DELETE FROM models WHERE id = '2'"
            )
            connection.commit()

        with self.assertRaisesRegex(
            VerificationError,
            "CSV=2, SQLite=1",
        ):
            verify_sqlite_db(
                self.root,
                database,
            )

    def test_reports_invalid_database_file(self) -> None:
        self.write_csv(
            "models.csv",
            ["id", "code"],
            [
                ["1", "duster"],
            ],
        )

        database = self.root / "invalid.sqlite"
        database.write_text(
            "not a SQLite database",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(
            VerificationError,
            "cannot verify SQLite database",
        ):
            verify_sqlite_db(
                self.root,
                database,
            )

    def test_cli_reports_missing_database(self) -> None:
        result = main([
            str(self.root / "missing.sqlite"),
        ])

        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
