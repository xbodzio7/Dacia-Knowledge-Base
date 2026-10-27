from __future__ import annotations

import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
TESTS = REPOSITORY / "tests"
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(TOOLS))

import data_product_workspace_verify as cli  # noqa: E402
import dkb  # noqa: E402
from data_product_workspace_fixture import create_workspace_payload  # noqa: E402
from reporting.data_product_release_model import (  # noqa: E402
    CHECKSUMS_NAME,
    MANIFEST_NAME,
    RELEASE_SCHEMA_VERSION,
    archive_name,
    checksum_text,
    file_record,
    json_text,
    release_tag,
    sha256_file,
    write_deterministic_zip,
    write_text,
)
from reporting.data_product_workspace_index import write_workspace_index  # noqa: E402
from reporting.data_product_workspace_verify import (  # noqa: E402
    WorkspaceVerificationError,
    _verify_index_links,
    render_json,
    verify_workspace,
)

VERSION = "1.2.3"
TAG = release_tag(VERSION)
COMMIT_SHA = "1" * 40
RELEASE_URL = (
    "https://github.com/xbodzio7/Dacia-Knowledge-Base/"
    f"releases/tag/{TAG}"
)


def build_workspace(root: Path) -> Path:
    workspace = root / "workspace"
    assets = workspace / "assets"
    contents = workspace / "contents"
    assets.mkdir(parents=True)
    create_workspace_payload(contents)
    archive_path = assets / archive_name(VERSION)
    records = write_deterministic_zip(contents, archive_path)
    manifest = {
        "schema_version": RELEASE_SCHEMA_VERSION,
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
        "archive": file_record(archive_path, assets),
        "files": records,
    }
    manifest_path = assets / MANIFEST_NAME
    write_text(manifest_path, json_text(manifest))
    write_text(
        assets / CHECKSUMS_NAME,
        checksum_text(
            {
                archive_path.name: sha256_file(archive_path),
                MANIFEST_NAME: sha256_file(manifest_path),
            }
        ),
    )
    write_workspace_index(
        workspace,
        manifest,
        {
            "release_version": VERSION,
            "release_tag": TAG,
            "repository_commit": COMMIT_SHA,
            "release_url": RELEASE_URL,
        },
    )
    return workspace


def snapshot(root: Path) -> dict[str, bytes | None]:
    result: dict[str, bytes | None] = {}
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        result[relative] = path.read_bytes() if path.is_file() else None
    return result


class WorkspaceVerificationChecks(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.workspace = build_workspace(self.root)

    def test_valid_workspace_returns_deterministic_report(self) -> None:
        first = verify_workspace(self.workspace)
        second = verify_workspace(self.workspace)
        self.assertEqual(first, second)
        self.assertEqual(first["status"], "verified")
        self.assertEqual(first["release_version"], VERSION)
        self.assertEqual(first["asset_count"], 3)
        self.assertEqual(first["content_file_count"], 8)
        self.assertEqual(first["selected_configuration_count"], 53)
        self.assertEqual(first["scope_group_count"], 13)
        self.assertGreater(first["index_local_link_count"], 10)
        self.assertEqual(render_json(first), render_json(second))
        self.assertNotIn(str(self.workspace), render_json(first))

    def test_verification_is_read_only(self) -> None:
        before = snapshot(self.workspace)
        verify_workspace(self.workspace)
        self.assertEqual(snapshot(self.workspace), before)

    def test_rejects_changed_release_asset(self) -> None:
        archive = self.workspace / "assets" / archive_name(VERSION)
        archive.write_bytes(archive.read_bytes() + b"corruption")
        with self.assertRaisesRegex(WorkspaceVerificationError, "archive"):
            verify_workspace(self.workspace)

    def test_rejects_changed_extracted_content(self) -> None:
        target = self.workspace / "contents/RELEASE_NOTES.md"
        target.write_text("changed\n", encoding="utf-8")
        with self.assertRaisesRegex(WorkspaceVerificationError, "content"):
            verify_workspace(self.workspace)

    def test_rejects_missing_and_unexpected_content(self) -> None:
        missing_workspace = self.root / "missing"
        shutil.copytree(self.workspace, missing_workspace)
        (missing_workspace / "contents/RELEASE_NOTES.md").unlink()
        with self.assertRaisesRegex(WorkspaceVerificationError, "inventory"):
            verify_workspace(missing_workspace)

        extra_workspace = self.root / "extra"
        shutil.copytree(self.workspace, extra_workspace)
        write_text(extra_workspace / "contents/unexpected.txt", "extra\n")
        with self.assertRaisesRegex(WorkspaceVerificationError, "inventory"):
            verify_workspace(extra_workspace)

    def test_rejects_edited_index_and_top_level_entry(self) -> None:
        edited_workspace = self.root / "edited"
        shutil.copytree(self.workspace, edited_workspace)
        index = edited_workspace / "index.html"
        index.write_text(index.read_text(encoding="utf-8") + "<!-- edit -->", encoding="utf-8")
        with self.assertRaisesRegex(WorkspaceVerificationError, "index bytes"):
            verify_workspace(edited_workspace)

        top_level_workspace = self.root / "top-level"
        shutil.copytree(self.workspace, top_level_workspace)
        write_text(top_level_workspace / "extra.txt", "extra\n")
        with self.assertRaisesRegex(WorkspaceVerificationError, "top-level"):
            verify_workspace(top_level_workspace)

    def test_link_validator_rejects_escape_and_runtime_resource(self) -> None:
        with self.assertRaisesRegex(WorkspaceVerificationError, "unsafe local link"):
            _verify_index_links(
                self.workspace,
                '<a href="../escape.txt">escape</a>',
                RELEASE_URL,
            )
        with self.assertRaisesRegex(WorkspaceVerificationError, "runtime"):
            _verify_index_links(
                self.workspace,
                '<script src="https://example.com/app.js"></script>',
                RELEASE_URL,
            )

    def test_cli_human_json_and_error_output(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(
                cli.main(["--workspace-directory", str(self.workspace)]),
                0,
            )
        self.assertIn("Verified local data product workspace", stdout.getvalue())

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(
                cli.main(
                    [
                        "--workspace-directory",
                        str(self.workspace),
                        "--json",
                    ]
                ),
                0,
            )
        self.assertEqual(json.loads(stdout.getvalue())["status"], "verified")

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            self.assertEqual(
                cli.main(["--workspace-directory", str(self.root / "missing")]),
                1,
            )
        self.assertIn("error:", stderr.getvalue())

    def test_unified_cli_help_and_forwarding(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(dkb.main([]), 0)
        self.assertIn("data-product-workspace-verify", stdout.getvalue())

        completed = SimpleNamespace(returncode=23)
        with mock.patch.object(dkb.subprocess, "run", return_value=completed) as run:
            result = dkb.run_script(
                "data-product-workspace-verify",
                ["--workspace-directory", "workspace", "--json"],
            )
        self.assertEqual(result, 23)
        run.assert_called_once_with(
            [
                sys.executable,
                str(TOOLS / "data_product_workspace_verify.py"),
                "--workspace-directory",
                "workspace",
                "--json",
            ],
            check=False,
        )

    def test_release_download_workflow_validates_and_corrupts_copy(self) -> None:
        workflow = (
            REPOSITORY / ".github/workflows/data-product-release-download.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("data-product-workspace-verify", workflow)
        self.assertIn("corrupted-release", workflow)
        self.assertIn("contents: read", workflow)
        self.assertNotIn("contents: write", workflow)


if __name__ == "__main__":
    unittest.main()
