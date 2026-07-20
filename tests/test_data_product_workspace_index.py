from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))

from data_product_workspace_fixture import (  # type: ignore[import-not-found]  # noqa: E402
    CONFIGURATION_CODES,
    SCOPE_NAMES,
    create_workspace_payload,
)
from reporting.data_product_release_model import (  # noqa: E402
    CHECKSUMS_NAME,
    MANIFEST_NAME,
    archive_name,
    file_record,
    json_text,
    release_tag,
    write_text,
)
from reporting.data_product_workspace_index import (  # noqa: E402
    INDEX_NAME,
    WorkspaceIndexError,
    render_workspace_index,
    write_workspace_index,
)

VERSION = "1.2.3"
COMMIT_SHA = "1" * 40
TAG = release_tag(VERSION)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.external_sources: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        values = dict(attrs)
        href = values.get("href")
        if href:
            self.hrefs.append(href)
        for attribute in ("src", "action"):
            value = values.get(attribute)
            if value and value.startswith(("http://", "https://", "//")):
                self.external_sources.append(value)


class DataProductWorkspaceIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.workspace = self.root / "workspace"
        self.assets = self.workspace / "assets"
        self.contents = self.workspace / "contents"
        self.assets.mkdir(parents=True)
        self.bundle = create_workspace_payload(self.contents)

        archive_path = self.assets / archive_name(VERSION)
        archive_path.write_bytes(b"fixture-archive")
        write_text(self.assets / MANIFEST_NAME, "{}\n")
        write_text(self.assets / CHECKSUMS_NAME, "fixture checksums\n")
        files = [
            file_record(path, self.contents)
            for path in sorted(
                self.contents.rglob("*"),
                key=lambda item: item.relative_to(self.contents).as_posix(),
            )
            if path.is_file()
        ]
        self.manifest: dict[str, object] = {
            "schema_version": 1,
            "release_version": VERSION,
            "release_tag": TAG,
            "repository_commit": COMMIT_SHA,
            "snapshot_date": "2026-06-26",
            "selected_configuration_count": 53,
            "scope_group_count": 13,
            "comparable_scope_count": 1,
            "singleton_scope_count": 12,
            "cross_scope_pairs_generated": False,
            "ranking_generated": False,
            "recommendations_generated": False,
            "inferred_values_generated": False,
            "archive": file_record(archive_path, self.assets),
            "files": files,
        }
        self.metadata = {
            "release_version": VERSION,
            "release_tag": TAG,
            "repository_commit": COMMIT_SHA,
            "release_id": 123,
            "release_url": (
                "https://github.com/xbodzio7/Dacia-Knowledge-Base/"
                f"releases/tag/{TAG}"
            ),
            "published_at": "2026-07-20T00:00:00Z",
        }

    @property
    def bundle_path(self) -> Path:
        return (
            self.contents
            / "comparison-bundle/comparison-bundle-manifest.json"
        )

    def _write_bundle(self, value: dict[str, object]) -> None:
        write_text(self.bundle_path, json_text(value))

    def _add_release_member(self, path: Path) -> None:
        records = self.manifest["files"]
        assert isinstance(records, list)
        records.append(file_record(path, self.contents))
        records.sort(key=lambda item: item["path"])

    def test_renders_deterministic_primary_scope_and_asset_navigation(self) -> None:
        first = render_workspace_index(
            self.workspace,
            self.manifest,
            self.metadata,
        )
        second = render_workspace_index(
            self.workspace,
            copy.deepcopy(self.manifest),
            copy.deepcopy(self.metadata),
        )

        self.assertEqual(first, second)
        self.assertTrue(first.startswith("<!doctype html>\n"))
        self.assertEqual(first.count('class="product-card"'), 4)
        self.assertEqual(first.count('class="scope-card"'), 13)
        self.assertEqual(first.count('class="badge comparable"'), 1)
        self.assertEqual(first.count('class="badge singleton"'), 12)
        self.assertIn("Configuration shortlist", first)
        self.assertIn("Comparison workbook", first)
        self.assertIn("Original release archive", first)
        self.assertIn(SCOPE_NAMES[0], first)
        self.assertIn("820", first)
        self.assertIn("17", first)
        self.assertNotIn("<script", first.lower())
        self.assertNotIn("generated at", first.lower())
        self.assertNotIn(str(self.workspace), first)

    def test_escapes_values_and_percent_encodes_local_paths(self) -> None:
        bundle = copy.deepcopy(self.bundle)
        groups = bundle["groups"]
        assert isinstance(groups, list)
        first_group = groups[0]
        assert isinstance(first_group, dict)
        codes = first_group["configuration_codes"]
        assert isinstance(codes, list)
        old_code = codes[0]
        codes[0] = "fixture_<danger>&_code"
        selected = bundle["selected_configuration_codes"]
        assert isinstance(selected, list)
        selected[selected.index(old_code)] = codes[0]

        report = (
            self.contents
            / "comparison-bundle/reports/space name & report.html"
        )
        write_text(report, "<!doctype html><title>Encoded path</title>\n")
        self._add_release_member(report)
        files = first_group["files"]
        assert isinstance(files, dict)
        files["html"] = file_record(
            report,
            self.contents / "comparison-bundle",
        )
        self._write_bundle(bundle)

        rendered = render_workspace_index(
            self.workspace,
            self.manifest,
            self.metadata,
        )

        self.assertIn("fixture_&lt;danger&gt;&amp;_code", rendered)
        self.assertNotIn("fixture_<danger>&_code", rendered)
        self.assertIn(
            "contents/comparison-bundle/reports/space%20name%20%26%20report.html",
            rendered,
        )

    def test_rejects_invalid_bundle_counts_and_statuses(self) -> None:
        cases: list[tuple[str, dict[str, object]]] = []
        wrong_count = copy.deepcopy(self.bundle)
        wrong_count["scope_group_count"] = 12
        cases.append(("scope_group_count", wrong_count))

        wrong_comparable = copy.deepcopy(self.bundle)
        wrong_comparable["comparable_scope_count"] = 2
        cases.append(("comparable_scope_count", wrong_comparable))

        wrong_status = copy.deepcopy(self.bundle)
        groups = wrong_status["groups"]
        assert isinstance(groups, list)
        assert isinstance(groups[0], dict)
        groups[0]["status"] = "unknown"
        cases.append(("status", wrong_status))

        cross_scope = copy.deepcopy(self.bundle)
        cross_scope["cross_scope_pairs_generated"] = True
        cases.append(("cross-scope", cross_scope))

        for label, bundle in cases:
            with self.subTest(label=label):
                self._write_bundle(bundle)
                with self.assertRaises(WorkspaceIndexError):
                    render_workspace_index(
                        self.workspace,
                        self.manifest,
                        self.metadata,
                    )

    def test_rejects_unsafe_or_missing_report_paths(self) -> None:
        unsafe = copy.deepcopy(self.bundle)
        groups = unsafe["groups"]
        assert isinstance(groups, list)
        assert isinstance(groups[0], dict)
        files = groups[0]["files"]
        assert isinstance(files, dict)
        assert isinstance(files["html"], dict)
        files["html"]["path"] = "../escape.html"
        self._write_bundle(unsafe)
        with self.assertRaisesRegex(WorkspaceIndexError, "unsafe"):
            render_workspace_index(
                self.workspace,
                self.manifest,
                self.metadata,
            )

        missing = copy.deepcopy(self.bundle)
        groups = missing["groups"]
        assert isinstance(groups, list)
        assert isinstance(groups[0], dict)
        files = groups[0]["files"]
        assert isinstance(files, dict)
        assert isinstance(files["html"], dict)
        files["html"]["path"] = "missing/report.html"
        self._write_bundle(missing)
        with self.assertRaisesRegex(WorkspaceIndexError, "verified release"):
            render_workspace_index(
                self.workspace,
                self.manifest,
                self.metadata,
            )

    def test_rejects_release_identity_and_inventory_mismatches(self) -> None:
        wrong_tag = dict(self.metadata)
        wrong_tag["release_tag"] = "data-products-v9.9.9"
        with self.assertRaisesRegex(WorkspaceIndexError, "tag"):
            render_workspace_index(
                self.workspace,
                self.manifest,
                wrong_tag,
            )

        wrong_commit = dict(self.metadata)
        wrong_commit["repository_commit"] = "2" * 40
        with self.assertRaisesRegex(WorkspaceIndexError, "commit"):
            render_workspace_index(
                self.workspace,
                self.manifest,
                wrong_commit,
            )

        wrong_count = dict(self.manifest)
        wrong_count["selected_configuration_count"] = 52
        with self.assertRaisesRegex(WorkspaceIndexError, "configuration counts"):
            render_workspace_index(
                self.workspace,
                wrong_count,
                self.metadata,
            )

    def test_all_local_hrefs_exist_and_no_external_dependencies_exist(self) -> None:
        rendered = render_workspace_index(
            self.workspace,
            self.manifest,
            self.metadata,
        )
        parser = LinkParser()
        parser.feed(rendered)

        release_urls = [
            href for href in parser.hrefs if href.startswith("https://")
        ]
        local_urls = [
            href for href in parser.hrefs if not href.startswith("https://")
        ]
        self.assertEqual(release_urls, [self.metadata["release_url"]])
        self.assertEqual(parser.external_sources, [])
        self.assertGreater(len(local_urls), 10)
        for href in local_urls:
            target = self.workspace.joinpath(
                *Path(unquote(href)).parts
            )
            self.assertTrue(target.is_file(), href)

    def test_write_workspace_index_matches_renderer_bytes(self) -> None:
        expected = render_workspace_index(
            self.workspace,
            self.manifest,
            self.metadata,
        )
        output = write_workspace_index(
            self.workspace,
            self.manifest,
            self.metadata,
        )
        self.assertEqual(output, self.workspace / INDEX_NAME)
        self.assertEqual(output.read_bytes(), expected.encode("utf-8"))

    def test_workflow_compares_linux_and_windows_index_bytes(self) -> None:
        workflow = (
            REPOSITORY
            / ".github/workflows/data-product-workspace-index.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("contents: read", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertIn("ubuntu-latest", workflow)
        self.assertIn("windows-latest", workflow)
        self.assertIn("data-product-release-download", workflow)
        self.assertIn("index.html", workflow)
        self.assertIn("compare", workflow.lower())
        self.assertIn("download-artifact", workflow)


if __name__ == "__main__":
    unittest.main()
