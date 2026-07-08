"""
Cross-reference validation between CSV files.
"""

from pathlib import Path
import csv
from typing import Set


def validate_references(root: Path) -> list[str]:
    """Validate references between tables (basic version)."""
    errors = []

    # Example: Check if attributes referenced in other files exist
    attributes_file = root / "data/master/attributes.csv"
    if not attributes_file.exists():
        return ["attributes.csv not found"]

    try:
        # Load all attribute codes
        valid_codes: Set[str] = set()
        with attributes_file.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = row.get("code", "").strip()
                if code:
                    valid_codes.add(code)

        # TODO: W przyszłości dodamy sprawdzanie referencji w attribute_values.csv itp.
        # Na razie zostawiamy placeholder

    except Exception as e:
        errors.append(f"Error during reference validation: {e}")

    return errors
