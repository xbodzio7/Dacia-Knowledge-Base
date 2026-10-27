from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))

import package_publish  # noqa: E402
import package_receipt  # noqa: E402
import package_workflow  # noqa: E402


class PackagePublishTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="dkb-publish-")
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.remote = self.root / "remote.git"
        self.output = self.root / "output"
        self.manifest_path = self.root / "package.json"
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
        (self.repo / "README.md").write_text("base\n", encoding="utf-8", newline="\n")
        self.git("add", "README.md")
        self.git("commit", "-m", "base")
        self.git("branch", "-M", "main")
        subprocess.run(
            ["git", "clone", "--bare", str(self.repo), str(self.remote)],
            cwd=self.root,
            env=self.env,
            check=True,
            capture_output=True,
            text=True,
        )
        self.git("remote", "add", "origin", str(self.remote))
        self.git("fetch", "origin")
        self.git("branch", "--set-upstream-to", "origin/main", "main")
        self.base = self.git("rev-parse", "HEAD")
        self.git("switch", "-c", "tooling/test")
        target = self.repo / "tools" / "example.py"
        target.parent.mkdir()
        target.write_text("print('ok')\n", encoding="utf-8", newline="\n")
        self.manifest = package_workflow.PackageManifest(
            branch="tooling/test",
            base_sha=self.base,
            commit_message="tooling: publish test",
            paths=("tools/example.py",),
        )
        self.manifest_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "branch": self.manifest.branch,
                    "base_sha": self.manifest.base_sha,
                    "commit_message": self.manifest.commit_message,
                    "expected_commits": 1,
                    "paths": list(self.manifest.paths),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        self.write_valid_receipt()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def git(self, *args: str, check: bool = True) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=self.repo,
            env=self.env,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if check and completed.returncode != 0:
            self.fail(
                f"git {' '.join(args)} failed\n{completed.stdout}\n{completed.stderr}"
            )
        return completed.stdout.strip()

    @property
    def receipt_path(self) -> Path:
        return self.output / "quality-receipt.json"

    @property
    def handoff_path(self) -> Path:
        return self.output / "handoff.json"

    def write_valid_receipt(self, tests: int = 298) -> None:
        self.output.mkdir(exist_ok=True)
        state = package_receipt.package_state(self.repo, self.manifest)
        package_receipt.write_json_atomic(
            self.receipt_path,
            package_receipt.build_receipt(
                self.manifest,
                state,
                tests=tests,
            ),
        )

    def publish(self, *, push: bool = False) -> int:
        return package_publish.publish_package(
            self.repo,
            self.manifest,
            manifest_path=self.manifest_path,
            output_dir=self.output,
            push=push,
        )

    def test_publishes_exact_manifest_from_empty_staging(self) -> None:
        self.assertEqual(self.git("diff", "--cached", "--name-only"), "")
        result = self.publish()
        self.assertEqual(result, 0)
        self.assertEqual(self.git("rev-list", "--count", f"{self.base}..HEAD"), "1")
        self.assertEqual(
            self.git("diff", "--name-only", f"{self.base}...HEAD"),
            "tools/example.py",
        )
        self.assertEqual(
            self.git("log", "-1", "--pretty=%s"),
            self.manifest.commit_message,
        )
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_rejects_additional_untracked_path(self) -> None:
        (self.repo / "extra.txt").write_text("extra\n", encoding="utf-8", newline="\n")
        result = self.publish()
        self.assertEqual(result, 1)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)
        handoff = json.loads(self.handoff_path.read_text(encoding="utf-8"))
        self.assertEqual(handoff["status"], "FAIL")
        self.assertEqual(handoff["phase"], "review")

    def test_rejects_additional_staged_path(self) -> None:
        (self.repo / "extra.txt").write_text("extra\n", encoding="utf-8", newline="\n")
        self.git("add", "extra.txt")
        result = self.publish()
        self.assertEqual(result, 1)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)
        self.assertIn("extra.txt", self.git("diff", "--cached", "--name-only"))

    def test_reuses_valid_receipt_without_quality(self) -> None:
        with mock.patch.object(
            package_receipt,
            "run_quality_and_write_receipt",
        ) as run_quality:
            result = self.publish()
        self.assertEqual(result, 0)
        run_quality.assert_not_called()

    def test_invalid_receipt_runs_full_quality(self) -> None:
        payload = json.loads(self.receipt_path.read_text(encoding="utf-8"))
        payload["branch"] = "tooling/other"
        package_receipt.write_json_atomic(self.receipt_path, payload)

        def fake_quality(
            repository: Path,
            manifest: package_workflow.PackageManifest,
            *,
            base_ref: str,
            receipt_path: Path,
            log_path: Path,
            require_review_state: bool,
        ) -> int:
            log_path.write_text("verbose quality log\n", encoding="utf-8")
            state = package_receipt.package_state(repository, manifest)
            package_receipt.write_json_atomic(
                receipt_path,
                package_receipt.build_receipt(manifest, state, tests=298),
            )
            return 0

        with mock.patch.object(
            package_receipt,
            "run_quality_and_write_receipt",
            side_effect=fake_quality,
        ) as run_quality:
            result = self.publish()
        self.assertEqual(result, 0)
        run_quality.assert_called_once()

    def test_finish_failure_writes_fail_handoff(self) -> None:
        with mock.patch.object(
            package_publish,
            "_capture_finish",
            return_value=7,
        ):
            result = self.publish()
        self.assertEqual(result, 1)
        self.assertEqual(self.git("rev-list", "--count", f"{self.base}..HEAD"), "1")
        handoff = json.loads(self.handoff_path.read_text(encoding="utf-8"))
        self.assertEqual(handoff["status"], "FAIL")
        self.assertEqual(handoff["phase"], "finish")
        self.assertEqual(handoff["package_finish"], "FAIL")

    def test_generates_small_pass_handoff(self) -> None:
        result = self.publish()
        self.assertEqual(result, 0)
        handoff = json.loads(self.handoff_path.read_text(encoding="utf-8"))
        self.assertEqual(handoff["status"], "PASS")
        self.assertEqual(handoff["phase"], "complete")
        self.assertEqual(handoff["quality"], "PASS")
        self.assertEqual(handoff["package_review"], "PASS")
        self.assertEqual(handoff["package_finish"], "PASS")
        self.assertEqual(handoff["push"], "SKIPPED")
        self.assertEqual(handoff["tests"], 298)
        self.assertEqual(handoff["exit_code"], 0)
        self.assertLess(self.handoff_path.stat().st_size, 2000)

    def test_failed_push_writes_fail_handoff(self) -> None:
        hooks = self.remote / "hooks"
        hook = hooks / "pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8", newline="\n")
        hook.chmod(0o755)
        result = self.publish(push=True)
        self.assertEqual(result, 1)
        handoff = json.loads(self.handoff_path.read_text(encoding="utf-8"))
        self.assertEqual(handoff["status"], "FAIL")
        self.assertEqual(handoff["phase"], "push")
        self.assertNotEqual(handoff["push"], "PASS")

    def test_safe_rerun_does_not_create_second_commit(self) -> None:
        self.assertEqual(self.publish(), 0)
        first_head = self.git("rev-parse", "HEAD")
        self.assertEqual(self.publish(), 0)
        self.assertEqual(self.git("rev-parse", "HEAD"), first_head)
        self.assertEqual(self.git("rev-list", "--count", f"{self.base}..HEAD"), "1")

    def test_explicit_push_updates_only_current_branch(self) -> None:
        result = self.publish(push=True)
        self.assertEqual(result, 0)
        head = self.git("rev-parse", "HEAD")
        remote = self.git("ls-remote", "--heads", "origin", "tooling/test")
        self.assertTrue(remote.startswith(head))
        handoff = json.loads(self.handoff_path.read_text(encoding="utf-8"))
        self.assertEqual(handoff["push"], "PASS")


if __name__ == "__main__":
    unittest.main()
