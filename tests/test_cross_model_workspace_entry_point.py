from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TESTS = ROOT / "tests"
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(TOOLS))

from data_product_workspace_fixture import create_workspace_payload  # noqa: E402
from reporting.data_product_release_model import (  # noqa: E402
    CHECKSUMS_NAME,
    MANIFEST_NAME,
    archive_name,
    file_record,
    write_text,
)
from reporting.data_product_workspace_index import (  # noqa: E402
    CROSS_MODEL_HTML_MEMBER,
    WorkspaceIndexError,
    render_workspace_index,
)

REPORT = ROOT / "data/reporting/cross_model_workspace_entry_point.json"
REVIEW = ROOT / "data/reporting/cross_model_navigation_usability_review.json"
AUDIT = ROOT / "data/reporting/data_products_v1_8_1_publication_audit.json"
STATE = ROOT / "project/state.json"
VERIFIER = ROOT / "tools/review_cross_model_workspace_entry_point_20260727.py"
WORKFLOW = ROOT / ".github/workflows/data-product-release-download.yml"
VERSION = "1.2.3"
COMMIT = "1" * 40


class Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        href = dict(attrs).get("href")
        if href:
            self.hrefs.append(href)


class CrossModelWorkspaceEntryPointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def fixture(
        self,
        *,
        cross_model: bool,
    ) -> tuple[
        Path,
        dict[str, object],
        dict[str, object],
        tempfile.TemporaryDirectory[str],
    ]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name) / "workspace"
        assets = root / "assets"
        contents = root / "contents"
        assets.mkdir(parents=True)
        create_workspace_payload(contents)
        archive = assets / archive_name(VERSION)
        archive.write_bytes(b"fixture")
        write_text(assets / MANIFEST_NAME, "{}\n")
        write_text(assets / CHECKSUMS_NAME, "fixture\n")
        if cross_model:
            write_text(
                contents / CROSS_MODEL_HTML_MEMBER,
                "<!doctype html><title>Models</title>\n",
            )
        files = [
            file_record(path, contents)
            for path in sorted(contents.rglob("*"))
            if path.is_file()
        ]
        manifest: dict[str, object] = {
            "release_version": VERSION,
            "release_tag": "data-products-v1.2.3",
            "repository_commit": COMMIT,
            "snapshot_date": "2026-06-26",
            "selected_configuration_count": 53,
            "scope_group_count": 13,
            "archive": file_record(archive, assets),
            "files": files,
        }
        metadata: dict[str, object] = {
            "release_tag": "data-products-v1.2.3",
            "repository_commit": COMMIT,
            "release_url": (
                "https://github.com/xbodzio7/Dacia-Knowledge-Base/"
                "releases/tag/data-products-v1.2.3"
            ),
        }
        return root, manifest, metadata, temporary

    def test_metadata_and_review_selection_are_exact(self) -> None:
        self.assertEqual(
            self.report["kind"],
            "cross_model_workspace_entry_point",
        )
        self.assertEqual(self.report["status"], "complete")
        self.assertEqual(self.report["source_review"]["pull_request"], 295)
        self.assertEqual(
            self.report["source_review"]["merge_commit"],
            "2ca040708e9f8bba92abe70693395c6a5447252f",
        )
        review = json.loads(REVIEW.read_text(encoding="utf-8"))
        self.assertEqual(
            review["selection"]["code"],
            "conditional_primary_cross_model_card",
        )

    def test_member_absent_release_keeps_four_primary_cards(self) -> None:
        root, manifest, metadata, temporary = self.fixture(cross_model=False)
        self.addCleanup(temporary.cleanup)
        rendered = render_workspace_index(root, manifest, metadata)
        self.assertEqual(rendered.count('class="product-card"'), 4)
        self.assertNotIn("Models and comparison scopes", rendered)

    def test_verified_member_adds_exact_fifth_card(self) -> None:
        root, manifest, metadata, temporary = self.fixture(cross_model=True)
        self.addCleanup(temporary.cleanup)
        rendered = render_workspace_index(root, manifest, metadata)
        self.assertEqual(rendered.count('class="product-card"'), 5)
        self.assertIn("Models and comparison scopes", rendered)
        self.assertIn(
            'href="contents/cross-model/cross-model-comparison-view.html"',
            rendered,
        )

    def test_declared_member_without_local_file_is_rejected(self) -> None:
        root, manifest, metadata, temporary = self.fixture(cross_model=False)
        self.addCleanup(temporary.cleanup)
        records = manifest["files"]
        assert isinstance(records, list)
        records.append(
            {
                "path": CROSS_MODEL_HTML_MEMBER,
                "size_bytes": 1,
                "sha256": "0" * 64,
            }
        )
        with self.assertRaisesRegex(
            WorkspaceIndexError,
            "cross-model comparison HTML is missing",
        ):
            render_workspace_index(root, manifest, metadata)

    def test_all_member_present_local_links_are_safe_and_exist(self) -> None:
        root, manifest, metadata, temporary = self.fixture(cross_model=True)
        self.addCleanup(temporary.cleanup)
        parser = Parser()
        parser.feed(render_workspace_index(root, manifest, metadata))
        local = [
            href
            for href in parser.hrefs
            if not href.startswith("https://")
        ]
        self.assertIn(
            "contents/cross-model/cross-model-comparison-view.html",
            local,
        )
        for href in local:
            self.assertTrue(
                root.joinpath(*Path(unquote(href)).parts).is_file(),
                href,
            )

    def test_public_download_contract_targets_v1_8_1_and_84_links(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("--version 1.8.1", workflow)
        self.assertIn(
            "0b7009fd1950693e347638a6b96756aeefb43b8a",
            workflow,
        )
        self.assertIn("len(local)==84", workflow)
        self.assertIn("Models and comparison scopes", workflow)
        self.assertIn("compare-workspace-index", workflow)

    def test_historical_audit_and_boundaries_remain_immutable(self) -> None:
        audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        self.assertEqual(
            audit["workspace"]["index_local_link_count"],
            83,
        )
        self.assertFalse(
            self.report["compatibility"]["historical_audit_rewritten"]
        )
        self.assertTrue(
            all(
                value is False
                for value in self.report["semantic_boundaries"].values()
            )
        )

    def test_project_state_and_verifier_accept_completed_package(self) -> None:
        state = json.loads(STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["phase"], "Cross-Model Workspace Entry Point")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(
            state["next_package"]["name"],
            "Post-Cross-Model Workspace Priority Selection Review",
        )
        self.assertEqual(state["baseline"]["tests"], 1070)
        completed = subprocess.run(
            [sys.executable, str(VERIFIER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            completed.stderr or completed.stdout,
        )
        self.assertIn(
            "PASS: Cross-Model Workspace Entry Point",
            completed.stdout,
        )


if __name__ == "__main__":
    unittest.main()
