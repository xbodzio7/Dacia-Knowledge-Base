#!/usr/bin/env python3
"""Allow empty optional dimensions in completeness semantic keys."""

from pathlib import Path


path = Path(__file__).resolve().parent / "_configuration_completeness_base.py"
text = path.read_text(encoding="utf-8")
old = "            if not item and field != 'fuel_type_code':\n"
new = "            if not item and field not in {'fuel_type_code', '_cargo_context_signature'}:\n"
if new not in text:
    if old not in text:
        raise RuntimeError("optional key validation anchor missing")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("PASS: optional cargo-context signature accepted")
