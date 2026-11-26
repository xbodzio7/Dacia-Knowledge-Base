#!/usr/bin/env python3
"""
Prosty Walidator Dacia Knowledge Base - z obsługą encodingów
"""

from pathlib import Path
import csv
import sys


def read_csv_with_fallback(path: Path):
    """Próbuje odczytać CSV z różnymi encodingami."""
    encodings = ["utf-8-sig", "utf-8", "windows-1250", "cp1250"]
    
    for enc in encodings:
        try:
            with path.open("r", encoding=enc, newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)
            return rows, enc
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"Nie udało się odczytać pliku {path}")


def main():
    root = Path(__file__).parent.parent
    data_dir = root / "data"

    print("=== Dacia Knowledge Base Validator ===")
    print(f"Root: {root}\n")

    csv_files = list(data_dir.rglob("*.csv"))
    print(f"Znaleziono {len(csv_files)} plików CSV:\n")

    errors = 0
    for csv_file in sorted(csv_files):
        try:
            rows, used_encoding = read_csv_with_fallback(csv_file)
            header = rows[0] if rows else []
            
            status = "✅" if len(header) > 0 else "⚠️"
            print(f"{status} {csv_file.name:<25} - {len(header)} kolumn (encoding: {used_encoding})")
            
        except Exception as e:
            print(f"❌ {csv_file.name:<25} - błąd: {e}")
            errors += 1

    print(f"\nWalidacja zakończona. Błędy: {errors}")
    if errors == 0:
        print("✅ Wszystko wygląda dobrze!")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
