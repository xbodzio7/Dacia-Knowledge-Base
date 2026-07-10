#!/usr/bin/env python3
"""
Advanced validator for Dacia Knowledge Base.
"""

from __future__ import annotations

import platform
from pathlib import Path

from reporting.markdown_report import write_validation_report
from reporting.statistics import collect_statistics
from validators.csv_validator import validate_csv
from validators.references import REFERENCE_RULES, validate_references
from validators.repository import discover_csv_files, validate_repository
from validators.uniqueness import validate_unique_keys
from validators.year_ranges import (
    YEAR_RANGE_RULES,
    validate_year_ranges,
)


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def print_header(root: Path) -> None:
    print("=" * 70)
    print("DKB Validator v0.5")
    print("=" * 70)
    print(f"Repository : {root}")
    print(f"Python     : {platform.python_version()}")
    print()


def main() -> int:
    root = repository_root()
    print_header(root)

    print("1. Sprawdzanie struktury repozytorium")
    repository_ok, missing = validate_repository(root)

    if repository_ok:
        print("   ✅ OK")
    else:
        print("   ❌ Brakujące pliki:")
        for relative_path in missing:
            print(f"      - {relative_path}")

    print("\n2. Walidacja plików CSV")
    csv_ok = True

    for relative_path in discover_csv_files(root):
        csv_path = root / relative_path
        valid, errors = validate_csv(csv_path)

        if valid:
            print(f"   ✅ {relative_path}")
            continue

        csv_ok = False
        print(f"   ❌ {relative_path}")

        for error in errors[:5]:
            print(f"      • {error}")

        if len(errors) > 5:
            print(f"      ... i {len(errors) - 5} więcej")

    print("\n3. Walidacja unikalności kluczy")
    unique_key_count, uniqueness_errors = validate_unique_keys(root)
    uniqueness_ok = not uniqueness_errors

    if uniqueness_ok:
        print(
            "   ✅ OK "
            f"({unique_key_count} kolumn kluczowych)"
        )
    else:
        print(
            "   ❌ Wykryto "
            f"{len(uniqueness_errors)} problemów:"
        )

        for error in uniqueness_errors:
            print(f"      • {error}")

    print("\n4. Walidacja relacji między tabelami")
    reference_errors = validate_references(root)
    references_ok = not reference_errors

    if references_ok:
        print(f"   ✅ OK ({len(REFERENCE_RULES)} relacji)")
    else:
        print(f"   ❌ Wykryto {len(reference_errors)} problemów:")

        for error in reference_errors:
            print(f"      • {error}")

    print("\n5. Walidacja zakresów lat")
    checked_year_records, year_range_errors = validate_year_ranges(root)
    year_ranges_ok = not year_range_errors

    if year_ranges_ok:
        print(
            "   ✅ OK "
            f"({checked_year_records} rekordów, "
            f"{len(YEAR_RANGE_RULES)} reguły)"
        )
    else:
        print(
            "   ❌ Wykryto "
            f"{len(year_range_errors)} problemów:"
        )

        for error in year_range_errors:
            print(f"      • {error}")

    print("\n6. Zbieranie statystyk")
    statistics = collect_statistics(root)

    print(f"   Plików CSV : {statistics['csv_files']}")
    print(f"   Wierszy    : {statistics['rows']}")

    print("\n7. Generowanie raportu")
    reports_dir = root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "validation_report.md"

    write_validation_report(
        report_path,
        repository_ok=repository_ok,
        csv_ok=csv_ok,
        uniqueness_ok=uniqueness_ok,
        uniqueness_errors=uniqueness_errors,
        references_ok=references_ok,
        reference_errors=reference_errors,
        year_ranges_ok=year_ranges_ok,
        year_range_errors=year_range_errors,
        statistics=statistics,
    )

    print(f"   ✅ Raport zapisany: {report_path}")

    validation_ok = (
        repository_ok
        and csv_ok
        and uniqueness_ok
        and references_ok
        and year_ranges_ok
    )

    return 0 if validation_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
