#!/usr/bin/env python3
"""
Verify parity between DKB master CSV files and SQLite.
"""

from __future__ import annotations

import argparse
import sqlite3
from contextlib import closing
import sys
from pathlib import Path
from typing import Sequence

try:
    from .build_sqlite import (
        BuildError,
        discover_csv_files,
        quote_identifier,
        read_csv,
    )
except ImportError:
    from build_sqlite import (
        BuildError,
        discover_csv_files,
        quote_identifier,
        read_csv,
    )


class VerificationError(RuntimeError):
    """Raised when SQLite does not match source CSV data."""


def _database_tables(
    connection: sqlite3.Connection,
) -> dict[str, str]:
    """Return normalized and original user table names."""

    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        """
    )

    tables: dict[str, str] = {}

    for row in rows:
        name = str(row[0])
        normalized = name.casefold()

        if normalized in tables:
            raise VerificationError(
                "SQLite contains duplicate table names: "
                f"'{tables[normalized]}' and '{name}'"
            )

        tables[normalized] = name

    return tables


def verify_sqlite_db(
    root: Path,
    database: Path,
) -> tuple[int, int]:
    """
    Verify table and row-count parity with master CSV files.

    Return the number of tables and total CSV rows verified.
    """

    root = root.resolve()
    database = database.expanduser().resolve()

    if not database.is_file():
        raise VerificationError(
            f"SQLite database does not exist: {database}"
        )

    master_dir = root / "data" / "master"
    csv_files = discover_csv_files(master_dir)

    expected_tables = {
        csv_file.stem.casefold(): csv_file
        for csv_file in csv_files
    }

    try:
        with closing(
            sqlite3.connect(database)
        ) as connection:
            integrity_row = connection.execute(
                "PRAGMA integrity_check"
            ).fetchone()

            integrity = (
                str(integrity_row[0])
                if integrity_row is not None
                else ""
            )

            if integrity != "ok":
                raise VerificationError(
                    "SQLite integrity check failed: "
                    f"{integrity or 'no result'}"
                )

            actual_tables = _database_tables(connection)

            missing_keys = sorted(
                set(expected_tables) - set(actual_tables)
            )
            unexpected_keys = sorted(
                set(actual_tables) - set(expected_tables)
            )

            problems: list[str] = []

            if missing_keys:
                missing = ", ".join(
                    expected_tables[key].stem
                    for key in missing_keys
                )
                problems.append(
                    f"missing SQLite tables: {missing}"
                )

            if unexpected_keys:
                unexpected = ", ".join(
                    actual_tables[key]
                    for key in unexpected_keys
                )
                problems.append(
                    f"unexpected SQLite tables: {unexpected}"
                )

            total_rows = 0

            shared_keys = sorted(
                set(expected_tables) & set(actual_tables)
            )

            for key in shared_keys:
                csv_file = expected_tables[key]
                table_name = actual_tables[key]

                _, csv_rows = read_csv(csv_file)
                csv_count = len(csv_rows)
                total_rows += csv_count

                sqlite_row = connection.execute(
                    "SELECT COUNT(*) FROM "
                    f"{quote_identifier(table_name)}"
                ).fetchone()

                sqlite_count = (
                    int(sqlite_row[0])
                    if sqlite_row is not None
                    else 0
                )

                if sqlite_count != csv_count:
                    problems.append(
                        f"table '{table_name}' row count mismatch: "
                        f"CSV={csv_count}, SQLite={sqlite_count}"
                    )

            if problems:
                raise VerificationError(
                    "SQLite parity verification failed:\n- "
                    + "\n- ".join(problems)
                )

    except sqlite3.Error as exc:
        raise VerificationError(
            f"cannot verify SQLite database: {exc}"
        ) from exc

    return len(expected_tables), total_rows


def parse_args(
    argv: Sequence[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that SQLite tables and row counts "
            "match DKB master CSV files."
        )
    )
    parser.add_argument(
        "database",
        type=Path,
        help="Path to the generated SQLite database.",
    )
    return parser.parse_args(argv)


def main(
    argv: Sequence[str] | None = None,
) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parent.parent

    try:
        table_count, row_count = verify_sqlite_db(
            root,
            args.database,
        )
    except (BuildError, VerificationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("SQLite verification: PASS")
    print(f"Tables verified: {table_count}")
    print(f"Rows verified: {row_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
