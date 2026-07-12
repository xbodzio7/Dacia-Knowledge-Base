"""
Repository structure validation for Dacia Knowledge Base.
"""

from pathlib import Path

# Pliki master data, które powinny istnieć
REQUIRED_MASTER_FILES = [
    "data/master/attributes.csv",
    "data/master/categories.csv",
    "data/master/domains.csv",
    "data/master/units.csv",
    "data/master/value_types.csv",
]


def validate_repository(root: Path) -> tuple[bool, list[str]]:
    """Validate required repository structure."""
    missing = []

    for relative_path in REQUIRED_MASTER_FILES:
        if not (root / relative_path).exists():
            missing.append(relative_path)

    return len(missing) == 0, missing


def discover_csv_files(root: Path) -> list[str]:
    """
    Discover all CSV files in the repository (excluding .git).
    Returns relative paths sorted for deterministic output.
    """
    csv_files = []

    for path in root.rglob("*.csv"):
        if ".git" in path.parts:
            continue
        csv_files.append(path.relative_to(root).as_posix())

    return sorted(csv_files)
