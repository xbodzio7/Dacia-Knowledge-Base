"""
CSV integrity validation.
"""

from __future__ import annotations

import csv
from pathlib import Path


def validate_csv(path: Path) -> tuple[bool, list[str]]:
    """
    Validate a CSV file.

    Returns:
        (success, errors)
    """
    errors: list[str] = []

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)

            header = next(reader, None)

            if not header:
                return False, ["Empty header"]

            expected_columns = len(header)

            for line_number, row in enumerate(reader, start=2):
                if len(row) != expected_columns:
                    errors.append(
                        f"Line {line_number}: expected {expected_columns} columns, found {len(row)}"
                    )

    except Exception as exc:
        return False, [str(exc)]

    return len(errors) == 0, errors
