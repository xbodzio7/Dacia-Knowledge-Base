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


CSV_FILES = REQUIRED_FILES.copy()


def discover_csv_files(root: Path) -> list[str]:
    """
    Discover every CSV file stored in the repository.

    Returned paths are relative to repository root and sorted
    to keep validator output deterministic.
    """

    csv_files = []

    for path in root.rglob("*.csv"):
        if ".git" in path.parts:
            continue

        csv_files.append(path.relative_to(root).as_posix())

    return sorted(csv_files)
