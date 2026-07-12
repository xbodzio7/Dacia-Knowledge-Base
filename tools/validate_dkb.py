#!/usr/bin/env python3
"""
Advanced validator for Dacia Knowledge Base.
"""

from __future__ import annotations

import platform
from pathlib import Path

from reporting.markdown_report import write_validation_report
from reporting.statistics import collect_statistics
from validators.association_intervals import (
    ASSOCIATION_INTERVAL_RULES,
    validate_association_intervals,
)
from validators.association_ranges import (
    ASSOCIATION_RANGE_RULES,
    validate_association_ranges,
)
from validators.csv_validator import validate_csv
from validators.references import REFERENCE_RULES, validate_references
from validators.rule_contracts import validate_rule_contracts
from validators.rule_execution import execute_data_rules
from validators.repository import discover_csv_files, validate_repository
from validators.uniqueness import validate_unique_keys
from validators.statuses import STATUS_RULES, validate_statuses
from validators.year_ranges import (
    YEAR_RANGE_RULES,
    validate_year_ranges,
)


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def print_header(root: Path) -> None:
    print("=" * 70)
    print("DKB Validator v0.10")
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

    print("\n6. Walidacja statusów i cyklu życia")
    checked_status_records, status_errors = validate_statuses(root)
    statuses_ok = not status_errors

    if statuses_ok:
        print(
            "   ✅ OK "
            f"({checked_status_records} rekordów, "
            f"{len(STATUS_RULES)} reguł)"
        )
    else:
        print(
            "   ❌ Wykryto "
            f"{len(status_errors)} problemów:"
        )

        for error in status_errors:
            print(f"      • {error}")

    print("\n7. Walidacja okresów dostępności powiązań")
    checked_association_ranges, association_range_errors = (
        validate_association_ranges(root)
    )
    association_ranges_ok = not association_range_errors

    if association_ranges_ok:
        print(
            "   ✅ OK "
            f"({checked_association_ranges} kontroli, "
            f"{len(ASSOCIATION_RANGE_RULES)} reguły)"
        )
    else:
        print(
            "   ❌ Wykryto "
            f"{len(association_range_errors)} problemów:"
        )

        for error in association_range_errors:
            print(f"      • {error}")

    print("\n8. Walidacja nakładających się okresów powiązań")
    checked_association_intervals, association_interval_errors = (
        validate_association_intervals(root)
    )
    association_intervals_ok = not association_interval_errors

    if association_intervals_ok:
        print(
            "   ✅ OK "
            f"({checked_association_intervals} rekordów, "
            f"{len(ASSOCIATION_INTERVAL_RULES)} reguły)"
        )
    else:
        print(
            "   ❌ Wykryto "
            f"{len(association_interval_errors)} problemów:"
        )

        for error in association_interval_errors:
            print(f"      • {error}")

    print("\n9. Walidacja kontraktu reguł danych")
    checked_rule_contracts, rule_contract_errors = (
        validate_rule_contracts(root)
    )
    rule_contracts_ok = not rule_contract_errors

    if rule_contracts_ok:
        print(
            "   ✅ OK "
            f"({checked_rule_contracts} reguł)"
        )
    else:
        print(
            "   ❌ Wykryto "
            f"{len(rule_contract_errors)} problemów:"
        )

        for error in rule_contract_errors:
            print(f"      • {error}")

    print("\n10. Wykonywanie reguł danych")

    if rule_contracts_ok:
        (
            checked_data_rules,
            checked_data_records,
            data_rule_errors,
            data_rule_warnings,
        ) = execute_data_rules(root)
    else:
        checked_data_rules = 0
        checked_data_records = 0
        data_rule_errors = [
            "Rule execution skipped because "
            "the rule contract is invalid."
        ]
        data_rule_warnings = []

    data_rules_ok = not data_rule_errors

    if data_rule_errors:
        print(
            "   ❌ Wykryto "
            f"{len(data_rule_errors)} błędów i "
            f"{len(data_rule_warnings)} ostrzeżeń:"
        )

        for error in data_rule_errors:
            print(f"      • {error}")

        for warning in data_rule_warnings:
            print(f"      ⚠ {warning}")

    elif data_rule_warnings:
        print(
            "   ⚠️ OK "
            f"({checked_data_rules} reguł, "
            f"{checked_data_records} rekordów, "
            f"{len(data_rule_warnings)} ostrzeżeń)"
        )

        for warning in data_rule_warnings:
            print(f"      ⚠ {warning}")

    else:
        print(
            "   ✅ OK "
            f"({checked_data_rules} reguł, "
            f"{checked_data_records} rekordów)"
        )

    print("\n11. Zbieranie statystyk")
    statistics = collect_statistics(root)

    print(f"   Plików CSV : {statistics['csv_files']}")
    print(f"   Wierszy    : {statistics['rows']}")

    print("\n12. Generowanie raportu")
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
        statuses_ok=statuses_ok,
        status_errors=status_errors,
        association_ranges_ok=association_ranges_ok,
        association_range_errors=association_range_errors,
        association_intervals_ok=association_intervals_ok,
        association_interval_errors=association_interval_errors,
        rule_contracts_ok=rule_contracts_ok,
        rule_contract_errors=rule_contract_errors,
        data_rules_ok=data_rules_ok,
        data_rule_errors=data_rule_errors,
        data_rule_warnings=data_rule_warnings,
        statistics=statistics,
    )

    print(f"   ✅ Raport zapisany: {report_path}")

    validation_ok = (
        repository_ok
        and csv_ok
        and uniqueness_ok
        and references_ok
        and year_ranges_ok
        and statuses_ok
        and association_ranges_ok
        and association_intervals_ok
        and rule_contracts_ok
        and data_rules_ok
    )

    return 0 if validation_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
