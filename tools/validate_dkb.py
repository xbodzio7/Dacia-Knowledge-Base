
#!/usr/bin/env python3
"""
Zaawansowany Walidator Dacia Knowledge Base v0.2
"""

from pathlib import Path
import platform
from typing import Any

from validators.csv_validator import validate_csv
from validators.repository import validate_repository, discover_csv_files
from validators.uniqueness import validate_attributes
from reporting.statistics import collect_statistics
from reporting.markdown_report import write_validation_report


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def print_header(root: Path) -> None:
    print("=" * 70)
    print("DKB Validator v0.2 - Zaawansowana wersja")
    print("=" * 70)
    print(f"Repository : {root}")
    print(f"Python     : {platform.python_version()}")
    print()


def main() -> int:
    root = repository_root()
    print_header(root)

    exit_code = 0

    # 1. Struktura repo
    print("1. Sprawdzanie struktury repozytorium")
    repo_ok, missing = validate_repository(root)
    if repo_ok:
        print("   ✅ OK")
    else:
        print("   ❌ Brakujące pliki:")
        for m in missing:
            print(f"      - {m}")
        exit_code = 1

    # 2. Walidacja CSV
    print("\n2. Walidacja plików CSV")
    csv_ok = True
    for relative in discover_csv_files(root):
        csv_path = root / relative
        valid, errors = validate_csv(csv_path)

        if valid:
            print(f"   ✅ {relative}")
        else:
            csv_ok = False
            print(f"   ❌ {relative}")
            for err in errors[:5]:  # max 5 błędów na plik
                print(f"      • {err}")
            if len(errors) > 5:
                print(f"      ... i {len(errors)-5} więcej")

    # 3. Walidacja atrybutów
    print("\n3. Walidacja atrybutów (uniqueness)")
    try:
        attr_ok, attr_errors = validate_attributes(root / "data/master/attributes.csv")
        if attr_ok:
            print("   ✅ OK")
        else:
            print("   ❌ Problemy z atrybutami:")
            for err in attr_errors:
                print(f"      • {err}")
            csv_ok = False
    except Exception as e:
        print(f"   ❌ Błąd walidacji atrybutów: {e}")
        csv_ok = False

    # 4. Statystyki
    print("\n4. Zbieranie statystyk")
    stats = collect_statistics(root)

    print(f"   Plików CSV : {stats['csv_files']}")
    print(f"   Wierszy    : {stats['rows']}")

    # 5. Generowanie raportu
    reports_dir = root / "reports"
    reports_dir.mkdir(exist_ok=True)

    write_validation_report(
        reports_dir / "validation_report.md",
        repository_ok=repo_ok,
        csv_ok=csv_ok,
        statistics=stats,
    )

    print(f"\n✅ Raport zapisany: {reports_dir}/validation_report.md")

    return 0 if repo_ok and csv_ok else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
