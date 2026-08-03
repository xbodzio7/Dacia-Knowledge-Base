from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

import sys

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))

from reporting.data_product_release_model import archive_name, verify_release_assets  # noqa: E402
from reporting.portfolio_model_family_release_integration import (  # noqa: E402
    create_release_assets,
)


class DataProductsV1121CorrectiveReleaseTests(unittest.TestCase):
    COMMIT = "1" * 40

    def build(self, root: Path, version: str) -> tuple[dict[str, object], str]:
        output = root / version
        manifest = create_release_assets(
            REPOSITORY,
            output,
            version,
            self.COMMIT,
        )
        with ZipFile(output / archive_name(version)) as handle:
            notes = handle.read("RELEASE_NOTES.md").decode("utf-8")
        return manifest, notes

    def test_patch_release_notes_describe_direct_workspace_interface(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest, notes = self.build(Path(temporary), "1.12.1")
        self.assertEqual(manifest["release_version"], "1.12.1")
        self.assertIn("## v1.12.1 corrective workspace interface", notes)
        self.assertIn("model_family_summary_html", notes)
        self.assertIn("Model family summary", notes)
        self.assertIn("does not rewrite `data-products-v1.12.0`", notes)

    def test_patch_release_remains_byte_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "first"
            second = root / "second"
            first_manifest = create_release_assets(
                REPOSITORY, first, "1.12.1", self.COMMIT
            )
            second_manifest = create_release_assets(
                REPOSITORY, second, "1.12.1", self.COMMIT
            )
            self.assertEqual(first_manifest, second_manifest)
            for name in (
                archive_name("1.12.1"),
                "data-product-release-manifest.json",
                "SHA256SUMS",
            ):
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
            self.assertEqual(verify_release_assets(first), first_manifest)

    def test_existing_v1_12_0_release_notes_contract_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            _, notes = self.build(Path(temporary), "1.12.0")
        self.assertIn("## v1.12.0 portfolio model-family product", notes)
        self.assertNotIn("## v1.12.1 corrective workspace interface", notes)


if __name__ == "__main__":
    unittest.main()
