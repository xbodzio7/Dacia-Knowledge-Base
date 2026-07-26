#!/usr/bin/env python3
"""Update historical list-based fixtures after adding gear_number."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_all(path: Path, old: str, new: str, minimum: int = 1) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count == 0 and new in text:
        return
    if count < minimum:
        raise RuntimeError(f"fixture anchor missing in {path}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


comparison = ROOT / "tests" / "test_configuration_comparison.py"
for value in ("90", "100", "180"):
    replace_all(
        comparison,
        f'                    "",\n                    "{value}",\n                    "2026-',
        f'                    "",\n                    "",\n                    "{value}",\n                    "2026-',
    )

cargo = ROOT / "tests" / "test_brochure_cargo_context_reporting_foundation.py"
for value in ("500", "1500", "1400"):
    replace_all(
        cargo,
        f'"boot_capacity", "", "{value}", "2026-',
        f'"boot_capacity", "", "", "{value}", "2026-',
    )

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

print("PASS: historical selected-gear fixtures updated")
