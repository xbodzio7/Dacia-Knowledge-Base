from __future__ import annotations

import io
import json
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

import data_product_release_download as cli  # noqa: E402
import dkb  # noqa: E402
from data_product_workspace_fixture import create_workspace_payload  # noqa: E402
from reporting.data_product_release_download import (  # noqa: E402
    API_ROOT,
    ENTRY_POINTS,
    REPOSITORY_FULL_NAME,
    ReleaseDownloadError,
    download_release,
)
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

VERSION = "1.2.3"
COMMIT_SHA = "1" * 40
TAG = release_tag(VERSION)
ARCHIVE_NAME = archive_name(VERSION)
RELEASE_API = f"{API_ROOT}/repos/{REPOSITORY_FULL_NAME}/releases/tags/{TAG}"
REF_API = f"{API_ROOT}/repos/{REPOSITORY_FULL_NAME}/git/ref/tags/{TAG}"
DOWNLOAD_PREFIX = (
    f"https://github.com/{REPOSITORY_FULL_NAME}/releases/download/{TAG}/"
)


class FakeResponse:
    def __init__(self, content: bytes) -> None:
        self.stream = io.BytesIO(content)

    def read(self, size: int = -1) -> bytes:
        return self.stream.read(size)

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None


class FakeOpener:
    def __init__(self, payloads: dict[str, bytes | Exception]) -> None:
        self.payloads = payloads
        self.requests: list[object] = []

    def __call__(self, request: object) -> FakeResponse:
        self.requests.append(request)
        url = request.full_url  # type: ignore[attr-defined]
        payload = self.payloads.get(url)
        if payload is None:
            raise AssertionError(f"unexpected request: {url}")
        if isinstance(payload, Exception):
            raise payload
        return FakeResponse(payload)


class DataProductReleaseDownloadTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.fixture = self.root / "fixture"
        self.fixture.mkdir()
        payload = self.root / "payload"
        create_workspace_payload(payload)
        archive_path = self.fixture / ARCHIVE_NAME
        files = write_deterministic_zip(payload, archive_path)
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
            "archive": file_record(archive_path, self.fixture),
            "files": files,
        }
        manifest_path = self.fixture / MANIFEST_NAME
        write_text(manifest_path, json_text(manifest))
        write_text(
            self.fixture / CHECKSUMS_NAME,
            checksum_text(
                {
                    ARCHIVE_NAME: sha256_file(archive_path),
                    MANIFEST_NAME: sha256_file(manifest_path),
                }
            ),
        )
        self.release = {
            "id": 123,
            "tag_name": TAG,
            "draft": False,
            "prerelease": False,
            "html_url": (
                f"https://github.com/{REPOSITORY_FULL_NAME}/releases/tag/{TAG}"
            ),
            "published_at": "2026-07-20T00:00:00Z",
            "assets": [
                {
                    "name": name,
                    "size": (self.fixture / name).stat().st_size,
                    "browser_download_url": DOWNLOAD_PREFIX + name,
                }
                for name in (MANIFEST_NAME, ARCHIVE_NAME, CHECKSUMS_NAME)
            ],
        }
        self.ref = {
            "ref": f"refs/tags/{TAG}",
            "object": {"type": "commit", "sha": COMMIT_SHA},
        }

    def _payloads(
        self,
        *,
        release: dict[str, object] | None = None,
        ref: dict[str, object] | None = None,
    ) -> dict[str, bytes | Exception]:
        selected_release = self.release if release is None else release
        selected_ref = self.ref if ref is None else ref
        payloads: dict[str, bytes | Exception] = {
            RELEASE_API: json.dumps(selected_release).encode("utf-8"),
            REF_API: json.dumps(selected_ref).encode("utf-8"),
        }
        for name in (ARCHIVE_NAME, MANIFEST_NAME, CHECKSUMS_NAME):
            payloads[DOWNLOAD_PREFIX + name] = (self.fixture / name).read_bytes()
        return payloads

    def test_downloads_verifies_extracts_and_reports_entry_points(self) -> None:
        output = self.root / "download"
        result = download_release(
            VERSION,
            output,
            token="",
            opener=FakeOpener(self._payloads()),
        )
        self.assertEqual(result["repository_commit"], COMMIT_SHA)
        self.assertEqual(result["entry_points"]["workspace_index"], "index.html")
        self.assertTrue((output / "index.html").is_file())
        self.assertEqual(
            set(result["entry_points"]),
            set(ENTRY_POINTS) | {"workspace_index"},
        )
        self.assertEqual(
            sorted(path.name for path in output.iterdir()),
            ["assets", "contents", "index.html"],
        )
        self.assertFalse(any(self.root.glob(".download.download-*")))

    def test_optional_credential_is_sent_only_to_api_requests(self) -> None:
        opener = FakeOpener(self._payloads())
        download_release(
            VERSION,
            self.root / "download",
            token="fixture",
            opener=opener,
        )
        api = [
            request
            for request in opener.requests
            if request.full_url.startswith(API_ROOT)  # type: ignore[attr-defined]
        ]
        assets = [request for request in opener.requests if request not in api]
        self.assertTrue(api)
        self.assertTrue(assets)
        self.assertTrue(
            all("Bearer fixture" in dict(request.header_items()).values() for request in api)
        )
        self.assertTrue(
            all("Bearer fixture" not in dict(request.header_items()).values() for request in assets)
        )

    def test_resolves_annotated_tag_to_commit(self) -> None:
        tag_sha = "a" * 40
        ref = {"object": {"type": "tag", "sha": tag_sha}}
        payloads = self._payloads(ref=ref)
        payloads[
            f"{API_ROOT}/repos/{REPOSITORY_FULL_NAME}/git/tags/{tag_sha}"
        ] = json.dumps(
            {"object": {"type": "commit", "sha": COMMIT_SHA}}
        ).encode("utf-8")
        result = download_release(
            VERSION,
            self.root / "download",
            token="",
            opener=FakeOpener(payloads),
        )
        self.assertEqual(result["repository_commit"], COMMIT_SHA)

    def test_rejects_invalid_version_before_network(self) -> None:
        opener = FakeOpener({})
        with self.assertRaisesRegex(ReleaseDownloadError, "MAJOR.MINOR.PATCH"):
            download_release(
                "v1.2.3",
                self.root / "download",
                token="",
                opener=opener,
            )
        self.assertEqual(opener.requests, [])

    def test_rejects_noncanonical_release_identity(self) -> None:
        cases = (
            {**self.release, "tag_name": "other"},
            {**self.release, "draft": True},
            {**self.release, "prerelease": True},
        )
        for index, release in enumerate(cases):
            with self.subTest(index=index):
                output = self.root / f"download-{index}"
                with self.assertRaises(ReleaseDownloadError):
                    download_release(
                        VERSION,
                        output,
                        token="",
                        opener=FakeOpener(self._payloads(release=release)),
                    )
                self.assertFalse(output.exists())

    def test_requires_exactly_three_canonical_assets(self) -> None:
        missing = {**self.release, "assets": list(self.release["assets"])[:-1]}
        extra = {
            **self.release,
            "assets": [
                *list(self.release["assets"]),
                {
                    "name": "extra.txt",
                    "size": 0,
                    "browser_download_url": DOWNLOAD_PREFIX + "extra.txt",
                },
            ],
        }
        duplicate = {
            **self.release,
            "assets": [
                *list(self.release["assets"]),
                list(self.release["assets"])[0],
            ],
        }
        for index, release in enumerate((missing, extra, duplicate)):
            with self.subTest(index=index):
                with self.assertRaises(ReleaseDownloadError):
                    download_release(
                        VERSION,
                        self.root / f"download-{index}",
                        token="",
                        opener=FakeOpener(self._payloads(release=release)),
                    )

    def test_rejects_unexpected_public_asset_url(self) -> None:
        assets = [dict(item) for item in self.release["assets"]]
        assets[0]["browser_download_url"] = "https://example.com/asset"
        release = {**self.release, "assets": assets}
        with self.assertRaisesRegex(ReleaseDownloadError, "unexpected public"):
            download_release(
                VERSION,
                self.root / "download",
                token="",
                opener=FakeOpener(self._payloads(release=release)),
            )

    def test_rejects_tag_manifest_commit_mismatch_transactionally(self) -> None:
        ref = {"object": {"type": "commit", "sha": "2" * 40}}
        output = self.root / "download"
        with self.assertRaisesRegex(ReleaseDownloadError, "tag commit"):
            download_release(
                VERSION,
                output,
                token="",
                opener=FakeOpener(self._payloads(ref=ref)),
            )
        self.assertFalse(output.exists())
        self.assertFalse(any(self.root.glob(".download.download-*")))

    def test_rejects_corrupt_asset_transactionally(self) -> None:
        payloads = self._payloads()
        archive = bytearray(payloads[DOWNLOAD_PREFIX + ARCHIVE_NAME])
        archive[-1] ^= 1
        payloads[DOWNLOAD_PREFIX + ARCHIVE_NAME] = bytes(archive)
        output = self.root / "download"
        with self.assertRaises(ReleaseDownloadError):
            download_release(
                VERSION,
                output,
                token="",
                opener=FakeOpener(payloads),
            )
        self.assertFalse(output.exists())

    def test_workspace_index_failure_is_transactional(self) -> None:
        output = self.root / "download"
        with mock.patch(
            "reporting.data_product_release_download.write_workspace_index",
            side_effect=ReleaseDownloadError("fixture index failure"),
        ):
            with self.assertRaisesRegex(ReleaseDownloadError, "fixture index failure"):
                download_release(
                    VERSION,
                    output,
                    token="",
                    opener=FakeOpener(self._payloads()),
                )
        self.assertFalse(output.exists())
        self.assertFalse(any(self.root.glob(".download.download-*")))

    def test_nonempty_output_is_not_overwritten(self) -> None:
        output = self.root / "download"
        output.mkdir()
        sentinel = output / "keep.txt"
        sentinel.write_text("keep", encoding="utf-8")
        opener = FakeOpener(self._payloads())
        with self.assertRaisesRegex(ReleaseDownloadError, "must not exist"):
            download_release(VERSION, output, token="", opener=opener)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")
        self.assertEqual(opener.requests, [])

    def test_cli_prints_entry_points_and_unified_cli_forwards(self) -> None:
        output = self.root / "download"
        result = {
            "release_version": VERSION,
            "release_tag": TAG,
            "repository_commit": COMMIT_SHA,
            "selected_configuration_count": 53,
            "scope_group_count": 13,
            "assets_directory": "assets",
            "contents_directory": "contents",
            "entry_points": {
                "workspace_index": "index.html",
                **{
                    key: (Path("contents") / relative).as_posix()
                    for key, relative in ENTRY_POINTS.items()
                },
            },
        }
        stdout = io.StringIO()
        with mock.patch.object(cli, "download_release", return_value=result), redirect_stdout(stdout):
            self.assertEqual(
                cli.main(["--version", VERSION, "--output-directory", str(output)]),
                0,
            )
        self.assertIn("Workspace index", stdout.getvalue())

        completed = SimpleNamespace(returncode=23)
        with mock.patch.object(dkb.subprocess, "run", return_value=completed) as run:
            self.assertEqual(
                dkb.run_script(
                    "data-product-release-download",
                    ["--version", VERSION, "--output-directory", "download"],
                ),
                23,
            )
        run.assert_called_once()

        stderr = io.StringIO()
        with mock.patch.object(
            cli,
            "download_release",
            side_effect=ReleaseDownloadError("fixture failure"),
        ), redirect_stderr(stderr):
            self.assertEqual(
                cli.main(["--version", VERSION, "--output-directory", str(output)]),
                1,
            )
        self.assertIn("fixture failure", stderr.getvalue())

    def test_workflow_is_read_only_and_checks_public_v1(self) -> None:
        workflow = (
            REPOSITORY
            / ".github/workflows/data-product-release-download.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("contents: read", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertIn("ubuntu-latest", workflow)
        self.assertIn("windows-latest", workflow)
        self.assertIn("--version 1.0.0", workflow)
        self.assertIn("653ddacf9dcaeefa356f53e3c00e71666f5c5b3e", workflow)


if __name__ == "__main__":
    unittest.main()
