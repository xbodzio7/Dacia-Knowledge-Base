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
from reporting.statistics import collect_statistics
from validators.duplicates import validate_duplicates
from validators.empty_dataset import validate_empty_dataset
from validators.required_fields import validate_required_fields
from reporting.markdown_report import write_validation_report
from reporting.json_report import write_statistics_json
from validators.references import validate_references


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

    # Repository structure
    repo_ok, missing = validate_repository(root)
    print("Repository structure")
    if repo_ok:
        print("  PASS")
    else:
        print("  FAIL")
        for item in missing:
            print(f"  Missing: {item}")

    # CSV integrity
    print()
    print("CSV integrity")

    csv_ok = True
    reference_errors = []

    for relative in discover_csv_files(root):
        csv_path = root / relative
        valid, errors = validate_csv(csv_path)

        duplicate_errors = validate_duplicates(csv_path)
        empty_errors = validate_empty_dataset(csv_path)
        required_errors = validate_required_fields(csv_path)

        if duplicate_errors:
            valid = False
            errors.extend(duplicate_errors)
        if empty_errors:
            valid = False
            errors.extend(empty_errors)
        if required_errors:
            valid = False
            errors.extend(required_errors)

        if valid:
            print(f"  PASS  {relative}")
        else:
            csv_ok = False
            print(f"  FAIL  {relative}")
            for error in errors:
                print(f"        {error}")

        # Reference validation (moved outside loop)
        reference_errors.extend(validate_references(root) or [])

    if reference_errors:
        csv_ok = False
        print()
        print("Reference validation")
        for error in reference_errors:
            print(f"  {error}")

    # Attribute validation
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

    # Statistics
    stats = collect_statistics(root)
    print()
    print("Repository statistics")
    print("---------------------")
    print(f"CSV files   : {stats.get('csv_files', 0)}")
    print(f"Rows        : {stats.get('rows', 0)}")
    print(f"Empty files : {stats.get('empty_files', 0)}")
    print()

    print("Largest datasets:")
    for name, rows in stats.get("datasets", [])[:10]:
        print(f"{name:<30} {rows:>8}")

    # Generate reports
    reports_dir = root / "reports"
    reports_dir.mkdir(exist_ok=True)

    write_validation_report(
        reports_dir / "validation_report.md",
        repository_ok=repo_ok,
        csv_ok=csv_ok,
        statistics=stats,
    )

    write_statistics_json(
        reports_dir / "statistics.json",
        stats,
    )

    print(f"\nValidation report written to {reports_dir}/validation_report.md")

    return 0 if repo_ok and csv_ok and attributes_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
