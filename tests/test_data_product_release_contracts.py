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


if __name__ == "__main__":
    unittest.main()
