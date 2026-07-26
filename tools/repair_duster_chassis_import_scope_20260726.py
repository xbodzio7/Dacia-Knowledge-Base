#!/usr/bin/env python3
"""Restrict the unmodeled hybrid-G 150 guard to Duster configurations."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools" / "import_duster_chassis_20260726.py"
OLD = '''            row.get("status") == "active"
            and row.get("powertrain_label") == "hybrid-G 150 4x4"
'''
NEW = '''            row.get("status") == "active"
            and row.get("code", "").startswith("duster_")
            and row.get("powertrain_label") == "hybrid-G 150 4x4"
'''


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    if NEW in text:
        print("PASS: Duster hybrid-G exclusion already scoped")
        return 0
    if OLD not in text:
        raise RuntimeError("expected unscoped hybrid-G guard not found")
    PATH.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print("PASS: Duster hybrid-G exclusion scoped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
