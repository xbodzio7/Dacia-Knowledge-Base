#!/usr/bin/env python3

"""
DKB Validator

Entry point for validating the Dacia Knowledge Base repository.
"""

from pathlib import Path
import platform

from validators.repository import validate_repository


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def print_header(root: Path) -> None:
    print("=" * 60)
    print("DKB Validator v0.1")
    print("=" * 60)
    print(f"Repository : {root}")
    print(f"Python     : {platform.python_version()}")
    print()


def main() -> int:
    root = repository_root()

    print_header(root)

    ok, missing = validate_repository(root)

    print("Repository structure")

    if ok:
        print("  PASS")
        return 0

    print("  FAIL")
    print()

    for item in missing:
        print(f"  Missing: {item}")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
