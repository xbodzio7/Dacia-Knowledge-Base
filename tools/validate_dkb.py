#!/usr/bin/env python3

"""
DKB Validator

Entry point for validating the Dacia Knowledge Base repository.
"""

from pathlib import Path
import platform

from validators.csv_validator import validate_csv
from validators.repository import (
    discover_csv_files,
    validate_repository,
)
from validators.uniqueness import validate_attributes


def repository_root() -> Path:
    """Return repository root directory."""
    return Path(__file__).resolve().parent.parent


def print_header(root: Path) -> None:
    """Print validator header."""
    print("=" * 60)
    print("DKB Validator v0.1")
    print("=" * 60)
    print(f"Repository : {root}")
    print(f"Python     : {platform.python_version()}")
    print()


def main() -> int:
    """Program entry point."""

    root = repository_root()

    print_header(root)

    #
    # Repository structure
    #

    repo_ok, missing = validate_repository(root)

    print("Repository structure")

    if repo_ok:
        print("  PASS")
    else:
        print("  FAIL")

        for item in missing:
            print(f"  Missing: {item}")

    #
    # CSV integrity
    #

    print()
    print("CSV integrity")

    csv_ok = True

    for relative in discover_csv_files(root):

        valid, errors = validate_csv(root / relative)

        if valid:
            print(f"  PASS  {relative}")
        else:
            csv_ok = False
            print(f"  FAIL  {relative}")

            for error in errors:
                print(f"        {error}")

    #
    # Attribute validation
    #

    print()
    print("Attributes")

    attributes_ok, errors = validate_attributes(
        root / "data/master/attributes.csv"
    )

    if attributes_ok:
        print("  PASS")
    else:
        print("  FAIL")

        for error in errors:
            print(f"        {error}")

    return 0 if repo_ok and csv_ok and attributes_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
