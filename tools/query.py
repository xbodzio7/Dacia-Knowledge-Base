#!/usr/bin/env python3
"""
Narzędzie do zapytań SQL w bazie Dacia Knowledge Base
"""

from pathlib import Path
import sqlite3
import sys


def query_db(sql: str, params=None, fetchall=True):
    db_path = Path(__file__).parent.parent / "dacia_knowledge_base.db"
    
    if not db_path.exists():
        print("Baza nie istnieje. Najpierw uruchom build_sqlite.py")
        return None

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # żeby zwracało dict-like
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        
        if fetchall:
            results = cursor.fetchall()
            return [dict(row) for row in results]
        else:
            return cursor.fetchone()
    finally:
        conn.close()


def main():
    print("=== Dacia Knowledge Base Query Tool ===\n")
    
    while True:
        print("Dostępne komendy:")
        print("  1. Modele")
        print("  2. Silniki")
        print("  3. Wyszukaj atrybut")
        print("  q - wyjście\n")
        
        cmd = input("Wybierz: ").strip().lower()
        
        if cmd == "q":
            break
        elif cmd == "1":
            results = query_db("SELECT * FROM models LIMIT 20")
            for r in results:
                print(r)
        elif cmd == "2":
            results = query_db("SELECT * FROM engines")
            for r in results:
                print(r)
        elif cmd == "3":
            attr = input("Podaj kod atrybutu: ")
            results = query_db("SELECT * FROM attributes WHERE code = ?", (attr,))
            if results:
                print(results)
            else:
                print("Nie znaleziono")
        else:
            print("Nieznana komenda")


if __name__ == "__main__":
    main()
