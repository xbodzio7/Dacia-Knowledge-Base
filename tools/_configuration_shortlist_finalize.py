from __future__ import annotations

import json
from pathlib import Path


def read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    Path(path).write_text(text, encoding="utf-8", newline="\n")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"missing {label} anchor")
    return text.replace(old, new, 1)


def insert_before(text: str, marker: str, addition: str, label: str) -> str:
    if marker not in text:
        raise RuntimeError(f"missing {label} marker")
    return text.replace(marker, addition + marker, 1)


def patch_unified_cli() -> None:
    path = "tools/dkb.py"
    text = read(path)
    if '"configuration-shortlist": (' not in text:
        marker = '    "configuration-comparison": (\n'
        block = '''    "configuration-shortlist": (
        "configuration_shortlist.py",
        "Filter active configurations into an evidence-aware shortlist.",
        "[--as-of YYYY-MM-DD] [--model CODE] [--version CODE] "
        "[--transmission TYPE] [--powertrain TEXT] "
        "[--min-price PLN] [--max-price PLN] [--seats N] "
        "[--require-equipment CODE] "
        "[--require-standard-equipment CODE] "
        "[--json FILE] [--markdown FILE] [--csv FILE]",
    ),
'''
        text = insert_before(text, marker, block, "shortlist command")
    if "configuration-shortlist --transmission automatic" not in text:
        marker = '''    print(
        "  python tools/dkb.py configuration-comparison "
'''
        example = '''    print(
        "  python tools/dkb.py configuration-shortlist --transmission automatic "
        "--max-price 100000 --csv ../configuration-shortlist.csv"
    )
'''
        text = insert_before(text, marker, example, "shortlist example")
    if '"configuration-shortlist": (' not in text:
        raise RuntimeError("shortlist command registration failed")
    write(path, text)


def patch_readme() -> None:
    path = "README.md"
    text = read(path)
    heading = "### Shortlista konfiguracji\n"
    if heading not in text:
        marker = "### Porównanie konfiguracji\n"
        section = '''### Shortlista konfiguracji

Komenda `configuration-shortlist` filtruje wszystkie aktywne konfiguracje na
podstawie jawnych kryteriów użytkowych, zachowując daty i źródła ceny, liczby
miejsc oraz wymaganego wyposażenia. Wyniki są uporządkowane według ceny
katalogowej, modelu, wersji i kodu konfiguracji.

```bash
python tools/dkb.py configuration-shortlist \\
  --transmission automatic \\
  --max-price 100000 \\
  --require-equipment rear_view_camera \\
  --json ../configuration-shortlist.json \\
  --markdown ../configuration-shortlist.md \\
  --csv ../configuration-shortlist.csv
```

Dostępne kryteria obejmują dokładne kody modelu i wersji, typ skrzyni,
fragment nazwy napędu, minimalną i maksymalną cenę katalogową brutto w PLN,
liczbę miejsc oraz dwa poziomy wymagań wyposażenia. Powtarzane wartości
modelu, wersji, skrzyni i napędu są łączone przez OR, a różne wymiary filtrów
i wymagania wyposażenia przez AND.

`--require-equipment` akceptuje status `standard` albo `optional`, natomiast
`--require-standard-equipment` wyłącznie `standard`. Brak źródłowego
stwierdzenia nie spełnia kryterium i jest raportowany osobno od
`not_available`. Analogicznie brak ceny lub liczby miejsc pozostaje jawną
niewiadomą, a nie wartością domyślną.

JSON zawiera pełne filtry, niełączne statystyki przyczyn wykluczeń i liczniki
niewiadomych. Markdown dostarcza czytelną shortlistę, a CSV jeden płaski wiersz
na dopasowaną konfigurację z proweniencją ceny, miejsc i wyposażenia.

'''
        text = insert_before(text, marker, section, "README shortlist section")
    if "* filtrowanie i tworzenie shortlist konfiguracji," not in text:
        marker = "* interaktywne i eksportowalne porównania konfiguracji,\n"
        text = replace_once(
            text,
            marker,
            marker + "* filtrowanie i tworzenie shortlist konfiguracji,\n",
            "README project status",
        )
    required = (
        "### Shortlista konfiguracji",
        "--require-standard-equipment",
        "configuration-shortlist.json",
        "filtrowanie i tworzenie shortlist konfiguracji",
    )
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError(f"README shortlist markers missing: {missing}")
    write(path, text)


def patch_changelog() -> None:
    path = "CHANGELOG.md"
    text = read(path)
    bullet = (
        "* Evidence-aware configuration shortlist CLI with model, version, "
        "powertrain, transmission, price, seat and equipment filters.\n"
    )
    if bullet not in text:
        text = replace_once(
            text,
            "### Added\n\n",
            "### Added\n\n"
            + bullet
            + "* Deterministic JSON, Markdown and CSV shortlist artifacts with explicit unknown and exclusion reporting.\n",
            "changelog Added",
        )
    write(path, text)


def patch_roadmap() -> None:
    path = "project/ROADMAP.md"
    text = read(path)
    completed = (
        "- deterministyczna shortlista konfiguracji z filtrami ceny, napędu, "
        "skrzyni, miejsc i wyposażenia,\n"
    )
    if completed not in text:
        marker = (
            "- samodzielny interaktywny HTML porównań z filtrowaniem i "
            "proweniencją,\n"
        )
        text = replace_once(
            text,
            marker,
            marker + completed,
            "roadmap completed shortlist",
        )
    if "- interaktywna przeglądarkowa shortlista konfiguracji," not in text:
        marker = "## Reporting\n\n"
        text = replace_once(
            text,
            marker,
            marker + "- interaktywna przeglądarkowa shortlista konfiguracji,\n",
            "roadmap shortlist backlog",
        )
    write(path, text)


def patch_state() -> None:
    path = Path("project/state.json")
    state = json.loads(path.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-19"
    state["phase"] = "Data Product Utilization"
    state["reference_delivery"] = {
        "name": "Configuration Discovery and Shortlist Planning Review",
        "pull_request": 144,
        "head_sha": "8fa744b00f2c1a5e5cab12f1bb79b8166d94980c",
        "quality_run": 713,
    }
    state["baseline"]["tests"] = 603
    state["current_package"] = {
        "name": "Configuration Shortlist CLI",
        "status": "active",
        "goal": "Filter active configurations by metadata, current catalogue price, seat count and evidence-aware equipment requirements, with deterministic JSON, Markdown and CSV outputs.",
    }
    state["next_package"] = {
        "name": "Interactive Configuration Shortlist HTML Planning Review",
        "status": "planned",
        "goal": "Select a browser-ready shortlist experience that reuses the transparent CLI contract without adding preference scoring or inferred values.",
    }
    path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def patch_baseline_assertions() -> None:
    for path_string in (
        "tests/test_jogger_payload_performance_ranges.py",
        "tests/test_jogger_wltp_efficiency_ranges.py",
    ):
        path = Path(path_string)
        text = path.read_text(encoding="utf-8")
        old = 'self.assertEqual(baseline["tests"], 593)'
        new = 'self.assertEqual(baseline["tests"], 603)'
        if old not in text and new not in text:
            raise RuntimeError(f"baseline assertion missing in {path}")
        path.write_text(
            text.replace(old, new, 1),
            encoding="utf-8",
            newline="\n",
        )


def main() -> None:
    patch_unified_cli()
    patch_readme()
    patch_changelog()
    patch_roadmap()
    patch_state()
    patch_baseline_assertions()


if __name__ == "__main__":
    main()
