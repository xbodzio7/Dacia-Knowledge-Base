#!/usr/bin/env python3
"""
Dacia Knowledge Base

CSV validator v1

Checks:
- UTF-8 encoding
- empty files
- empty rows
- consistent number of columns
- header presence

Future versions:
- duplicate IDs
- foreign keys
- dictionary validation
- cross references
"""

from pathlib import Path
import csv
import sys


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

ERRORS = []


def error(msg):
    ERRORS.append(msg)


def validate_csv(path: Path):

    try:
        with open(path, encoding="utf-8", newline="") as f:

            reader = csv.reader(f)

            try:
                header = next(reader)
            except StopIteration:
                error(f"{path}: empty file")
                return

            if not header:
                error(f"{path}: missing header")
                return

            expected_columns = len(header)

            for line_no, row in enumerate(reader, start=2):

                if not row:
                    error(f"{path}:{line_no}: empty row")
                    continue

                if len(row) != expected_columns:
                    error(
                        f"{path}:{line_no}: "
                        f"expected {expected_columns} columns "
                        f"but found {len(row)}"
                    )

    except UnicodeDecodeError:
        error(f"{path}: invalid UTF-8")


def main():

    if not DATA_DIR.exists():
        print("No data directory.")
        return 1

    csv_files = sorted(DATA_DIR.rglob("*.csv"))

    if not csv_files:
        print("No CSV files found.")
        return 0

    for file in csv_files:
        validate_csv(file)

    if ERRORS:

        print("VALIDATION FAILED\n")

        for e in ERRORS:
            print("-", e)

        return 1

    print("Validation OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
