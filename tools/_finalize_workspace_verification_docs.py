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
    old = '''Komenda wymaga jawnej, niezmiennej wersji. Sprawdza tag GitHub, dokładny zestaw
trzech assetów, manifest, `SHA256SUMS`, każdy element archiwum i powiązanie z
commitem źródłowym. Po sukcesie wskazuje gotowe do otwarcia: interaktywną
shortlistę HTML, skoroszyt XLSX porównań, manifest pakietu i notatki wydania.
'''
    new = '''Komenda wymaga jawnej, niezmiennej wersji. Sprawdza tag GitHub, dokładny zestaw
trzech assetów, manifest, `SHA256SUMS`, każdy element archiwum i powiązanie z
commitem źródłowym. Po sukcesie tworzy lokalny `index.html` i wskazuje gotowe do
otwarcia: interaktywną shortlistę HTML, skoroszyt XLSX porównań, manifest
pakietu i notatki wydania.

Integralność istniejącego workspace można później sprawdzić całkowicie offline
i bez modyfikowania plików:

```bash
python tools/dkb.py data-product-workspace-verify \\
  --workspace-directory ../dkb-data-products-v1.0.0
```

Opcja `--json` zwraca deterministyczny raport dla automatyzacji. Weryfikator
ponownie sprawdza trzy assety, wszystkie rozpakowane pliki, dokładne bajty
`index.html` i bezpieczne lokalne odnośniki.
'''
    replace_once(path, old, new)


def patch_changelog() -> None:
    path = ROOT / "CHANGELOG.md"
    anchor = "### Added\n\n"
    addition = (
        "* Fully offline, read-only local data-product workspace verification CLI "
        "covering canonical assets, extracted member hashes, deterministic index bytes and safe links.\n"
        "* Linux and Windows live verification of public `v1.0.0`, including rejection of a deliberately corrupted copied workspace without further file changes.\n"
    )
    replace_once(path, anchor, anchor + addition)


def patch_roadmap() -> None:
    path = ROOT / "project/ROADMAP.md"
    anchor = (
        "- deterministyczna lokalna strona startowa HTML łącząca produkty, "
        "zakresy porównań i proweniencję wydania,\n"
    )
    addition = (
        "- całkowicie offline'owa i tylko do odczytu ponowna weryfikacja assetów, "
        "rozpakowanych plików, indeksu i lokalnych odnośników workspace,\n"
    )
    replace_once(path, anchor, anchor + addition)


def patch_state() -> None:
    path = ROOT / "project/state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-20"
    state["reference_delivery"] = {
        "name": "Data Product Utilization Milestone Review",
        "pull_request": 165,
        "head_sha": "b5abac9eb8e71357fcdbdbf54cde0a33f89ca330",
        "quality_run": 901,
    }
    state["current_package"] = {
        "name": "Local Data Product Workspace Verification CLI",
        "status": "complete",
        "goal": (
            "Verify an existing local data-product workspace fully offline, "
            "including canonical assets, extracted member hashes, deterministic "
            "index bytes and safe local links, without modifying the workspace."
        ),
    }
    state["next_package"] = {
        "name": "Data Product Consumer Guide",
        "status": "planned",
        "goal": (
            "Consolidate the immutable release, verified download, offline index, "
            "selection and comparison flow, and lifecycle verification into one "
            "source-backed consumer guide without expanding source data."
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
