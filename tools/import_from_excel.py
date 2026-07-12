#!/usr/bin/env python3
"""
Narzędzie do importu danych z Excela do struktury CSV Dacia Knowledge Base
"""

from pathlib import Path
import pandas as pd
import sys
from typing import Optional


def import_excel_to_csv(excel_path: Path, output_dir: Optional[Path] = None):
    """Import data from Excel to CSV structure."""
    if not excel_path.exists():
        print(f"❌ Plik nie istnieje: {excel_path}")
        return False

    if output_dir is None:
        output_dir = excel_path.parent / "imported_csv"
    
    output_dir.mkdir(exist_ok=True)
    print(f"Importuję z: {excel_path}")
    print(f"Zapisuję do: {output_dir}\n")

    try:
        # Wczytaj wszystkie arkusze
        excel_file = pd.ExcelFile(excel_path)
        
        for sheet_name in excel_file.sheet_names:
            print(f"Przetwarzam arkusz: {sheet_name}")
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            # Wyczyść nazwy kolumn
            df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
            
            output_file = output_dir / f"{sheet_name.lower().replace(' ', '_')}.csv"
            df.to_csv(output_file, index=False, encoding="utf-8-sig")
            print(f"   → Zapisano {len(df)} wierszy do {output_file.name}")

        print("\n✅ Import zakończony pomyślnie!")
        return True

    except Exception as e:
        print(f"❌ Błąd podczas importu: {e}")
        return False


def main():
    if len(sys.argv) > 1:
        excel_file = Path(sys.argv[1])
    else:
        # Domyślny plik - zmień nazwę jeśli masz inny
        excel_file = Path("data/import/source_data.xlsx")
    
    import_excel_to_csv(excel_file)


if __name__ == "__main__":
    main()
