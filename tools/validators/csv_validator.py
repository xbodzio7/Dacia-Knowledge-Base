"""
CSV integrity validation.
"""

from __future__ import annotations

import csv
from pathlib import Path


def validate_csv(path: Path) -> tuple[bool, list[str]]:
    """
    Validate a CSV file.

    Checks:
    - file can be opened
    - header exists
    - every non-empty row has the same number of columns

    Returns:
        (success, errors)
    """

    errors: list[str] = []

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.reader(file)

            header = next(reader, None)

            if not header:
                return False, ["Missing CSV header"]

            expected_columns = len(header)

            for line_number, row in enumerate(reader, start=2):

                # Ignore completely empty lines
                if not row:
                    continue

                # Ignore rows containing only whitespace
                if all(cell.strip() == "" for cell in row):
                    continue

                if len(row) != expected_columns:
                    errors.append(
                        f"Line {line_number}: expected "
                        f"{expected_columns} columns, found {len(row)}"
                    )

    except Exception as exc:
        return False, [str(exc)]

    return len(errors) == 0, errors
