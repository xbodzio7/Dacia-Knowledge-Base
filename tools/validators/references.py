"""
Cross-reference validation between CSV files.
"""

from pathlib import Path
import csv
from typing import Set


def validate_references(root: Path) -> list[str]:
    """Validate references between tables."""
    errors: list[str] = []

    attributes_file = root / "data/master/attributes.csv"
    if not attributes_file.exists():
        return ["attributes.csv not found"]

    try:
        valid_codes: Set[str] = set()
        duplicate_codes: Set[str] = set()

        with attributes_file.open(
            encoding="utf-8-sig",
            newline="",
        ) as f:
            reader = csv.DictReader(f)

            for row_number, row in enumerate(reader, start=2):
                code = (row.get("code") or "").strip()

                if not code:
                    continue

                if code in valid_codes:
                    duplicate_codes.add(code)
                    errors.append(
                        f"{attributes_file}: row {row_number}: duplicate attribute code '{code}'"
                    )
                else:
                    valid_codes.add(code)

    except Exception as e:
        errors.append(f"Error during reference validation: {e}")

    return errors
