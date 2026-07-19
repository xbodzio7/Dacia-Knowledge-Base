from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (ROOT / path).write_text(content, encoding="utf-8")


def replace_once(text: str, old: str, new: str, path: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"missing expected marker in {path}: {old!r}")
    return text.replace(old, new, 1)


state_path = ROOT / "project/state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
state["baseline"]["tests"] = 628
state["reference_delivery"] = {
    "name": "Configuration Comparison Bundle CLI",
    "pull_request": 149,
    "head_sha": "960b410a5afb0389aa8d88572ff8141452068c4d",
    "quality_run": 745,
}
state["current_package"] = {
    "name": "Interactive Configuration Selection Export",
    "status": "active",
    "goal": "Add persistent browser selection controls and deterministic offline JSON and text downloads consumable by the comparison bundle.",
}
state["next_package"] = {
    "name": "Data Product Utilization Milestone Review",
    "status": "planned",
    "goal": "Review the five completed user-facing data products, validate their end-to-end workflow and select the next utilization milestone without expanding source data.",
}
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

readme_path = "README.md"
readme = read(readme_path)
anchor = (
    "HTML osadza pełny aktywny snapshot dla wskazanej daty, a kryteria CLI\n"
    "ustawiają początkowy stan formularza. Wyczyszczenie filtrów przywraca cały\n"
    "katalog, podczas gdy JSON, Markdown i CSV pozostają wynikami filtrów\n"
    "wykonanych po stronie Pythona. Plik działa bez serwera i nie pobiera\n"
    "zewnętrznych skryptów, stylów ani fontów."
)
selection_text = anchor + (
    "\n\nKażda karta w przeglądarce może zostać jawnie wybrana do porównania. Wybór jest\n"
    "niezależny od filtrów: ukryte konfiguracje pozostają zaznaczone, a akcje\n"
    "`Wybierz widoczne`, usuwanie pojedynczych pozycji i `Wyczyść wybór` nie\n"
    "zmieniają kryteriów shortlisty. Panel wyboru zachowuje deterministyczną\n"
    "kolejność katalogu.\n\n"
    "`Pobierz JSON` zapisuje wybór w formacie bezpośrednio obsługiwanym przez\n"
    "`configuration-comparison-bundle`, wraz z datą snapshotu i metadanymi\n"
    "źródłowymi ceny oraz liczby miejsc. `Pobierz kody TXT` zapisuje jeden dokładny\n"
    "kod konfiguracji na linię. Eksport nie zawiera czasu uruchomienia, dlatego ten\n"
    "sam snapshot i wybór tworzą identyczne bajty."
)
readme = replace_once(readme, anchor, selection_text, readme_path)
write(readme_path, readme)

roadmap_path = "project/ROADMAP.md"
roadmap = read(roadmap_path)
bundle_bullet = "- transakcyjny pakiet porównań z shortlisty z grupowaniem według jednorodnych zakresów i manifestem SHA-256,"
selection_bullet = "- trwały wybór konfiguracji w przeglądarce z deterministycznym eksportem JSON i TXT zgodnym z pakietem porównań,"
roadmap = replace_once(
    roadmap,
    bundle_bullet,
    bundle_bullet + "\n" + selection_bullet,
    roadmap_path,
)
roadmap = roadmap.replace(
    "- przeglądarkowy eksport jawnie wybranych konfiguracji do pakietu porównań,\n",
    "",
    1,
)
write(roadmap_path, roadmap)

changelog_path = "CHANGELOG.md"
changelog = read(changelog_path)
added_anchor = "### Added\n"
added_text = added_anchor + (
    "\n* Persistent browser selection independent of active shortlist filters, with visible-set and individual controls.\n"
    "* Deterministic bundle-compatible shortlist JSON and plain configuration-code exports verified end to end."
)
changelog = replace_once(changelog, added_anchor, added_text, changelog_path)
write(changelog_path, changelog)

for test_path in (
    "tests/test_jogger_payload_performance_ranges.py",
    "tests/test_jogger_wltp_efficiency_ranges.py",
):
    text = read(test_path)
    old = 'self.assertEqual(baseline["tests"], 620)'
    new = 'self.assertEqual(baseline["tests"], 628)'
    if old not in text and new not in text:
        raise RuntimeError(f"missing baseline assertion in {test_path}")
    write(test_path, text.replace(old, new))
