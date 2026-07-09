"""
CSV integrity validation with better encoding support.
"""

from __future__ import annotations

import csv
from pathlib import Path


def validate_csv(path: Path) -> tuple[bool, list[str]]:
    """
    Validate a single CSV file with robust encoding.
    """
    errors: list[str] = []

    try:
        # Próbujemy różnych encodingów
        for encoding in ["utf-8-sig", "utf-8", "windows-1250", "cp1250"]:
            try:
                with path.open("r", encoding=encoding, newline="") as file:
                    reader = csv.reader(file)
                    header = next(reader, None)

                    if not header:
                        return False, ["Plik jest pusty lub nie ma nagłówka"]

                    expected = len(header)

                    for line_no, row in enumerate(reader, start=2):
                        if not row or all(x.strip() == "" for x in row):
                            continue
                        if len(row) != expected:
                            errors.append(
                                f"Line {line_no}: expected {expected} columns, got {len(row)}"
                            )
                break  # jeśli się udało - wychodzimy

            except UnicodeDecodeError:
                continue
        else:
            return False, ["Nie udało się odczytać pliku z żadnym encodingiem"]

    except Exception as e:
        return False, [f"Unexpected error: {e}"]

    return len(errors) == 0, errors
