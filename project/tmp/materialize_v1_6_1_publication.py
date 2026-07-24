from __future__ import annotations

import json
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected one match in {path}, found {count}: {old[:80]!r}")
    file.write_text(text.replace(old, new, 1), encoding="utf-8")


SOURCE_SHA = "4b77571c788b862a6543161b9343a35f464bd7c6"
HEAD_SHA = "8dce2a3f6ccbeb563fb9532c7b86c36d294735bf"

replace_once(
    "README.md",
    "Najnowsze zweryfikowane publiczne wydanie `data-products-v1.6.0` można pobrać, sprawdzić",
    "Najnowsze zweryfikowane publiczne wydanie `data-products-v1.6.1` można pobrać, sprawdzić",
)
replace_once(
    "README.md",
    "  --version 1.6.0 \\\n  --output-directory ../dkb-data-products-v1.6.0",
    "  --version 1.6.1 \\\n  --output-directory ../dkb-data-products-v1.6.1",
)
replace_once(
    "README.md",
    "  --workspace-directory ../dkb-data-products-v1.6.0",
    "  --workspace-directory ../dkb-data-products-v1.6.1",
)
old_release_paragraph = "Najnowsze wydanie [`data-products-v1.6.0`](https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/data-products-v1.6.0) zostało opublikowane z dokładnego commita `539fba58d1ee2ef538c782b20e049be482d72988`. Używa oficjalnych zdjęć pięciu rodzin modeli Dacia Polska z lokalnym fallbackiem SVG, przedstawia wybory w stylu konfiguratora, umieszcza ceny minimalną i maksymalną w jednym wierszu, pokazuje wyłącznie źródłowo kompletne i rzeczywiście różnicujące wyposażenie oraz porównuje wszystkie zapisane parametry techniczne i wyposażenie. Pole tekstowe przy wyposażeniu filtruje nazwy na liście; samochody są zawężane dopiero po zaznaczeniu pozycji. Trwały zapis publikacji znajduje się w `project/releases/data-products-v1.6.0.md`, a opis pakietu w `project/packages/data-products-v1.6.0-configurator-style-full-comparison.md`."
new_release_paragraph = "Wydanie [`data-products-v1.6.0`](https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/data-products-v1.6.0) zostało opublikowane z dokładnego commita `539fba58d1ee2ef538c782b20e049be482d72988`. Używa oficjalnych zdjęć pięciu rodzin modeli Dacia Polska z lokalnym fallbackiem SVG, przedstawia wybory w stylu konfiguratora, umieszcza ceny minimalną i maksymalną w jednym wierszu, pokazuje wyłącznie źródłowo kompletne i rzeczywiście różnicujące wyposażenie oraz porównuje wszystkie zapisane parametry techniczne i wyposażenie. Trwały zapis publikacji znajduje się w `project/releases/data-products-v1.6.0.md`.\n\nNajnowsza poprawka [`data-products-v1.6.1`](https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/data-products-v1.6.1) została opublikowana z dokładnego commita `4b77571c788b862a6543161b9343a35f464bd7c6`. Pole „Filtruj listę wyposażenia” rzeczywiście ukrywa niedopasowane nazwy, wybrane pozycje pozostają aktywne do jawnego usunięcia, a lista oferuje wyłącznie źródłowo kompletne dodatki zgodne z bieżącym wyborem. Alternatywy wzajemnie się wykluczające są ukrywane, natomiast braki danych o opcjach innych modeli nadal pozostają niewiadomą. Trwały zapis publikacji znajduje się w `project/releases/data-products-v1.6.1.md`, a opis poprawki w `project/packages/equipment-facet-interaction-fix.md`."
replace_once("README.md", old_release_paragraph, new_release_paragraph)

changelog_anchor = "* Fixed equipment-facet interaction: list search now visibly filters entries, selected equipment is never removed automatically, and only source-complete compatible additions remain selectable."
changelog_bullet = "* Published and independently re-verified patch release `data-products-v1.6.1` from exact main commit `4b77571c788b862a6543161b9343a35f464bd7c6`, preserving selected equipment, making list search visible and hiding only incompatible or source-incomplete additions without changing catalogue data."
replace_once("CHANGELOG.md", changelog_anchor, changelog_anchor + "\n" + changelog_bullet)

