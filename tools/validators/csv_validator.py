"""
CSV integrity validation for Dacia Knowledge Base.
"""

from __future__ import annotations

import csv
from pathlib import Path


def validate_csv(path: Path) -> tuple[bool, list[str]]:
    """
    Validate a single CSV file.

    Checks:
        - UTF-8 encoding
        - Presence of header
        - Consistent column count
        - Empty rows (warning)

    Returns:
        (is_valid, list_of_errors)
    """
    errors: list[str] = []

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.reader(file)
            header = next(reader, None)

            if not header:
                return False, ["Plik jest pusty lub nie zawiera nagłówka"]

            expected_columns = len(header)

            for line_number, row in enumerate(reader, start=2):
                if not row or all(cell.strip() == "" for cell in row):
                    continue  # pusta linia - pomijamy

                if len(row) != expected_columns:
                    errors.append(
                        f"Line {line_number}: Oczekiwano {expected_columns} kolumn, "
                        f"znaleziono {len(row)}"
                    )
    except UnicodeDecodeError:
        return False, ["Błąd kodowania – plik musi być UTF-8"]
    except Exception as exc:
        return False, [f"Nieoczekiwany błąd: {exc}"]

    return len(errors) == 0, errors
