#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"expected exactly one anchor in {path}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8", newline="")


def patch_readme() -> None:
    path = ROOT / "README.md"
    anchor = '''Opcja `--json` zwraca deterministyczny raport dla automatyzacji. Weryfikator
ponownie sprawdza trzy assety, wszystkie rozpakowane pliki, dokładne bajty
`index.html` i bezpieczne lokalne odnośniki.
'''
    addition = anchor + '''
Pełny przepływ — od pobrania wydania przez shortlistę i własne porównania po
późniejszą kontrolę integralności — opisuje
[`project/guides/data-product-consumer-guide.md`](project/guides/data-product-consumer-guide.md).
'''
    replace_once(path, anchor, addition)


def patch_changelog() -> None:
    path = ROOT / "CHANGELOG.md"
    anchor = "### Added\n\n"
    addition = (
        "* Source-backed Polish data-product consumer guide covering immutable "
        "download, offline navigation, shortlist selection, custom comparison bundles, "
        "provenance, recovery and lifecycle verification.\n"
        "* Automated validation that every documented unified-CLI command, product path, "
        "version example and semantic boundary remains valid.\n"
    )
    replace_once(path, anchor, anchor + addition)


def patch_roadmap() -> None:
    path = ROOT / "project/ROADMAP.md"
    anchor = (
        "- całkowicie offline'owa i tylko do odczytu ponowna weryfikacja assetów, "
        "rozpakowanych plików, indeksu i lokalnych odnośników workspace,\n"
    )
    addition = (
        "- jeden źródłowy przewodnik konsumencki obejmujący pobranie, nawigację, "
        "wybór, własne porównania, proweniencję i kontrolę integralności,\n"
    )
    replace_once(path, anchor, anchor + addition)


def patch_state() -> None:
    path = ROOT / "project/state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-20"
    state["reference_delivery"] = {
        "name": "Local Data Product Workspace Verification CLI",
        "pull_request": 166,
        "head_sha": "d278eb71b97f782635c2b528a872f885bc367a36",
        "quality_run": 908,
    }
    state["current_package"] = {
        "name": "Data Product Consumer Guide",
        "status": "complete",
        "goal": (
            "Consolidate the immutable release, verified download, offline index, "
            "selection and comparison flow, and lifecycle verification into one "
            "source-backed consumer guide without expanding source data."
        ),
    }
    state["next_package"] = {
        "name": "Data Product Utilization Completion Review",
        "status": "planned",
        "goal": (
            "Assess whether the existing public release, offline workspace, verification "
            "and consumer documentation complete the current utilization phase, and "
            "select only a clearly justified next package without expanding source data."
        ),
    }
    path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="",
    )


def main() -> None:
    patch_readme()
    patch_changelog()
    patch_roadmap()
    patch_state()


if __name__ == "__main__":
    main()