roadmap_anchor = "- publiczne wydanie `data-products-v1.6.0` z trzema niezależnie zweryfikowanymi assetami, dokładnym powiązaniem tagu z zielonym commitem i audytem opublikowanego HTML,"
roadmap_line = "- poprawka `data-products-v1.6.1` naprawiająca widoczne wyszukiwanie wyposażenia, zachowanie zaznaczeń i kompatybilne fasety, z niezależną weryfikacją publicznych assetów oraz dokładnego HTML,"
replace_once("project/ROADMAP.md", roadmap_anchor, roadmap_anchor + "\n" + roadmap_line)

package_path = Path("project/packages/equipment-facet-interaction-fix.md")
package_text = package_path.read_text(encoding="utf-8")
publication_section = """

## Publication

`data-products-v1.6.1` was published from exact squash-merged `main` commit `4b77571c788b862a6543161b9343a35f464bd7c6`. The public assets were downloaded again and independently verified. The exact published HTML contains the visible-search `hidden` override, explicit `selection_conflict` and `addable_equipment` contracts, and no longer contains the legacy automatic-selection removal path.
"""
if "## Publication" not in package_text:
    package_path.write_text(package_text.rstrip() + publication_section, encoding="utf-8")
else:
    raise SystemExit("publication section already exists")

state_path = Path("project/state.json")
state = json.loads(state_path.read_text(encoding="utf-8"))
state["updated_on"] = "2026-07-24"
state["phase"] = "Data Products v1.6.1 Publication"
state["reference_delivery"] = {
    "name": "Equipment Facet Interaction Fix",
    "pull_request": 236,
    "head_sha": HEAD_SHA,
    "quality_run": 1275,
}
state["current_package"] = {
    "name": "Data Products v1.6.1 Publication",
    "status": "complete",
    "goal": "Publish and independently re-verify immutable data-products-v1.6.1 assets from exact green main commit 4b77571c788b862a6543161b9343a35f464bd7c6 after the equipment-facet interaction fix.",
}
state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

release_dir = Path("project/releases")
release_dir.mkdir(parents=True, exist_ok=True)
audit = {
    "release_id": 359532111,
    "tag": "data-products-v1.6.1",
    "target_commit_sha": SOURCE_SHA,
    "target_commitish": SOURCE_SHA,
    "published_at": "2026-07-24T20:30:34Z",
    "html_url": "https://github.com/xbodzio7/Dacia-Knowledge-Base/releases/tag/data-products-v1.6.1",
    "draft": False,
    "prerelease": False,
    "assets": [
        {
            "name": "SHA256SUMS",
            "asset_id": 488795807,
            "size": 213,
            "sha256": "f8a402f879ab3410af5c2d1840ced4ab6abec517b7d344b6e248c27d6725821a",
            "api_digest": "sha256:f8a402f879ab3410af5c2d1840ced4ab6abec517b7d344b6e248c27d6725821a",
            "state": "uploaded",
        },
        {
            "name": "dacia-knowledge-base-data-products-v1.6.1.zip",
            "asset_id": 488795809,
            "size": 46477840,
            "sha256": "0dd8da53b5ccdb7030040c669d4f32ac80e6fa34ec6b1910d81af5c77d13359a",
            "api_digest": "sha256:0dd8da53b5ccdb7030040c669d4f32ac80e6fa34ec6b1910d81af5c77d13359a",
            "state": "uploaded",
        },
        {
            "name": "data-product-release-manifest.json",
            "asset_id": 488795810,
            "size": 19154,
            "sha256": "6f40676d3f8771f63b9240accc3bb73975b5f7d3da8f3cb233c737e0aa777d7f",
            "api_digest": "sha256:6f40676d3f8771f63b9240accc3bb73975b5f7d3da8f3cb233c737e0aa777d7f",
            "state": "uploaded",
        },
    ],
    "archive_member_count": 79,
    "browser": {
        "configuration_count": 69,
        "technical_comparison_facet_count": 88,
        "equipment_facet_count": 109,
        "official_model_media_count": 5,
        "contract_text_verified": [
            "Pokaż tylko różnice",
            "Filtruj listę wyposażenia",
            "Cena minimalna",
            "Cena maksymalna",
            "vehicle-photo-fallback",
            ".equipment-choice[hidden]{display:none!important}",
            "system nie odznacza filtrów automatycznie",
            "selection_conflict",
            "addable_equipment",
        ],
        "legacy_auto_removal_absent": [
            "setSelected(equipment, facetState.selected_equipment)",
            "removedCodes = state && Array.isArray(state.removed_equipment)",
        ],
    },
    "verification": "PASS",
}
(release_dir / "data-products-v1.6.1-publication-audit.json").write_text(
    json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)

