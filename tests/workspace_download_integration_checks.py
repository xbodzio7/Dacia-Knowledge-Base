from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))

from reporting import data_product_release_download as downloader  # noqa: E402


class WorkspaceDownloadIntegrationChecks(unittest.TestCase):
    def test_download_adds_index_before_atomic_workspace_publish(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "workspace"
            version = "1.2.3"
            commit = "1" * 40
            release = {
                "id": 123,
                "html_url": (
                    "https://github.com/xbodzio7/Dacia-Knowledge-Base/"
                    "releases/tag/data-products-v1.2.3"
                ),
                "published_at": "2026-07-20T00:00:00Z",
            }
            manifest = {
                "release_version": version,
                "repository_commit": commit,
                "selected_configuration_count": 53,
                "scope_group_count": 13,
            }

            def extract(
                assets_directory: Path,
                contents_directory: Path,
                verified_manifest: object,
            ) -> dict[str, str]:
                self.assertEqual(verified_manifest, manifest)
                contents_directory.mkdir()
                return {"shortlist_html": "contents/shortlist.html"}

            def write_index(
                workspace_root: Path,
                verified_manifest: object,
                metadata: object,
            ) -> Path:
                self.assertEqual(verified_manifest, manifest)
                self.assertEqual(metadata["repository_commit"], commit)
                path = workspace_root / "index.html"
                path.write_text("<!doctype html>\n", encoding="utf-8")
                return path

            with (
                mock.patch.object(
                    downloader,
                    "_release_metadata",
                    return_value=(release, ()),
                ),
                mock.patch.object(
                    downloader,
                    "_resolve_tag_commit",
                    return_value=commit,
                ),
                mock.patch.object(
                    downloader,
                    "verify_release_assets",
                    return_value=manifest,
                ),
                mock.patch.object(
                    downloader,
                    "_extract_verified_contents",
                    side_effect=extract,
                ),
                mock.patch.object(
                    downloader,
                    "write_workspace_index",
                    side_effect=write_index,
                ),
            ):
                result = downloader.download_release(
                    version,
                    output,
                    token="",
                )

            self.assertEqual(result["entry_points"]["workspace_index"], "index.html")
            self.assertTrue((output / "index.html").is_file())
            self.assertEqual(
                sorted(path.name for path in output.iterdir()),
                ["assets", "contents", "index.html"],
            )
            self.assertFalse(any(Path(temporary).glob(".workspace.download-*")))


if __name__ == "__main__":
    unittest.main()
