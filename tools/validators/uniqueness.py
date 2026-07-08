"""
Uniqueness and required fields validation.
"""

from __future__ import annotations

import csv
from pathlib import Path


def validate_attributes(path: Path) -> tuple[bool, list[str]]:
    """
    Validate attributes.csv for uniqueness of id and code.
    """
    if not path.exists():
        return False, [f"File not found: {path}"]

    errors: list[str] = []
    ids: set[str] = set()
    codes: set[str] = set()

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            for line_number, row in enumerate(reader, start=2):
                attr_id = row.get("id", "").strip()
                code = row.get("code", "").strip()

                if not attr_id:
                    errors.append(f"Line {line_number}: missing 'id'")
                elif attr_id in ids:
                    errors.append(f"Line {line_number}: duplicate id '{attr_id}'")
                else:
                    ids.add(attr_id)

                if not code:
                    errors.append(f"Line {line_number}: missing 'code'")
                elif code in codes:
                    errors.append(f"Line {line_number}: duplicate code '{code}'")
                else:
                    codes.add(code)

    except Exception as exc:
        return False, [f"Error reading attributes.csv: {exc}"]

    return len(errors) == 0, errors
