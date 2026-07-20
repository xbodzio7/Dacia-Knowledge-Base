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


def patch_downloader() -> None:
    path = ROOT / "tools/reporting/data_product_release_download.py"
    anchor = '''from reporting.data_product_release_model import (
    CHECKSUMS_NAME,
    MANIFEST_NAME,
    ReleaseError,
    archive_name,
    normalize_commit_sha,
    normalize_version,
    release_tag,
    safe_member_name,
    verify_release_assets,
)
'''
    replacement = anchor + '''from reporting.data_product_workspace_index import (
    INDEX_NAME,
    write_workspace_index,
)
'''
    replace_once(path, anchor, replacement)

    old = '''        entry_points = _extract_verified_contents(
            assets_directory,
            contents_directory,
            manifest,
        )
        result = {
            "release_version": normalized_version,
            "release_tag": release_tag(normalized_version),
            "repository_commit": tag_commit,
            "release_id": release.get("id"),
            "release_url": release.get("html_url"),
            "published_at": release.get("published_at"),
            "selected_configuration_count": manifest.get(
                "selected_configuration_count"
            ),
            "scope_group_count": manifest.get("scope_group_count"),
            "assets_directory": ASSETS_DIRECTORY_NAME,
            "contents_directory": CONTENTS_DIRECTORY_NAME,
            "entry_points": entry_points,
        }
'''
    new = '''        entry_points = _extract_verified_contents(
            assets_directory,
            contents_directory,
            manifest,
        )
        release_metadata = {
            "release_version": normalized_version,
            "release_tag": release_tag(normalized_version),
            "repository_commit": tag_commit,
            "release_id": release.get("id"),
            "release_url": release.get("html_url"),
            "published_at": release.get("published_at"),
        }
        index_path = write_workspace_index(
            build_root,
            manifest,
            release_metadata,
        )
        entry_points = {
            "workspace_index": index_path.relative_to(build_root).as_posix(),
            **entry_points,
        }
        result = {
            **release_metadata,
            "selected_configuration_count": manifest.get(
                "selected_configuration_count"
            ),
            "scope_group_count": manifest.get("scope_group_count"),
            "assets_directory": ASSETS_DIRECTORY_NAME,
            "contents_directory": CONTENTS_DIRECTORY_NAME,
            "entry_points": entry_points,
        }
'''
    replace_once(path, old, new)


def patch_cli() -> None:
    path = ROOT / "tools/data_product_release_download.py"
    old_labels = '''    labels = {
        "shortlist_html": "Shortlist HTML",
        "comparison_workbook": "Comparison workbook",
        "comparison_bundle_manifest": "Bundle manifest",
        "release_notes": "Release notes",
    }
    for key in (
        "shortlist_html",
        "comparison_workbook",
        "comparison_bundle_manifest",
        "release_notes",
    ):
'''
    new_labels = '''    labels = {
        "workspace_index": "Workspace index",
        "shortlist_html": "Shortlist HTML",
        "comparison_workbook": "Comparison workbook",
        "comparison_bundle_manifest": "Bundle manifest",
        "release_notes": "Release notes",
    }
    for key in (
        "workspace_index",
        "shortlist_html",
        "comparison_workbook",
        "comparison_bundle_manifest",
        "release_notes",
    ):
'''
    replace_once(path, old_labels, new_labels)


def patch_renderer() -> None:
    path = ROOT / "tools/reporting/data_product_workspace_index.py"
    anchor = '''    scopes = _scope_records(
        workspace_root,
        release_members,
        bundle,
    )
    primary_links = _primary_links(
'''
    replacement = '''    scopes = _scope_records(
        workspace_root,
        release_members,
        bundle,
    )
    selected_codes = _configuration_codes(
        bundle.get("selected_configuration_codes"),
        "comparison bundle selected_configuration_codes",
    )
    if len(selected_codes) != bundle_configuration_count:
        raise WorkspaceIndexError(
            "comparison bundle selected configuration count does not match codes"
        )
    grouped_codes = tuple(
        code
        for scope in scopes
        for code in scope["configuration_codes"]
    )
    if len(grouped_codes) != len(set(grouped_codes)):
        raise WorkspaceIndexError(
            "comparison bundle configuration codes overlap between scopes"
        )
    if set(grouped_codes) != set(selected_codes):
        raise WorkspaceIndexError(
            "comparison bundle selected configuration codes do not match groups"
        )
    primary_links = _primary_links(
'''
    replace_once(path, anchor, replacement)


