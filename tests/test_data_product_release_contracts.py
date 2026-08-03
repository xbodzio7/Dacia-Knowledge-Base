from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]


class DataProductReleaseContractTests(unittest.TestCase):
    def test_unified_cli_routes_release_command(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(REPOSITORY / "tools" / "dkb.py"),
                "data-product-release",
                "--help",
            ],
            cwd=REPOSITORY,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("--output-directory", completed.stdout)
        self.assertIn("--commit-sha", completed.stdout)
        self.assertIn("--verify", completed.stdout)

    def test_release_workflow_is_manual_write_and_read_only_on_prs(self) -> None:
        text = (
            REPOSITORY / ".github" / "workflows" / "data-product-release.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("  pull_request:\n", text)
        self.assertIn("  workflow_dispatch:\n", text)
        self.assertNotIn("\n  push:\n", text)
        self.assertNotIn("\n  schedule:\n", text)
        self.assertIn("permissions:\n  contents: read\n", text)
        self.assertIn(
            "  publish-release:\n"
            "    if: github.event_name == 'workflow_dispatch'",
            text,
        )
        self.assertIn("    permissions:\n      contents: write\n", text)
        self.assertIn('if [[ "${GITHUB_REF}" != "refs/heads/main" ]]', text)
        self.assertIn("Reject existing tag or release", text)
        self.assertIn('if [[ "${output}" != *"(HTTP 404)"* ]]', text)
        self.assertIn("Unable to prove ${label} absence", text)
        self.assertIn("gh release create", text)
        self.assertIn("data-product-release-manifest.json", text)
        self.assertIn("SHA256SUMS", text)

        publisher_path = (
            REPOSITORY / "tools" / "publish_data_products_v1_14_0_20260803.sh"
        )
        recorder_path = (
            REPOSITORY
            / "tools"
            / "record_data_products_v1_14_0_publication_20260803.py"
        )
        if publisher_path.exists() or recorder_path.exists():
            self.assertTrue(publisher_path.is_file())
            self.assertTrue(recorder_path.is_file())
            publisher = publisher_path.read_text(encoding="utf-8")
            recorder = recorder_path.read_text(encoding="utf-8")

            self.assertIn(
                "data_products_v1_14_0_publication_001", publisher
            )
            self.assertIn("data-products-v1.14.0", publisher)
            self.assertIn('actual_sha="$(git rev-parse HEAD)"', publisher)
            self.assertIn("release-a", publisher)
            self.assertIn("release-b", publisher)
            self.assertIn("diff -qr", publisher)
            self.assertIn("data-product-workspace-verify", publisher)
            self.assertIn("model_family_summary_html", publisher)
            self.assertIn(
                "model_family_comparison_matrix_html", publisher
            )
            self.assertIn(
                "model_version_comparison_matrix_html", publisher
            )
            self.assertIn("Model version comparison matrix", publisher)
            self.assertIn("gh release create data-products-v1.14.0", publisher)
            self.assertIn("gh release download data-products-v1.14.0", publisher)
            self.assertIn(
                "record_data_products_v1_14_0_publication_20260803.py",
                publisher,
            )
            self.assertIn(
                "release(data-products): record v1.14.0 publication",
                publisher,
            )
            self.assertIn("data_products_v1_14_0_publication", recorder)
            self.assertIn(
                "data_products_v1_14_0_publication.json", recorder
            )
            self.assertIn("public_v1_13_0_immutable", recorder)
            self.assertIn(
                "post_v1_14_0_release_priority_selection_review_001",
                recorder,
            )


if __name__ == "__main__":
    unittest.main()
