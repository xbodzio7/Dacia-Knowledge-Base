#!/usr/bin/env python3
"""
Buduje bazę SQLite z plików CSV Dacia Knowledge Base
"""

from pathlib import Path
import sqlite3
import csv
import sys


def build_sqlite_db(root: Path, db_path: Path = None):
    if db_path is None:
        db_path = root / "dacia_knowledge_base.db"

    print(f"Tworzę bazę SQLite: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    
    master_dir = root / "data" / "master"
    
    for csv_file in sorted(master_dir.rglob("*.csv")):
        table_name = csv_file.stem
        print(f"Importuję tabelę: {table_name}")
        
        # Obsługa encodingu
        encodings = ["utf-8-sig", "windows-1250", "cp1250", "utf-8"]
        rows = None
        used_encoding = None
        
        for enc in encodings:
            try:
                with csv_file.open("r", encoding=enc, newline="") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                used_encoding = enc
                break
            except UnicodeDecodeError:
                continue
        
        if rows is None:
            print(f"  ❌ Nie udało się odczytać {csv_file.name}")
            continue

        headers = rows[0]
        
        # Tworzymy tabelę
        columns = ", ".join([f'"{col}" TEXT' for col in headers])
        conn.execute(f"DROP TABLE IF EXISTS [{table_name}];")
        conn.execute(f"CREATE TABLE [{table_name}] ({columns});")
        
        # Wstawiamy dane
        placeholders = ", ".join(["?"] * len(headers))
        insert_sql = f"INSERT INTO [{table_name}] VALUES ({placeholders})"
        
        for row in rows[1:]:
            conn.execute(insert_sql, row)
        
        print(f"   → {len(rows)-1} wierszy (encoding: {used_encoding})")

    conn.commit()
    conn.close()
    
    print(f"\n✅ Baza SQLite gotowa!")
    return db_path


def main():
    root = Path(__file__).parent.parent
    build_sqlite_db(root)


if __name__ == "__main__":
    main()