def patch_downloader_tests() -> None:
    path = ROOT / "tests/test_data_product_release_download.py"
    import_anchor = '''import dkb  # noqa: E402
from reporting.data_product_release_download import (  # noqa: E402
'''
    import_replacement = '''import dkb  # noqa: E402
from tests.data_product_workspace_fixture import (  # noqa: E402
    create_workspace_payload,
)
from reporting.data_product_release_download import (  # noqa: E402
'''
    replace_once(path, import_anchor, import_replacement)

    old_payload = '''        payload = self.root / "payload"
        for relative_name in ENTRY_POINTS.values():
            write_text(payload / relative_name, f"fixture:{relative_name}\n")
        archive_path = self.fixture / ARCHIVE_NAME
'''
    new_payload = '''        payload = self.root / "payload"
        create_workspace_payload(payload)
        archive_path = self.fixture / ARCHIVE_NAME
'''
    replace_once(path, old_payload, new_payload)

    old_entries = '''        self.assertEqual(
            set(result["entry_points"]),
            set(ENTRY_POINTS),
        )
        for key, relative_name in ENTRY_POINTS.items():
'''
    new_entries = '''        self.assertEqual(
            set(result["entry_points"]),
            set(ENTRY_POINTS) | {"workspace_index"},
        )
        self.assertEqual(result["entry_points"]["workspace_index"], "index.html")
        self.assertTrue((output / "index.html").is_file())
        for key, relative_name in ENTRY_POINTS.items():
'''
    replace_once(path, old_entries, new_entries)

    replace_once(
        path,
        '''            ["assets", "contents"],
''',
        '''            ["assets", "contents", "index.html"],
''',
    )

    old_mock_entries = '''            "entry_points": {
                key: (Path("contents") / relative).as_posix()
                for key, relative in ENTRY_POINTS.items()
            },
'''
    new_mock_entries = '''            "entry_points": {
                "workspace_index": "index.html",
                **{
                    key: (Path("contents") / relative).as_posix()
                    for key, relative in ENTRY_POINTS.items()
                },
            },
'''
    replace_once(path, old_mock_entries, new_mock_entries)

    replace_once(
        path,
        '''        self.assertIn("Shortlist HTML", rendered)
''',
        '''        self.assertIn("Workspace index", rendered)
        self.assertIn("Shortlist HTML", rendered)
''',
    )

    transaction_anchor = '''    def test_nonempty_output_is_not_overwritten(self) -> None:
'''
    transaction_test = '''    def test_workspace_index_failure_is_transactional(self) -> None:
        output = self.root / "download"
        with mock.patch(
            "reporting.data_product_release_download.write_workspace_index",
            side_effect=ReleaseDownloadError("fixture index failure"),
        ):
            with self.assertRaisesRegex(
                ReleaseDownloadError,
                "fixture index failure",
            ):
                download_release(
                    VERSION,
                    output,
                    token="",
                    opener=FakeOpener(self._payloads()),
                )
        self.assertFalse(output.exists())
        self.assertEqual(
            [path for path in self.root.iterdir() if ".download-" in path.name],
            [],
        )

'''
    replace_once(path, transaction_anchor, transaction_test + transaction_anchor)


def patch_workspace_tests() -> None:
    path = ROOT / "tests/test_data_product_workspace_index.py"
    replace_once(
        path,
        '''from data_product_workspace_fixture import (  # type: ignore[import-not-found]  # noqa: E402
''',
        '''from tests.data_product_workspace_fixture import (  # noqa: E402
''',
    )


def patch_docs() -> None:
    readme = ROOT / "README.md"
    old = '''Komenda wymaga jawnej, niezmiennej wersji. Sprawdza tag GitHub, dokładny zestaw
trzech assetów, manifest, `SHA256SUMS`, każdy element archiwum i powiązanie z
commitem źródłowym. Po sukcesie wskazuje gotowe do otwarcia: interaktywną
shortlistę HTML, skoroszyt XLSX porównań, manifest pakietu i notatki wydania.
'''
    new = '''Komenda wymaga jawnej, niezmiennej wersji. Sprawdza tag GitHub, dokładny zestaw
trzech assetów, manifest, `SHA256SUMS`, każdy element archiwum i powiązanie z
commitem źródłowym. Po sukcesie tworzy deterministyczny `index.html` jako główną
stronę startową oraz wskazuje bezpośrednio interaktywną shortlistę HTML,
skoroszyt XLSX porównań, manifest pakietu i notatki wydania.
'''
    replace_once(readme, old, new)

    old_release = '''Szczegóły opisuje `project/packages/verified-data-product-release-download-cli.md`.
'''
    new_release = '''Szczegóły opisuje `project/packages/verified-data-product-release-download-cli.md`.
Lokalny `index.html` łączy wszystkie podstawowe produkty, 13 zakresów porównań
i trzy oryginalne assety proweniencji bez JavaScriptu i zasobów zewnętrznych.
'''
    replace_once(readme, old_release, new_release)

    changelog = ROOT / "CHANGELOG.md"
    anchor = "### Added\n\n"
    addition = (
        "* Deterministic offline `index.html` for verified local data-product "
        "workspaces, linking primary products, all comparison scopes and release provenance.\n"
        "* Byte-identical Linux/Windows workspace index validation against the public `data-products-v1.0.0` release.\n"
    )
    replace_once(changelog, anchor, anchor + addition)

    roadmap = ROOT / "project/ROADMAP.md"
    roadmap_anchor = "- zweryfikowane pobieranie i bezpieczne rozpakowanie jawnej wersji publicznego wydania do lokalnego workspace,\n"
    roadmap_addition = "- deterministyczna lokalna strona startowa HTML łącząca produkty, zakresy porównań i proweniencję wydania,\n"
    replace_once(roadmap, roadmap_anchor, roadmap_anchor + roadmap_addition)


