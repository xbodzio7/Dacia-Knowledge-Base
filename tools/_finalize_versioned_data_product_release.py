from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def update(path: Path, transform) -> None:
    text = path.read_text(encoding="utf-8")
    updated = transform(text)
    if updated == text:
        return
    path.write_text(updated, encoding="utf-8", newline="")


def readme(text: str) -> str:
    text = text.replace("sześciоarkuszowy", "sześcioarkuszowy")
    command_marker = (
        "| `configuration-comparison` | Porównanie cen, wartości technicznych "
        "i wyposażenia konfiguracji |"
    )
    command_row = (
        command_marker
        + "\n| `data-product-release` | Budowa i weryfikacja wersjonowanego "
        "pakietu produktów offline |"
    )
    if command_row not in text:
        if command_marker not in text:
            raise RuntimeError("README command marker not found")
        text = text.replace(command_marker, command_row, 1)

    marker = (
        "Pakiet tworzy także deterministyczny skoroszyt XLSX z sześcioma "
        "arkuszami, pełnymi stanami porównań i proweniencją. Szczegółowy "
        "kontrakt opisuje `project/packages/"
        "configuration-comparison-workbook-export.md`."
    )
    section = """### Wersjonowana dystrybucja produktów

Komenda `data-product-release` buduje jeden deterministyczny kandydat wydania
obejmujący kompletną shortlistę 53 aktywnych konfiguracji i pełny pakiet
porównań dla 13 niezależnych zakresów.

```bash
python tools/dkb.py data-product-release \\
  --version 1.0.0 \\
  --commit-sha 0123456789012345678901234567890123456789 \\
  --output-directory ../data-product-release
```

Powstają dokładnie trzy assety: wersjonowane archiwum ZIP, zewnętrzny
`data-product-release-manifest.json` i `SHA256SUMS`. Archiwum zawiera 59 plików:
shortlistę JSON, Markdown, CSV i HTML, 13 grup raportowych, manifest bundle oraz
sześcioarkuszowy XLSX. Manifest zachowuje rozmiary, typy MIME i SHA-256 każdego
pliku; nie jest kopiowany do ZIP, aby uniknąć samoodniesienia hashu archiwum.

Tryb `--verify` sprawdza istniejący katalog bez przebudowy. Workflow
`Versioned Data Product Release` buduje read-only kandydat na Pull Requestach,
a utworzenie tagu `data-products-vMAJOR.MINOR.PATCH` i GitHub Release jest
możliwe wyłącznie przez ręczny `workflow_dispatch` z `main`. Istniejące tagi i
wydania nie są nadpisywane. Pełny kontrakt opisuje
`project/packages/versioned-data-product-release-publication.md`.
"""
    insertion = marker + "\n\n" + section.rstrip()
    if section.strip() not in text:
        if marker not in text:
            raise RuntimeError("README workbook marker not found")
        text = text.replace(marker, insertion, 1)
    return text


def changelog(text: str) -> str:
    marker = "## Unreleased\n\n### Added\n\n"
    addition = (
        marker
        + "* Deterministic versioned data-product release archives covering "
        "the complete shortlist and all 13 comparison scopes.\n"
        + "* External release manifests, SHA256SUMS and guarded manual GitHub "
        "Release publication from main.\n"
    )
    if "Deterministic versioned data-product release archives" not in text:
        if marker not in text:
            raise RuntimeError("changelog marker not found")
        text = text.replace(marker, addition, 1)
    return text


def roadmap(text: str) -> str:
    marker = (
        "- deterministyczny XLSX z sześcioma arkuszami i identycznymi bajtami "
        "na Linuxie oraz Windows,"
    )
    addition = (
        marker
        + "\n- wersjonowane, deterministyczne archiwa produktów z manifestem, "
        "SHA-256 i ręczną publikacją GitHub Release,"
    )
    if "wersjonowane, deterministyczne archiwa produktów" not in text:
        if marker not in text:
            raise RuntimeError("roadmap release marker not found")
        text = text.replace(marker, addition, 1)
    return text


def review(text: str) -> str:
    text = text.replace(
        "- a copy of `data-product-release-manifest.json`.\n",
        "",
    )
    marker = (
        "The release workflow does not publish the Quality log or internal "
        "gap-review working reports as user products. Those remain available "
        "through the existing Quality artifact."
    )
    addition = (
        marker
        + "\n\nThe release manifest remains a standalone asset and records the "
        "final ZIP hash. It is not copied into the ZIP because that would "
        "create an impossible self-reference between the manifest and the "
        "archive containing it."
    )
    if "impossible self-reference" not in text:
        if marker not in text:
            raise RuntimeError("distribution review marker not found")
        text = text.replace(marker, addition, 1)
    return text


update(ROOT / "README.md", readme)
update(ROOT / "CHANGELOG.md", changelog)
update(ROOT / "project" / "ROADMAP.md", roadmap)
update(
    ROOT / "project" / "reviews" / "data-product-distribution-planning-review.md",
    review,
)

for relative in (
    "tests/test_jogger_payload_performance_ranges.py",
    "tests/test_jogger_wltp_efficiency_ranges.py",
):
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    updated = text.replace(
        'self.assertEqual(baseline["tests"], 640)',
        'self.assertEqual(baseline["tests"], 654)',
    )
    if 'self.assertEqual(baseline["tests"], 640)' in updated:
        raise RuntimeError(f"old baseline remains in {relative}")
    path.write_text(updated, encoding="utf-8", newline="")

state_path = ROOT / "project" / "state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
state["reference_delivery"] = {
    "name": "Data Product Distribution Planning Review",
    "pull_request": 155,
    "head_sha": "5c861728f32eafaa52db0ef72974d841d599b530",
    "quality_run": 805,
}
state["baseline"]["tests"] = 654
state["current_package"] = {
    "name": "Versioned Data Product Release Publication",
    "status": "active",
    "goal": (
        "Publish deterministic versioned GitHub Release assets for the "
        "existing offline data products."
    ),
}
state["next_package"] = {
    "name": "Initial Data Product Release Readiness Review",
    "status": "planned",
    "goal": (
        "Verify the immutable publication contract and select the first "
        "public release version without publishing it."
    ),
}
state_path.write_text(
    json.dumps(state, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
    newline="",
)

subprocess.run(
    [sys.executable, str(ROOT / "tools" / "dkb.py"), "project-state", "--apply"],
    cwd=ROOT,
    check=True,
)
subprocess.run(
    [
        sys.executable,
        str(ROOT / "tools" / "dkb.py"),
        "documentation-baseline",
        "--apply",
    ],
    cwd=ROOT,
    check=True,
)
