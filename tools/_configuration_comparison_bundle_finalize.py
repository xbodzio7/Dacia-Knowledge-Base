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
    if '"configuration-comparison-bundle": (' not in text:
        marker = '    "configuration-comparison": (\n'
        block = '''    "configuration-comparison-bundle": (
        "configuration_comparison_bundle.py",
        "Generate scope-safe comparison bundles from explicit selections.",
        "[--configuration-code CODE] [--shortlist-json FILE] "
        "--output-directory DIR",
    ),
'''
        text = insert_before(text, marker, block, "bundle command")
    if "configuration-comparison-bundle --shortlist-json" not in text:
        marker = '''    print(
        "  python tools/dkb.py configuration-comparison "
        "--difference-context fuel_type_code=lpg "
'''
        example = '''    print(
        "  python tools/dkb.py configuration-comparison-bundle "
        "--shortlist-json ../configuration-shortlist.json "
        "--output-directory ../comparison-bundle"
    )
'''
        text = insert_before(text, marker, example, "bundle example")
    if '"configuration-comparison-bundle": (' not in text:
        raise RuntimeError("bundle command registration failed")
    write(path, text)


def patch_readme() -> None:
    path = "README.md"
    text = read(path)
    heading = "### Pakiet porównań z shortlisty\n"
    if heading not in text:
        marker = "### Porównanie konfiguracji\n"
        section = '''### Pakiet porównań z shortlisty

Komenda `configuration-comparison-bundle` łączy jawnie wybrane konfiguracje z
istniejącymi, jednorodnymi zakresami raportowymi. Przyjmuje powtarzalne kody
konfiguracji oraz raporty JSON wygenerowane przez `configuration-shortlist`.
Ich suma jest deterministycznie deduplikowana.

```bash
python tools/dkb.py configuration-comparison-bundle \\
  --shortlist-json ../configuration-shortlist.json \\
  --configuration-code duster_iii_expression_ecog100_4x2_manual \\
  --output-directory ../comparison-bundle
```

Wybrane konfiguracje są grupowane według 13 bieżących specyfikacji
kompletności. Grupy zawierające co najmniej dwie konfiguracje generują
istniejące raporty JSON, Markdown, CSV różnic i interaktywny HTML. Grupy
jednoelementowe są zapisane jako singletony bez sztucznego porównania.
Konfiguracje z różnych zakresów nigdy nie tworzą wspólnej pary.

Dla każdej porównywalnej grupy filtrowane są zarówno wpisy konfiguracji w
specyfikacji kompletności, jak i decyzje w specyfikacji dowodowej. Mianowniki,
algorytm par i klasyfikacje dowodowe pozostają bez zmian, a istniejący silnik
porównawczy wykonuje raporty bez osłabienia walidacji.

Publikacja katalogu jest transakcyjna. Niepusty katalog wyjściowy nie jest
nadpisywany, a błąd wejścia lub raportowania nie pozostawia częściowego
pakietu. `comparison-bundle-manifest.json` zawiera wybór, grupy, singletony,
liczby par i różnic oraz ścieżki, rozmiary i SHA-256 wszystkich raportów. Pole
`cross_scope_pairs_generated` zawsze ma wartość `false`.

'''
        text = insert_before(text, marker, section, "README bundle section")
    if "* transakcyjne pakiety porównań z jawnych wyborów shortlisty," not in text:
        marker = "* filtrowanie i tworzenie shortlist konfiguracji,\n"
        text = replace_once(
            text,
            marker,
            marker
            + "* transakcyjne pakiety porównań z jawnych wyborów shortlisty,\n",
            "README project status",
        )
    required = (
        "### Pakiet porównań z shortlisty",
        "configuration-comparison-bundle",
        "cross_scope_pairs_generated",
        "transakcyjne pakiety porównań",
    )
    missing = [value for value in required if value not in text]
    if missing:
        raise RuntimeError(f"README bundle markers missing: {missing}")
    write(path, text)


def patch_changelog() -> None:
    path = "CHANGELOG.md"
    text = read(path)
    bullet = (
        "* Transactional configuration comparison bundles that group explicit "
        "selections by independent reporting scope.\n"
    )
    if bullet not in text:
        text = replace_once(
            text,
            "### Added\n\n",
            "### Added\n\n"
            + bullet
            + "* Evidence-filtered JSON, Markdown, CSV and HTML bundle reports with singleton groups and SHA-256 manifests.\n",
            "changelog Added",
        )
    write(path, text)


def patch_roadmap() -> None:
    path = "project/ROADMAP.md"
    text = read(path)
    completed = (
        "- transakcyjny pakiet porównań z shortlisty z grupowaniem według "
        "jednorodnych zakresów i manifestem SHA-256,\n"
    )
    if completed not in text:
        marker = (
            "- interaktywna przeglądarkowa shortlista konfiguracji z pełnym "
            "snapshotem i testami parytetu semantyki,\n"
        )
        text = replace_once(
            text,
            marker,
            marker + completed,
            "roadmap completed bundle",
        )
    text = text.replace(
        "- przepływ shortlisty do porównania wybranych konfiguracji,\n",
        "- przeglądarkowy eksport jawnie wybranych konfiguracji do pakietu porównań,\n",
        1,
    )
    write(path, text)


def patch_state() -> None:
    path = Path("project/state.json")
    state = json.loads(path.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-19"
    state["phase"] = "Data Product Utilization"
    state["reference_delivery"] = {
        "name": "Shortlist-to-Comparison Workflow Planning Review",
        "pull_request": 148,
        "head_sha": "b55b09f8e27108a242fca10a4be46b92533f1c6f",
        "quality_run": 737,
    }
    state["baseline"]["tests"] = 620
    state["current_package"] = {
        "name": "Configuration Comparison Bundle CLI",
        "status": "active",
        "goal": "Group explicit selections by independent scope, filter completeness and evidence contracts, and publish transactional JSON, Markdown, CSV and HTML comparison bundles with singleton and checksum manifests.",
    }
    state["next_package"] = {
        "name": "Interactive Selection Export Planning Review",
        "status": "planned",
        "goal": "Select a browser workflow for explicitly selecting shortlist results and exporting codes or shortlist JSON consumable by the comparison bundle without ranking or inferred values.",
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
        old = 'self.assertEqual(baseline["tests"], 610)'
        new = 'self.assertEqual(baseline["tests"], 620)'
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
