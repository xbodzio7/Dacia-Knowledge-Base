"""
Repository structure validation.
"""

from pathlib import Path

REQUIRED_FILES = [
    "data/master/attributes.csv",
    "data/master/domains.csv",
    "data/master/units.csv",
    "data/master/value_types.csv",
    "data/master/validation_rules.csv",
]


def validate_repository(root: Path) -> tuple[bool, list[str]]:
    """
    Validate required repository structure.

    Returns:
        (success, missing_files)
    """
    missing = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            missing.append(relative_path)

    return len(missing) == 0, missing