release_md = """# Data Products v1.6.1 Publication

Date: 2026-07-24

## Published identity

- GitHub Release: `data-products-v1.6.1`
- Release ID: `359532111`
- Published at: `2026-07-24T20:30:34Z`
- Exact tag target and source commit: `4b77571c788b862a6543161b9343a35f464bd7c6`
- Source Pull Request: `#236`
- Verified Pull Request head: `8dce2a3f6ccbeb563fb9532c7b86c36d294735bf`
- Quality workflow: `#1275`

The tag resolves exactly to the squash-merged `main` commit above. The release is final, not a draft and not a prerelease.

## Public assets

| Asset | Asset ID | Size | SHA-256 |
| --- | ---: | ---: | --- |
| `SHA256SUMS` | `488795807` | 213 bytes | `f8a402f879ab3410af5c2d1840ced4ab6abec517b7d344b6e248c27d6725821a` |
| `dacia-knowledge-base-data-products-v1.6.1.zip` | `488795809` | 46,477,840 bytes | `0dd8da53b5ccdb7030040c669d4f32ac80e6fa34ec6b1910d81af5c77d13359a` |
| `data-product-release-manifest.json` | `488795810` | 19,154 bytes | `6f40676d3f8771f63b9240accc3bb73975b5f7d3da8f3cb233c737e0aa777d7f` |

GitHub's recorded API digests match the independently calculated SHA-256 values for all three downloaded assets.

## Release contents

- 69 active configurations;
- 18 independent comparison scopes;
- 79 deterministic archive members;
- 88 source-backed technical comparison facets;
- 109 equipment facets;
- five official Dacia Polska model-media entries with offline SVG fallbacks;
- equipment-list search that visibly hides non-matching entries;
- selected equipment preserved until explicit user removal;
- only source-complete compatible additions exposed after each selection;
- mutually exclusive alternatives hidden while the active choice remains selected;
- incomplete cross-model option data preserved as unknown rather than unavailable.

## Published-browser audit

The exact `shortlist/configuration-shortlist.html` member extracted from the public release archive was audited after re-downloading the asset from GitHub Release. The embedded catalogue still contains 69 configurations, 88 technical comparison facets, 109 equipment facets and five official model-media entries.

The audit confirmed the `hidden` CSS override used by equipment search, the `selection_conflict` and `addable_equipment` contracts, and the user-facing statement that the system does not deselect filters automatically. It also proved that the previous automatic-selection removal calls are absent from the published HTML.

## Verification

All 15 source Pull Request workflows passed on the final source head, including 719 tests, Windows, HTML, workbook, comparison, selection-export and versioned-release verification.

The public assets were then downloaded again from the published GitHub Release and accepted by `data-product-release --verify`. Exact sizes, SHA-256 values, GitHub API digests, tag target, release status, archive membership and published browser payload were independently audited. Publication audit result: `PASS`.

## Data boundary

This patch changes browser interaction only. It does not add, infer or reclassify Duster, Jogger, Sandero, Sandero Stepway or Bigster options. Missing cross-model option records remain unknown until a separate official-configurator source import proves their status.

## Immutability

The release assets and tag are immutable. Later corrections or source-backed data extensions must use a new semantic version and must not replace or rewrite `data-products-v1.6.1`.
"""
(release_dir / "data-products-v1.6.1.md").write_text(release_md, encoding="utf-8")
