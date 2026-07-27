#!/usr/bin/env python3
"""Expand the catalogue price-list slice relationship scope to all 15 matrix configurations."""

from __future__ import annotations

from pathlib import Path

PATH = Path(__file__).resolve().parent / "import_sandero_stepway_catalog_completion.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '''    price_codes = [str(item["code"]) for item in CONFIGURATIONS]\n    price_codes.extend(code for code, _ in EXTRA_PRICE_OBSERVATIONS)\n    for configuration_code in price_codes:\n''',
        '''    for configuration_code in MATRIX_CONFIGURATIONS:\n''',
        "price-list relationship scope",
    )
    text = replace_once(
        text,
        '''            sorted(\n                {str(item["code"]) for item in CONFIGURATIONS}\n                | {code for code, _ in EXTRA_PRICE_OBSERVATIONS}\n            ),\n''',
        '''            list(MATRIX_CONFIGURATIONS),\n''',
        "price-list source slice selection",
    )
    text = replace_once(
        text,
        '            "source_configuration_relationships": 14,\n',
        '            "source_configuration_relationships": 21,\n',
        "relationship addition contract",
    )
    compile(text, str(PATH), "exec")
    PATH.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
