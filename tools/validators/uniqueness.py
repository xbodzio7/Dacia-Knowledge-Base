"""
Validation of unique and required fields in attributes.csv.
"""

from __future__ import annotations

import csv
from pathlib import Path


def validate_attributes(path: Path) -> tuple[bool, list[str]]:
    """
    Validate attributes.csv.

    Checks:
    - id is present
    - id is unique
    - code is present
    - code is unique
    """

    errors: list[str] = []

    ids: set[str] = set()
    codes: set[str] = set()

    with path.open("r", encoding="utf-8-sig", newline="") as file:

        reader = csv.DictReader(file)

        for line_number, row in enumerate(reader, start=2):

            attribute_id = row.get("id", "").strip()
            code = row.get("code", "").strip()

            #
            # id
            #

            if not attribute_id:
                errors.append(f"Line {line_number}: missing id")

            elif attribute_id in ids:
                errors.append(
                    f"Line {line_number}: duplicate id '{attribute_id}'"
                )

            else:
                ids.add(attribute_id)

            #
            # code
            #

            if not code:
                errors.append(f"Line {line_number}: missing code")

            elif code in codes:
                errors.append(
                    f"Line {line_number}: duplicate code '{code}'"
                )

            else:
                codes.add(code)

    return len(errors) == 0, errors
