from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))

import package_receipt  # noqa: E402
import package_workflow  # noqa: E402


class PackageReceiptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="dkb-receipt-")
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.env = os.environ.copy()
        self.env["GIT_CONFIG_NOSYSTEM"] = "1"
        config = self.root / "gitconfig"
        config.write_text("", encoding="utf-8")
        self.env["GIT_CONFIG_GLOBAL"] = str(config)
        self.git("init")
        self.git("config", "user.name", "Tests")
        self.git("config", "user.email", "tests@example.com")
        self.git("config", "core.autocrlf", "false")
        (self.repo / "README.md").write_text("base\n", encoding="utf-8")
        self.git("add", "README.md")
        self.git("commit", "-m", "base")
        self.git("branch", "-M", "main")
        self.base = self.git("rev-parse", "HEAD")
        self.git("switch", "-c", "tooling/test")
        target = self.repo / "tools" / "zażółć.py"
        target.parent.mkdir()
        target.write_text('print("gęślą jaźń")\n', encoding="utf-8")
        self.manifest = package_workflow.PackageManifest(
            branch="tooling/test",
            base_sha=self.base,
            commit_message="tooling: test",
            paths=("tools/zażółć.py",),
        )
        self.state = package_receipt.package_state(self.repo, self.manifest)
        self.receipt = self.root / "receipt.json"
        package_receipt.write_json_atomic(
            self.receipt,
            package_receipt.build_receipt(
                self.manifest,
                self.state,
                tests=298,
            ),
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def git(self, *args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=self.repo,
            env=self.env,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return completed.stdout.strip()

    def test_accepts_valid_receipt(self) -> None:
        result = package_receipt.validate_receipt(
            self.receipt, self.manifest, self.state
        )
        self.assertTrue(result.valid, result.reason)
        self.assertEqual(result.tests, 298)

    def test_rejects_receipt_with_other_branch(self) -> None:
        payload = json.loads(self.receipt.read_text(encoding="utf-8"))
        payload["branch"] = "tooling/other"
        package_receipt.write_json_atomic(self.receipt, payload)
        result = package_receipt.validate_receipt(
            self.receipt, self.manifest, self.state
        )
        self.assertFalse(result.valid)
        self.assertIn("branch", result.reason)

    def test_rejects_receipt_with_other_base_sha(self) -> None:
        payload = json.loads(self.receipt.read_text(encoding="utf-8"))
        payload["base_sha"] = "0" * 40
        package_receipt.write_json_atomic(self.receipt, payload)
        result = package_receipt.validate_receipt(
            self.receipt, self.manifest, self.state
        )
        self.assertFalse(result.valid)
        self.assertIn("base_sha", result.reason)

    def test_rejects_receipt_with_other_subject(self) -> None:
        payload = json.loads(self.receipt.read_text(encoding="utf-8"))
        payload["commit_message"] = "other"
        package_receipt.write_json_atomic(self.receipt, payload)
        result = package_receipt.validate_receipt(
            self.receipt, self.manifest, self.state
        )
        self.assertFalse(result.valid)
        self.assertIn("commit_message", result.reason)

    def test_rejects_receipt_with_other_path_manifest(self) -> None:
        payload = json.loads(self.receipt.read_text(encoding="utf-8"))
        payload["paths"] = ["README.md"]
        package_receipt.write_json_atomic(self.receipt, payload)
        result = package_receipt.validate_receipt(
            self.receipt, self.manifest, self.state
        )
        self.assertFalse(result.valid)
        self.assertIn("paths", result.reason)

    def test_rejects_one_byte_change_after_review(self) -> None:
        target = self.repo / "tools" / "zażółć.py"
        original = target.read_bytes()
        target.write_bytes(original[:-1] + b"!")
        changed = package_receipt.package_state(self.repo, self.manifest)
        result = package_receipt.validate_receipt(
            self.receipt, self.manifest, changed
        )
        self.assertFalse(result.valid)
        self.assertIn(result.reason.split(":")[-1].strip(), {"tree_sha", "byte_sha256"})

    def test_utf8_path_and_content_have_stable_state(self) -> None:
        again = package_receipt.package_state(self.repo, self.manifest)
        self.assertEqual(self.state, again)
        self.assertRegex(self.state.tree_sha, r"^[0-9a-f]{40}$")
        self.assertRegex(self.state.byte_sha256, r"^[0-9a-f]{64}$")

    def test_requires_receipt_output_outside_repository(self) -> None:
        with self.assertRaises(package_workflow.GitCommandError):
            package_receipt.require_external_output(
                self.repo,
                self.repo / "receipt.json",
            )


if __name__ == "__main__":
    unittest.main()