def write_package_doc() -> None:
    path = ROOT / "project/packages/local-data-product-workspace-index-html.md"
    content = '''# Local Data Product Workspace Index HTML

## Status

Implementation package for the `Data Product Utilization` phase.

## Goal

Create one deterministic offline landing page for every workspace produced by `data-product-release-download`, without changing the immutable public release or source data.

## Output

After all three public assets are downloaded, verified and safely extracted, the downloader writes `index.html` at the workspace root before the final atomic directory rename. The CLI reports this page as the first entry point.

## Inputs and boundaries

The renderer reads only verified release metadata, the external release manifest and `contents/comparison-bundle/comparison-bundle-manifest.json`. It does not open individual comparison values, rank configurations, recommend products, infer missing observations or create cross-scope comparisons.

## Page contract

The page is self-contained, contains embedded CSS, no JavaScript and no external runtime resources. For the same verified release it produces identical UTF-8 bytes on Linux and Windows. It contains no generation time, hostname, absolute path or random identifier.

It presents:

- release version, tag, commit, snapshot date, configuration and scope counts,
- a canonical link to the public GitHub Release,
- primary cards for shortlist HTML, the comparison workbook, bundle manifest and release notes,
- one ordered card for every comparable or singleton scope,
- source-backed pair, difference and artifact counts from the bundle manifest,
- available JSON, Markdown, CSV and HTML scope reports,
- links to the original ZIP, external manifest and `SHA256SUMS` under `assets/`.

Every local path must be normalized, present in the verified release inventory and exist on disk. Rendered text is HTML-escaped and each relative URL segment is percent-encoded. A malformed manifest, overlapping scope membership, identity mismatch, missing target or unsafe path fails the whole transactional download.

## Validation

A shared synthetic fixture models 53 configurations across 13 independent scopes with one comparable scope and 12 singletons. Regression tests cover deterministic rendering, primary and provenance navigation, scope states, escaping, URL encoding, count and identity mismatches, unsafe or missing paths, local target existence, write parity, downloader cleanup and workflow permissions.

The read-only `Local Data Product Workspace Index` workflow downloads public `data-products-v1.0.0` on Linux and Windows, validates every local link and offline dependency rule, uploads both index files and requires byte-identical output in a separate comparison job.

## Non-goals

- changing or republishing `data-products-v1.0.0`,
- adding a mutable latest alias,
- launching a local server or browser automatically,
- adding JavaScript, external styles or fonts,
- expanding source data.
'''
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="")


def patch_state() -> None:
    state_path = ROOT / "project/state.json"
    summary_path = ROOT / "project/STATE_SUMMARY.md"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-20"
    state["reference_delivery"] = {
        "name": "Local Data Product Workspace Index Planning Review",
        "pull_request": 163,
        "head_sha": "13bb769a37a41a16a1589b19094c1d2588b03d35",
        "quality_run": 872,
    }
    state["baseline"]["tests"] = 676
    state["current_package"] = {
        "name": "Local Data Product Workspace Index HTML",
        "status": "complete",
        "goal": (
            "Generate one deterministic offline index.html after verified release "
            "extraction, linking primary products, every comparison scope and "
            "release provenance with safe relative paths."
        ),
    }
    state["next_package"] = {
        "name": "Data Product Utilization Milestone Review",
        "status": "planned",
        "goal": (
            "Review the complete public release, verified download and offline "
            "workspace flow, then select the next highest-value utilization "
            "package without expanding source data."
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


def patch_baseline_expectations() -> None:
    for relative in (
        "tests/test_jogger_payload_performance_ranges.py",
        "tests/test_jogger_wltp_efficiency_ranges.py",
    ):
        path = ROOT / relative
        replace_once(
            path,
            'self.assertEqual(baseline["tests"], 667)',
            'self.assertEqual(baseline["tests"], 676)',
        )


def main() -> int:
    patch_downloader()
    patch_cli()
    patch_renderer()
    patch_downloader_tests()
    patch_workspace_tests()
    patch_docs()
    write_package_doc()
    patch_state()
    patch_baseline_expectations()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
