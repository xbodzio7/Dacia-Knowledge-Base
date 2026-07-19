from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "finalize-initial-release-publication.yml"
SCRIPT = Path(__file__)

RELEASE_TAG = "data-products-v1.0.0"
RELEASE_URL = (
    "https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/"
    "data-products-v1.0.0"
)
TESTED_MAIN_SHA = "653ddacf9dcaeefa356f53e3c00e71666f5c5b3e"
ARCHIVE_SHA = "434be3ba2daa941f4fb37dbc1a542ede705e8396f32e8c1221fbfc02080dcf78"
MANIFEST_SHA = "ee449a628bbf60dc017b625abcb85be8f2ebea440ff05840e0e62c35f342064f"
SUMS_SHA = "84ba40b3f98b9baefa03cd61e5c6a8d9534c22b88a0cc2ded0632f67e5b61404"


def update(path: Path, transform) -> None:
    text = path.read_text(encoding="utf-8")
    updated = transform(text)
    if updated != text:
        path.write_text(updated, encoding="utf-8", newline="")


def update_readme(text: str) -> str:
    marker = "`project/packages/versioned-data-product-release-publication.md`."
    paragraph = (
        "Pierwsze publiczne wydanie zostało opublikowane jako "
        "[`data-products-v1.0.0`](https://github.com/xbodzio7/"
        "Dacia-Knowledge-Base/releases/tag/data-products-v1.0.0) z commita "
        f"`{TESTED_MAIN_SHA}`. Trzy publiczne assety zostały ponownie pobrane, "
        "zweryfikowane przez `data-product-release --verify` i zapisane w "
        "`project/releases/data-products-v1.0.0.md`."
    )
    if "Pierwsze publiczne wydanie zostało opublikowane" in text:
        return text
    if marker not in text:
        raise RuntimeError("README release marker not found")
    return text.replace(marker, marker + "\n\n" + paragraph, 1)


def update_changelog(text: str) -> str:
    marker = "## Unreleased\n\n### Added\n\n"
    bullet = (
        "* Published the first immutable public data-product release, "
        f"`{RELEASE_TAG}`, from main commit `{TESTED_MAIN_SHA}` with three "
        "downloaded and verifier-confirmed assets.\n"
    )
    if "Published the first immutable public data-product release" in text:
        return text
    if marker not in text:
        raise RuntimeError("CHANGELOG Added marker not found")
    return text.replace(marker, marker + bullet, 1)


def update_roadmap(text: str) -> str:
    marker = (
        "- wersjonowane, deterministyczne archiwa produktów z manifestem, "
        "SHA-256 i ręczną publikacją GitHub Release,"
    )
    bullet = (
        "- pierwsze publiczne wydanie `data-products-v1.0.0` z trzema "
        "pobranymi i ponownie zweryfikowanymi assetami,"
    )
    if "pierwsze publiczne wydanie `data-products-v1.0.0`" in text:
        return text
    if marker not in text:
        raise RuntimeError("ROADMAP release marker not found")
    return text.replace(marker, marker + "\n" + bullet, 1)


update(ROOT / "README.md", update_readme)
update(ROOT / "CHANGELOG.md", update_changelog)
update(ROOT / "project" / "ROADMAP.md", update_roadmap)

release_record = f"""# Data Products v1.0.0

## Identity

- Release tag: [`{RELEASE_TAG}`]({RELEASE_URL})
- GitHub Release ID: `356447618`
- Published at: `2026-07-19T22:35:40Z`
- Tested main commit: `{TESTED_MAIN_SHA}`
- Source snapshot date: `2026-06-26`

## Product inventory

- Active configurations: `53`
- Independent and comparable reporting scopes: `13 / 13`
- Singleton scopes: `0`
- Archive members: `59`
- Cross-scope pairs: none
- Ranking, recommendations and inferred values: absent

## Public assets

| Asset | Bytes | SHA-256 |
| --- | ---: | --- |
| `dacia-knowledge-base-data-products-v1.0.0.zip` | 30,993,350 | `{ARCHIVE_SHA}` |
| `data-product-release-manifest.json` | 14,337 | `{MANIFEST_SHA}` |
| `SHA256SUMS` | 213 | `{SUMS_SHA}` |

## Verification

A read-only GitHub Actions audit downloaded all three public assets and executed
`python tools/data_product_release.py --verify` against version `1.0.0` and the
tested main commit. The verifier accepted the archive inventory, paths, media
types, sizes, checksums, release identity and exact commit binding.

- Verification workflow run: `29706481294`
- Publication evidence artifact: `8448056707`
- Evidence retention through: `2026-10-17T22:37:22Z`

This release changes distribution only. It does not add, infer or modify source
data.
"""
release_path = ROOT / "project" / "releases" / "data-products-v1.0.0.md"
release_path.parent.mkdir(parents=True, exist_ok=True)
if release_path.exists() and release_path.read_text(encoding="utf-8") != release_record:
    raise RuntimeError("existing release record differs from verified publication")
release_path.write_text(release_record, encoding="utf-8", newline="")

state_path = ROOT / "project" / "state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
state["reference_delivery"] = {
    "name": "Initial Data Product Release Readiness Review",
    "pull_request": 157,
    "head_sha": "c64292e43f9b3fa02dedb9d755ddf619f2cde8b1",
    "quality_run": 836,
}
state["current_package"] = {
    "name": "Initial Data Product Release Publication",
    "status": "complete",
    "goal": (
        "Publish data-products-v1.0.0 from the explicitly authorized and "
        "verified main commit."
    ),
}
state["next_package"] = {
    "name": "Data Product Release Consumption Review",
    "status": "planned",
    "goal": (
        "Assess discoverability, download, verification and user workflow of "
        "data-products-v1.0.0 and select the next utilization improvement "
        "without expanding source data."
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
    [sys.executable, str(ROOT / "tools" / "dkb.py"), "documentation-baseline", "--check"],
    cwd=ROOT,
    check=True,
)

WORKFLOW.unlink(missing_ok=True)
SCRIPT.unlink(missing_ok=True)
