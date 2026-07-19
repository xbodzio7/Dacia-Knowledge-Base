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


def patch_readme() -> None:
    path = "README.md"
    text = read(path)
    paragraph = (
        "Każda karta w przeglądarce może zostać jawnie zaznaczona do porównania.\n"
        "Zaznaczenia pozostają aktywne przy zmianie filtrów, a akcja `Wybierz\n"
        "widoczne` dodaje bieżący wynik bez usuwania wcześniej ukrytych wyborów.\n"
        "Panel wyboru umożliwia pojedyncze usuwanie, wyczyszczenie całego zestawu\n"
        "oraz pobranie deterministycznego JSON-u zgodnego z\n"
        "`configuration-comparison-bundle` albo pliku TXT z jednym kodem na linię.\n"
        "Eksport nie zawiera znacznika czasu i zachowuje porządek katalogu.\n\n"
    )
    if paragraph not in text:
        marker = (
            "HTML osadza pełny aktywny snapshot dla wskazanej daty, a kryteria CLI\n"
            "ustawiają początkowy stan formularza. Wyczyszczenie filtrów przywraca cały\n"
            "katalog, podczas gdy JSON, Markdown i CSV pozostają wynikami filtrów\n"
            "wykonanych po stronie Pythona. Plik działa bez serwera i nie pobiera\n"
            "zewnętrznych skryptów, stylów ani fontów.\n\n"
        )
        text = replace_once(
            text,
            marker,
            marker + paragraph,
            "README selection export paragraph",
        )
    if "* jawny przeglądarkowy wybór i eksport konfiguracji do pakietu porównań," not in text:
        marker = "* transakcyjne pakiety porównań z jawnych wyborów shortlisty,\n"
        text = replace_once(
            text,
            marker,
            marker
            + "* jawny przeglądarkowy wybór i eksport konfiguracji do pakietu porównań,\n",
            "README product status",
        )
    required = (
        "Wybierz widoczne",
        "configuration-comparison-bundle",
        "pliku TXT z jednym kodem na linię",
        "jawny przeglądarkowy wybór",
    )
    missing = [value for value in required if value not in text]
    if missing:
        raise RuntimeError(f"README selection markers missing: {missing}")
    write(path, text)


def patch_changelog() -> None:
    path = "CHANGELOG.md"
    text = read(path)
    bullet = (
        "* Persistent browser selection for configuration shortlist results with "
        "bundle-compatible JSON and plain code downloads.\n"
    )
    if bullet not in text:
        text = replace_once(
            text,
            "### Added\n\n",
            "### Added\n\n"
            + bullet
            + "* End-to-end browser selection export validation through the transactional comparison bundle.\n",
            "changelog Added",
        )
    write(path, text)


def patch_roadmap() -> None:
    path = "project/ROADMAP.md"
    text = read(path)
    completed = (
        "- trwały wybór konfiguracji w przeglądarce oraz deterministyczny "
        "eksport JSON i TXT zgodny z pakietem porównań,\n"
    )
    if completed not in text:
        marker = (
            "- transakcyjny pakiet porównań z shortlisty z grupowaniem według "
            "jednorodnych zakresów i manifestem SHA-256,\n"
        )
        text = replace_once(
            text,
            marker,
            marker + completed,
            "roadmap completed selection export",
        )
    text = text.replace(
        "- przeglądarkowy eksport jawnie wybranych konfiguracji do pakietu porównań,\n",
        "- przegląd kierunku kolejnych produktów wykorzystujących zamknięty portfel danych,\n",
        1,
    )
    write(path, text)


def patch_state() -> None:
    path = Path("project/state.json")
    state = json.loads(path.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-19"
    state["phase"] = "Data Product Utilization"
    state["reference_delivery"] = {
        "name": "Interactive Selection Export Planning Review",
        "pull_request": 150,
        "head_sha": "b9bdf9160ba30a6c81f729750c52d3625bf15744",
        "quality_run": 747,
    }
    state["baseline"]["tests"] = 628
    state["current_package"] = {
        "name": "Interactive Configuration Selection Export",
        "status": "active",
        "goal": "Add persistent browser selection controls and deterministic offline JSON and text downloads directly consumable by the comparison bundle.",
    }
    state["next_package"] = {
        "name": "Data Product Utilization Milestone Review",
        "status": "planned",
        "goal": "Review the five delivered data products, verify their end-to-end contracts and select the next product direction or an explicit pause boundary."
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
        old = 'self.assertEqual(baseline["tests"], 620)'
        new = 'self.assertEqual(baseline["tests"], 628)'
        if old not in text and new not in text:
            raise RuntimeError(f"baseline assertion missing in {path}")
        path.write_text(
            text.replace(old, new, 1),
            encoding="utf-8",
            newline="\n",
        )


def main() -> None:
    patch_readme()
    patch_changelog()
    patch_roadmap()
    patch_state()
    patch_baseline_assertions()


if __name__ == "__main__":
    main()
