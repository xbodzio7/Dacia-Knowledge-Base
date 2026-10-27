#!/usr/bin/env python3
"""
Build a local SQLite database from Dacia Knowledge Base master CSV files.

The generated database is a disposable build artifact. CSV files remain the
source of truth.
"""

from __future__ import annotations

import argparse
import csv
import os
import sqlite3
import sys
from pathlib import Path
from typing import Sequence


DEFAULT_DATABASE_NAME = "dacia_knowledge_base.db"


class BuildError(RuntimeError):
    """Raised when the SQLite database cannot be built safely."""


def quote_identifier(value: str) -> str:
    """Return a safely quoted SQLite identifier."""
    return f'"{value.replace(chr(34), chr(34) * 2)}"'


def read_csv(csv_file: Path) -> tuple[list[str], list[list[str]]]:
    """
    Read and validate one UTF-8 CSV file.

    utf-8-sig accepts regular UTF-8 and transparently removes an optional BOM.
    """
    try:
        with csv_file.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
    except UnicodeDecodeError as exc:
        raise BuildError(f"{csv_file}: file is not valid UTF-8") from exc
    except OSError as exc:
        raise BuildError(f"{csv_file}: cannot read file: {exc}") from exc

    if not rows:
        raise BuildError(f"{csv_file}: empty CSV file")

    headers = [header.strip() for header in rows[0]]

    if not headers or any(not header for header in headers):
        raise BuildError(f"{csv_file}: empty column name")

    normalized_headers = [header.casefold() for header in headers]

    if len(normalized_headers) != len(set(normalized_headers)):
        raise BuildError(f"{csv_file}: duplicate column name")

    expected_columns = len(headers)
    data_rows: list[list[str]] = []

    for row_number, row in enumerate(rows[1:], start=2):
        if len(row) != expected_columns:
            raise BuildError(
                f"{csv_file}:{row_number}: expected {expected_columns} "
                f"columns, found {len(row)}"
            )

        data_rows.append(row)

    return headers, data_rows


def discover_csv_files(master_dir: Path) -> list[Path]:
    """Return master CSV files and reject ambiguous table names."""
    if not master_dir.is_dir():
        raise BuildError(f"master data directory does not exist: {master_dir}")

    csv_files = sorted(master_dir.rglob("*.csv"))

    if not csv_files:
        raise BuildError(f"no CSV files found in {master_dir}")

    table_sources: dict[str, Path] = {}

    for csv_file in csv_files:
        table_name = csv_file.stem.casefold()

        if table_name in table_sources:
            raise BuildError(
                "duplicate SQLite table name "
                f"'{csv_file.stem}' from {table_sources[table_name]} "
                f"and {csv_file}"
            )

        table_sources[table_name] = csv_file

    return csv_files


def import_table(
    connection: sqlite3.Connection,
    csv_file: Path,
) -> int:
    """Create one SQLite table and return the imported row count."""
    headers, rows = read_csv(csv_file)
    table_name = csv_file.stem

    quoted_table = quote_identifier(table_name)
    columns = ", ".join(
        f"{quote_identifier(header)} TEXT"
        for header in headers
    )

    connection.execute(f"CREATE TABLE {quoted_table} ({columns})")

    if rows:
        placeholders = ", ".join("?" for _ in headers)
        connection.executemany(
            f"INSERT INTO {quoted_table} VALUES ({placeholders})",
            rows,
        )

    return len(rows)


def build_sqlite_db(
    root: Path,
    db_path: Path | None = None,
) -> Path:
    """
    Build the database in a temporary file and atomically replace the output.

    The existing database remains untouched when validation or import fails.
    """
    root = root.resolve()
    master_dir = root / "data" / "master"

    if db_path is None:
        db_path = root / DEFAULT_DATABASE_NAME
    else:
        db_path = db_path.expanduser().resolve()

    db_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = db_path.with_name(f"{db_path.name}.tmp")
    temporary_path.unlink(missing_ok=True)

    csv_files = discover_csv_files(master_dir)

    print(f"Building SQLite database: {db_path}")
    print(f"Source directory: {master_dir}")

    connection: sqlite3.Connection | None = None

    try:
        connection = sqlite3.connect(temporary_path)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("BEGIN")

        for csv_file in csv_files:
            row_count = import_table(connection, csv_file)
            relative_path = csv_file.relative_to(root)
            print(f"  {relative_path} -> {csv_file.stem}: {row_count} rows")

        connection.commit()
        connection.close()
        connection = None

        os.replace(temporary_path, db_path)

    except (BuildError, OSError, sqlite3.Error) as exc:
        if connection is not None:
            connection.rollback()
            connection.close()

        temporary_path.unlink(missing_ok=True)

        if isinstance(exc, BuildError):
            raise

        raise BuildError(f"database build failed: {exc}") from exc

    print(f"Database ready: {db_path}")
    return db_path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a local SQLite database from DKB master CSV files."
    )
    parser.add_argument(
        "--output",
        type=Path,
        help=(
            "Output database path. "
            f"Default: repository root/{DEFAULT_DATABASE_NAME}"
        ),
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parent.parent

    try:
        build_sqlite_db(root, args.output)
    except BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
