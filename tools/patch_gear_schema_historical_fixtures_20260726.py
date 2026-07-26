#!/usr/bin/env python3
"""Normalize historical fixtures and gear-aware compatibility contracts."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_required(path: Path, pattern: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.DOTALL)
    if count == 0:
        if replacement in text:
            return
        raise RuntimeError(f"anchor missing in {path}: {pattern!r}")
    path.write_text(updated, encoding="utf-8")


def replace_text(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old in text:
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
    elif new not in text:
        raise RuntimeError(f"anchor missing in {path}: {old!r}")


comparison = ROOT / "tests" / "test_configuration_comparison.py"
comparison_rows = {
    "a_power_old": ("1", "cfg_a", "engine_power", "90", "2026-01-01", "src_a"),
    "a_power": ("2", "cfg_a", "engine_power", "100", "2026-06-01", "src_a"),
    "b_power": ("3", "cfg_b", "engine_power", "100", "2026-06-01", "src_b"),
    "a_torque": ("4", "cfg_a", "engine_torque", "180", "2026-06-01", "src_a"),
}
for code, (identifier, configuration, attribute, value, date, source) in comparison_rows.items():
    canonical = f'''                [
                    "{identifier}",
                    "{code}",
                    "{configuration}",
                    "{attribute}",
                    "",
                    "",
                    "{value}",
                    "{date}",
                    "{source}",
                    "",
                ],'''
    pattern = rf'''                \[
                    "{identifier}",
                    "{code}",
                    "{configuration}",
                    "{attribute}",
.*?                \],'''
    replace_required(comparison, pattern, canonical)

shortlist = ROOT / "tests" / "test_configuration_shortlist.py"
shortlist_rows = {
    "cfg_a_seats": '(1, "cfg_a_seats", "cfg_a", "number_of_seats", "", "", 5, "2026-01-01", "src_a", ""),',
    "cfg_b_seats": '(2, "cfg_b_seats", "cfg_b", "number_of_seats", "", "", 5, "2026-01-01", "src_b", ""),',
    "cfg_c_seats": '(3, "cfg_c_seats", "cfg_c", "number_of_seats", "", "", 7, "2026-01-01", "src_c", ""),',
    "cfg_a_power": '(4, "cfg_a_power", "cfg_a", "engine_power", "petrol", "", 90, "2026-01-01", "src_a", ""),',
}
for code, canonical in shortlist_rows.items():
    replace_required(shortlist, rf'\([^\n]*"{code}"[^\n]*\),', canonical)

validate = ROOT / "tests" / "test_validate_cli.py"
text = validate.read_text(encoding="utf-8")
old = '''            "5. Walidacja zakresów lat",
            "6. Walidacja statusów i cyklu życia",
            "7. Walidacja okresów dostępności powiązań",
            "8. Walidacja nakładających się okresów powiązań",
            "9. Walidacja kontraktu reguł danych",
            "10. Wykonywanie reguł danych",
            "11. Zbieranie statystyk",
            "12. Generowanie raportu",
'''
new = '''            "5. Walidacja kontekstu wybranego biegu",
            "6. Walidacja zakresów lat",
            "7. Walidacja statusów i cyklu życia",
            "8. Walidacja okresów dostępności powiązań",
            "9. Walidacja nakładających się okresów powiązań",
            "10. Walidacja kontraktu reguł danych",
            "11. Wykonywanie reguł danych",
            "12. Zbieranie statystyk",
            "13. Generowanie raportu",
'''
if old in text:
    text = text.replace(old, new)
elif new not in text:
    raise RuntimeError("validate CLI snapshot anchor missing")
needle = '''        self.assertIn(
            "- Year ranges: **PASS**",
            report,
        )
'''
addition = '''        self.assertIn(
            "- Selected-gear context: **PASS**",
            report,
        )
''' + needle
if addition not in text:
    if needle not in text:
        raise RuntimeError("validation report snapshot anchor missing")
    text = text.replace(needle, addition)
validate.write_text(text, encoding="utf-8")

# Cargo importers remain reproducible after the master schema gains gear_number.
duster = ROOT / "tools" / "import_duster_brochure_cargo_20260726.py"
replace_text(
    duster,
    '            "attribute_code": "boot_capacity", "fuel_type_code": "", "value": str(observation["value"]),',
    '            "attribute_code": "boot_capacity", "fuel_type_code": "", "gear_number": "", "value": str(observation["value"]),',
)

# A range conflicts only with a scalar lacking selected-gear context.
ranges = ROOT / "tools" / "import_configuration_value_ranges.py"
replace_text(
    ranges,
    '            row.get("fuel_type_code", ""),\n            row.get("observation_date", ""),',
    '            row.get("fuel_type_code", ""),\n            row.get("gear_number", ""),\n            row.get("observation_date", ""),',
)
replace_text(
    ranges,
    '        semantic = (row.configuration_code, spec.attribute_code, fuel, spec.observation_date)',
    '        semantic = (row.configuration_code, spec.attribute_code, fuel, "", spec.observation_date)',
)

# The scalar-range collision fixture must also carry an explicit empty gear.
range_test = ROOT / "tests" / "test_configuration_value_ranges.py"
replace_text(
    range_test,
    '            [["1", "scalar", "example_configuration", "fuel_consumption", "petrol", "5.9", "2026-04-01", "example_source", "source"]],',
    '            [["1", "scalar", "example_configuration", "fuel_consumption", "petrol", "", "5.9", "2026-04-01", "example_source", "source"]],',
)

print("PASS: historical selected-gear contracts normalized")
