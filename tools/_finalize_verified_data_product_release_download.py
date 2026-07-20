#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import project_state


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"expected exactly one anchor in {path}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8", newline="")


def patch_dkb() -> None:
    path = ROOT / "tools/dkb.py"
    old = '''    "data-product-release": (
        "data_product_release.py",
        "Build or verify deterministic versioned data-product release assets.",
        "--output-directory DIR [--version MAJOR.MINOR.PATCH] "
        "[--commit-sha SHA] [--verify]",
    ),
'''
    new = old + '''    "data-product-release-download": (
        "data_product_release_download.py",
        "Download, verify and safely extract one immutable public data-product release.",
        "--version MAJOR.MINOR.PATCH --output-directory DIR",
    ),
'''
    replace_once(path, old, new)

    old_example = '''    print(
        "  python tools/dkb.py data-product-release --version 1.0.0 "
        "--commit-sha 0123456789012345678901234567890123456789 "
        "--output-directory ../data-product-release"
    )
'''
    new_example = old_example + '''    print(
        "  python tools/dkb.py data-product-release-download --version 1.0.0 "
        "--output-directory ../dkb-data-products-v1.0.0"
    )
'''
    replace_once(path, old_example, new_example)


def patch_downloader() -> None:
    path = ROOT / "tools/reporting/data_product_release_download.py"
    old = '''def download_release(
    version: str,
    output_directory: Path,
    *,
    token: str | None = None,
    opener: OpenUrl = urlopen,
) -> dict[str, Any]:
    normalized_version = normalize_version(version)
    selected_token = token if token is not None else os.environ.get("GITHUB_TOKEN")
    build_root = _prepare_output_directory(output_directory)
'''
    new = '''def download_release(
    version: str,
    output_directory: Path,
    *,
    token: str | None = None,
    opener: OpenUrl = urlopen,
) -> dict[str, Any]:
    try:
        normalized_version = normalize_version(version)
    except ReleaseError as exc:
        raise ReleaseDownloadError(str(exc)) from exc
    selected_token = token if token is not None else os.environ.get("GITHUB_TOKEN")
    build_root = _prepare_output_directory(output_directory)
'''
    replace_once(path, old, new)

    old_tail = '''        build_root.replace(output_directory)
        return result
    except Exception:
        shutil.rmtree(build_root, ignore_errors=True)
        raise
'''
    new_tail = '''        build_root.replace(output_directory)
        return result
    except ReleaseDownloadError:
        shutil.rmtree(build_root, ignore_errors=True)
        raise
    except ReleaseError as exc:
        shutil.rmtree(build_root, ignore_errors=True)
        raise ReleaseDownloadError(str(exc)) from exc
    except Exception as exc:
        shutil.rmtree(build_root, ignore_errors=True)
        raise ReleaseDownloadError(
            f"cannot download data product release: {exc}"
        ) from exc
'''
    replace_once(path, old_tail, new_tail)


def patch_readme() -> None:
    path = ROOT / "README.md"
    structure = "## Struktura repozytorium\n"
    quick_start = '''## Gotowe produkty offline

Zweryfikowane publiczne wydanie `data-products-v1.0.0` można pobrać, sprawdzić
oraz bezpiecznie rozpakować jedną komendą:

```bash
python tools/dkb.py data-product-release-download \\
  --version 1.0.0 \\
  --output-directory ../dkb-data-products-v1.0.0
```

Komenda wymaga jawnej, niezmiennej wersji. Sprawdza tag GitHub, dokładny zestaw
trzech assetów, manifest, `SHA256SUMS`, każdy element archiwum i powiązanie z
commitem źródłowym. Po sukcesie wskazuje gotowe do otwarcia: interaktywną
shortlistę HTML, skoroszyt XLSX porównań, manifest pakietu i notatki wydania.

'''
    replace_once(path, structure, quick_start + structure)

    old_row = "| `data-product-release` | Budowa i weryfikacja wersjonowanego pakietu produktów offline |\n"
    new_row = old_row + "| `data-product-release-download` | Pobranie, weryfikacja i bezpieczne rozpakowanie publicznego wydania |\n"
    replace_once(path, old_row, new_row)

    old_release = '''Pierwsze publiczne wydanie zostało opublikowane jako [`data-products-v1.0.0`](https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/data-products-v1.0.0) z commita `653ddacf9dcaeefa356f53e3c00e71666f5c5b3e`. Trzy publiczne assety zostały ponownie pobrane, zweryfikowane przez `data-product-release --verify` i zapisane w `project/releases/data-products-v1.0.0.md`.
'''
    new_release = old_release + '''
Dla użytkownika końcowego preferowaną ścieżką jest komenda
`data-product-release-download`. Pobiera ona dokładnie wskazaną wersję, rozwiązuje
tag do commita, weryfikuje trzy publiczne assety istniejącym kontraktem i zapisuje
zweryfikowane pliki w `assets/`, a bezpiecznie rozpakowane produkty w `contents/`.
Szczegóły opisuje `project/packages/verified-data-product-release-download-cli.md`.
'''
    replace_once(path, old_release, new_release)


def patch_changelog() -> None:
    path = ROOT / "CHANGELOG.md"
    anchor = "### Added\n\n"
    addition = (
        "* Verified public data-product release download and safe extraction CLI "
        "with immutable tag binding, canonical asset enforcement and ready-to-open entry points.\n"
        "* Read-only Linux and Windows smoke verification of the public `data-products-v1.0.0` release.\n"
    )
    replace_once(path, anchor, anchor + addition)


def patch_roadmap() -> None:
    path = ROOT / "project/ROADMAP.md"
    anchor = "- pierwsze publiczne wydanie `data-products-v1.0.0` z trzema pobranymi i ponownie zweryfikowanymi assetami,\n"
    addition = "- zweryfikowane pobieranie i bezpieczne rozpakowanie jawnej wersji publicznego wydania do lokalnego workspace,\n"
    replace_once(path, anchor, anchor + addition)


def patch_state() -> None:
    state_path = ROOT / "project/state.json"
    summary_path = ROOT / "project/STATE_SUMMARY.md"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-20"
    state["reference_delivery"] = {
        "name": "Data Product Release Consumption Review",
        "pull_request": 161,
        "head_sha": "8207a33889388062f04eb9719c6401ecfed84d5f",
        "quality_run": 851,
    }
    state["baseline"]["tests"] = 667
    state["current_package"] = {
        "name": "Verified Data Product Release Download CLI",
        "status": "complete",
        "goal": (
            "Download an explicit immutable release version, verify its GitHub "
            "tag and three canonical assets, safely extract validated contents "
            "and report ready-to-open user entry points."
        ),
    }
    state["next_package"] = {
        "name": "Local Data Product Workspace Index Planning Review",
        "status": "planned",
        "goal": (
            "Select a deterministic local landing-page contract linking the "
            "downloaded shortlist, workbook, scope reports and provenance without "
            "republishing the release or expanding source data."
        ),
    }
    project_state.validate_state(state)
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="",
    )
    summary_path.write_text(
        project_state.render_summary(state),
        encoding="utf-8",
        newline="",
    )


def main() -> int:
    patch_dkb()
    patch_downloader()
    patch_readme()
    patch_changelog()
    patch_roadmap()
    patch_state()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
