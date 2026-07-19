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


def patch_unified_cli() -> None:
    path = "tools/dkb.py"
    text = read(path)
    old = (
        '        "[--require-standard-equipment CODE] "\n'
        '        "[--json FILE] [--markdown FILE] [--csv FILE]",\n'
    )
    new = (
        '        "[--require-standard-equipment CODE] "\n'
        '        "[--json FILE] [--markdown FILE] [--csv FILE] "\n'
        '        "[--html FILE]",\n'
    )
    if '"[--html FILE]",' not in text[text.find('"configuration-shortlist"'):text.find('"configuration-comparison"')]:
        text = replace_once(text, old, new, "shortlist HTML usage")
    if "--html ../configuration-shortlist.html" not in text:
        marker = '''    print(
        "  python tools/dkb.py configuration-shortlist --transmission automatic "
        "--max-price 100000 --csv ../configuration-shortlist.csv"
    )
'''
        replacement = marker + '''    print(
        "  python tools/dkb.py configuration-shortlist --transmission automatic "
        "--max-price 100000 --html ../configuration-shortlist.html"
    )
'''
        text = replace_once(
            text,
            marker,
            replacement,
            "shortlist HTML example",
        )
    write(path, text)


def patch_readme() -> None:
    path = "README.md"
    text = read(path)
    if "--html ../configuration-shortlist.html" not in text:
        text = replace_once(
            text,
            "  --markdown ../configuration-shortlist.md \\\n  --csv ../configuration-shortlist.csv\n",
            "  --markdown ../configuration-shortlist.md \\\n  --csv ../configuration-shortlist.csv \\\n  --html ../configuration-shortlist.html\n",
            "README shortlist command",
        )
    paragraph = (
        "HTML osadza pełny aktywny snapshot dla wskazanej daty, a kryteria CLI\n"
        "ustawiają początkowy stan formularza. Wyczyszczenie filtrów przywraca cały\n"
        "katalog, podczas gdy JSON, Markdown i CSV pozostają wynikami filtrów\n"
        "wykonanych po stronie Pythona. Plik działa bez serwera i nie pobiera\n"
        "zewnętrznych skryptów, stylów ani fontów.\n\n"
    )
    if paragraph not in text:
        marker = (
            "JSON zawiera pełne filtry, niełączne statystyki przyczyn wykluczeń i liczniki\n"
            "niewiadomych. Markdown dostarcza czytelną shortlistę, a CSV jeden płaski wiersz\n"
            "na dopasowaną konfigurację z proweniencją ceny, miejsc i wyposażenia.\n\n"
        )
        text = replace_once(
            text,
            marker,
            marker + paragraph,
            "README shortlist HTML paragraph",
        )
    required = (
        "--html ../configuration-shortlist.html",
        "HTML osadza pełny aktywny snapshot",
        "Wyczyszczenie filtrów przywraca cały",
    )
    missing = [marker for marker in required if marker not in text]
    if missing:
        raise RuntimeError(f"README HTML markers missing: {missing}")
    write(path, text)


def patch_changelog() -> None:
    path = "CHANGELOG.md"
    text = read(path)
    bullet = (
        "* Self-contained interactive configuration shortlist HTML with a full "
        "source-backed browser catalog and CLI-defined initial filters.\n"
    )
    if bullet not in text:
        text = replace_once(
            text,
            "### Added\n\n",
            "### Added\n\n"
            + bullet
            + "* JavaScript/Python semantic parity tests for metadata, price, seat and equipment shortlist filters.\n",
            "changelog Added",
        )
    write(path, text)


def patch_roadmap() -> None:
    path = "project/ROADMAP.md"
    text = read(path)
    completed = (
        "- interaktywna przeglądarkowa shortlista konfiguracji z pełnym "
        "snapshotem i testami parytetu semantyki,\n"
    )
    if completed not in text:
        marker = (
            "- deterministyczna shortlista konfiguracji z filtrami ceny, napędu, "
            "skrzyni, miejsc i wyposażenia,\n"
        )
        text = replace_once(
            text,
            marker,
            marker + completed,
            "roadmap completed shortlist HTML",
        )
    text = text.replace(
        "- interaktywna przeglądarkowa shortlista konfiguracji,\n",
        "- przepływ shortlisty do porównania wybranych konfiguracji,\n",
        1,
    )
    write(path, text)


def patch_state() -> None:
    path = Path("project/state.json")
    state = json.loads(path.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-19"
    state["phase"] = "Data Product Utilization"
    state["reference_delivery"] = {
        "name": "Interactive Configuration Shortlist HTML Planning Review",
        "pull_request": 146,
        "head_sha": "c5571a9006143da3afcff7ebb9534d5cd1f9f982",
        "quality_run": 723,
    }
    state["baseline"]["tests"] = 610
    state["current_package"] = {
        "name": "Interactive Configuration Shortlist HTML",
        "status": "active",
        "goal": "Publish a self-contained 53-configuration browser catalog with CLI-defined initial filters and JavaScript semantics verified against the Python shortlist engine.",
    }
    state["next_package"] = {
        "name": "Shortlist-to-Comparison Workflow Planning Review",
        "status": "planned",
        "goal": "Select a transparent workflow that turns explicitly selected shortlist results into an existing source-backed configuration comparison without adding ranking or inferred values.",
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
        old = 'self.assertEqual(baseline["tests"], 603)'
        new = 'self.assertEqual(baseline["tests"], 610)'
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
