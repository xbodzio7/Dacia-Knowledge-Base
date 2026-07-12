"""
Strict structural validation for Dacia Knowledge Base CSV files.
"""

from __future__ import annotations

import csv
from pathlib import Path


def validate_csv(path: Path) -> tuple[bool, list[str]]:
    """
    Validate one CSV file.

    The validator requires UTF-8, permits an optional UTF-8 BOM and checks:
    - presence and integrity of the header,
    - unique non-empty column names,
    - consistent row width,
    - absence of completely empty data rows,
    - valid CSV quoting.
    """

    if not path.is_file():
        return False, [f"File not found: {path}"]

    errors: list[str] = []

    try:
        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            reader = csv.reader(handle, strict=True)
            header = next(reader, None)

            if not header:
                return False, ["File is empty or has no header"]

            normalized_headers = [
                column.strip()
                for column in header
            ]

            first_positions: dict[str, int] = {}

            for position, column in enumerate(
                normalized_headers,
                start=1,
            ):
                if not column:
                    errors.append(
                        "Header: empty column name "
                        f"at position {position}"
                    )
                    continue

                normalized = column.casefold()

                if normalized in first_positions:
                    errors.append(
                        f"Header: duplicate column name '{column}' "
                        f"at position {position} "
                        f"(first seen at position "
                        f"{first_positions[normalized]})"
                    )
                    continue

                first_positions[normalized] = position

            expected_columns = len(header)

            for row in reader:
                line_number = reader.line_num

                if not row or all(
                    not value.strip()
                    for value in row
                ):
                    errors.append(
                        f"Line {line_number}: empty data row"
                    )
                    continue

                if len(row) != expected_columns:
                    errors.append(
                        f"Line {line_number}: expected "
                        f"{expected_columns} columns, "
                        f"got {len(row)}"
                    )

    except UnicodeDecodeError:
        return False, ["File is not valid UTF-8"]
    except csv.Error as exc:
        return False, [f"CSV parse error: {exc}"]
    except OSError as exc:
        return False, [f"Cannot read file: {exc}"]

    return not errors, errors
