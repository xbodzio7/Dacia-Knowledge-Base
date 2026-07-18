#!/usr/bin/env python3
"""Apply the deterministic README and changelog updates for Duster prices."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, path: Path) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected one match in {path}: {count} for {old!r}")
    return text.replace(old, new, 1)


readme_path = ROOT / "README.md"
readme = readme_path.read_text(encoding="utf-8")
bootstrap = (
    "Katalog Duster III obejmuje 5 aktywnych wersji i 24 źródłowo potwierdzone\n"
    "kombinacje wersji, napędu i skrzyni biegów z oficjalnego cennika Dacia\n"
    "Polska obowiązującego od 6 lutego 2026 r. Encje pozostają poza bieżącym\n"
    "podzbiorem raportowym Sandero do czasu osobnych, źródłowych importów cen,\n"
    "parametrów technicznych i wyposażenia.\n"
)
price_note = (
    "\nDla wszystkich 24 konfiguracji Duster zapisano również datowane ceny katalogowe\n"
    "brutto obowiązujące od 6 lutego 2026 r. Promocyjny rabat oraz korzyści finansowania\n"
    "nie są cenami katalogowymi i nie zostały zaimportowane.\n"
)
readme = replace_once(readme, bootstrap, bootstrap + price_note, readme_path)
readme = replace_once(
    readme,
    "Zweryfikowany model obejmuje 416 testów, 34 pliki CSV, 1440 rekordów",
    "Zweryfikowany model obejmuje 422 testów, 34 pliki CSV, 1464 rekordów",
    readme_path,
)
readme = replace_once(
    readme,
    "SQLite obejmuje 34 tabele i 1440 rekordów",
    "SQLite obejmuje 34 tabele i 1464 rekordów",
    readme_path,
)
readme_path.write_text(readme, encoding="utf-8")

changelog_path = ROOT / "CHANGELOG.md"
changelog = changelog_path.read_text(encoding="utf-8")
changelog = replace_once(
    changelog,
    "## Unreleased\n\n### Added\n\n",
    (
        "## Unreleased\n\n### Added\n\n"
        "* Duster III catalogue gross prices for all 24 source-supported configurations, "
        "dated 2026-02-06 and separated from promotional discount and financing claims.\n"
    ),
    changelog_path,
)
changelog = replace_once(
    changelog,
    "* The automated test suite now contains 416 tests.",
    "* The automated test suite now contains 422 tests.",
    changelog_path,
)
changelog = replace_once(
    changelog,
    "* The verified master-data baseline now contains 34 CSV files and 1440 rows.",
    "* The verified master-data baseline now contains 34 CSV files and 1464 rows.",
    changelog_path,
)
changelog = replace_once(
    changelog,
    "* SQLite verification now covers 34 tables and 1440 rows.",
    "* SQLite verification now covers 34 tables and 1464 rows.",
    changelog_path,
)
changelog_path.write_text(changelog, encoding="utf-8")
