from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock


REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS_DIRECTORY = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS_DIRECTORY))
import package_workflow  # noqa: E402


class PackageWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory(
            prefix="dkb-workflow-test-",
            dir=REPOSITORY.parent,
        )
        root = Path(self.temporary_directory.name)
        self.root = root
        self.remote = root / "remote.git"
        self.repository = root / "repository"

        isolated_config = root / "gitconfig"
        isolated_config.write_text("", encoding="utf-8", newline="\n")
        self.git_environment = os.environ.copy()
        self.git_environment.pop("GIT_DIR", None)
        self.git_environment.pop("GIT_WORK_TREE", None)
        self.git_environment["GIT_CONFIG_NOSYSTEM"] = "1"
        self.git_environment["GIT_CONFIG_GLOBAL"] = str(isolated_config)

        self.run_external("git", "init", str(self.repository), cwd=root)
        self.run_git("config", "user.name", "DKB Tests")
        self.run_git("config", "user.email", "tests@example.com")
        self.run_git("config", "core.autocrlf", "false")

        (self.repository / "README.md").write_text(
            "baseline\n",
            encoding="utf-8",
            newline="\n",
        )
        self.run_git("add", "README.md")
        self.run_git("commit", "-m", "baseline")
        self.run_git("branch", "-M", "main")

        self.run_external(
            "git",
            "clone",
            "--bare",
            str(self.repository),
            str(self.remote),
            cwd=root,
        )
        self.run_git("remote", "add", "origin", str(self.remote))
        self.run_git("fetch", "origin")
        self.run_git(
            "branch",
            "--set-upstream-to",
            "origin/main",
            "main",
        )
        self.base_sha = self.run_git("rev-parse", "main")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_external(
        self,
        *arguments: str,
        cwd: Path | None = None,
    ) -> str:
        completed = subprocess.run(
            arguments,
            cwd=cwd,
            env=self.git_environment,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            self.fail(
                f"command failed ({completed.returncode}): "
                f"{' '.join(arguments)}\n"
                f"stdout:\n{completed.stdout}\n"
                f"stderr:\n{completed.stderr}"
            )
        return completed.stdout.strip()

    def run_git(self, *arguments: str) -> str:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=self.repository,
            env=self.git_environment,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            self.fail(
                f"git command failed ({completed.returncode}): "
                f"git {' '.join(arguments)}\n"
                f"stdout:\n{completed.stdout}\n"
                f"stderr:\n{completed.stderr}"
            )
        return completed.stdout.strip()

    def run_main(self, arguments: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()

        with (
            mock.patch.object(
                package_workflow,
                "repository_root",
                return_value=self.repository,
            ),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            result = package_workflow.main(arguments)

        return result, stdout.getvalue(), stderr.getvalue()

    def start_branch(self, branch: str = "tooling/test") -> None:
        result, _, stderr = self.run_main(["start", branch])
        self.assertEqual(result, 0, stderr)

    def commit_file(
        self,
        path: str = "tools/example.py",
        content: str = "print('ok')\n",
    ) -> None:
        target = self.repository / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")
        self.run_git("add", path)
        self.run_git("commit", "-m", "package change")

    def write_manifest(
        self,
        *,
        branch: str = "tooling/test",
        base_sha: str | None = None,
        commit_message: str = "package change",
        paths: list[str] | None = None,
    ) -> Path:
        manifest = self.root / "package.json"
        manifest.write_text(
            json.dumps(
                {
                    "version": 1,
                    "branch": branch,
                    "base_sha": base_sha or self.base_sha,
                    "commit_message": commit_message,
                    "expected_commits": 1,
                    "paths": paths or ["tools/example.py"],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return manifest

    def test_run_git_ignores_ambient_git_context(self) -> None:
        hostile_environment = {
            "GIT_DIR": str(self.repository / ".git"),
            "GIT_WORK_TREE": str(REPOSITORY),
            "GIT_INDEX_FILE": str(REPOSITORY / ".git" / "index"),
        }

        with mock.patch.dict(
            os.environ,
            hostile_environment,
            clear=False,
        ):
            status = package_workflow.git_output(
                self.repository,
                "status",
                "--porcelain",
            )

        self.assertEqual(status, "")

    def test_start_creates_branch_from_synchronized_main(self) -> None:
        result, stdout, stderr = self.run_main(
            ["start", "tooling/workflow-test"]
        )

        self.assertEqual(result, 0, stderr)
        self.assertEqual(
            self.run_git("branch", "--show-current"),
            "tooling/workflow-test",
        )
        self.assertIn("PACKAGE STARTED", stdout)

    def test_start_rejects_dirty_working_tree(self) -> None:
        (self.repository / "README.md").write_text(
            "dirty\n",
            encoding="utf-8",
            newline="\n",
        )

        result, _, stderr = self.run_main(
            ["start", "tooling/dirty"]
        )

        self.assertEqual(result, 1)
        self.assertIn("working tree is not clean", stderr)
        self.assertEqual(self.run_git("branch", "--show-current"), "main")

    def test_start_rejects_existing_local_branch(self) -> None:
        self.run_git("branch", "tooling/existing")

        result, _, stderr = self.run_main(
            ["start", "tooling/existing"]
        )

        self.assertEqual(result, 1)
        self.assertIn("local branch already exists", stderr)

    def test_review_accepts_untracked_file_inside_scope(self) -> None:
        self.start_branch()
        target = self.repository / "tools" / "new_tool.py"
        target.parent.mkdir()
        target.write_text(
            "print('ok')\n",
            encoding="utf-8",
            newline="\n",
        )

        result, stdout, stderr = self.run_main(
            ["review", "--allow", "tools"]
        )

        self.assertEqual(result, 0, stderr)
        self.assertIn("tools/new_tool.py", stdout)
        self.assertIn("PACKAGE REVIEW", stdout)

    def test_review_show_diff_includes_untracked_content(self) -> None:
        self.start_branch()
        target = self.repository / "tools" / "new_tool.py"
        target.parent.mkdir()
        target.write_text(
            "print('ok')\n",
            encoding="utf-8",
            newline="\n",
        )

        result, stdout, stderr = self.run_main(
            ["review", "--allow", "tools", "--show-diff"]
        )

        self.assertEqual(result, 0, stderr)
        self.assertIn("UNTRACKED FILES", stdout)
        self.assertIn("+++ b/tools/new_tool.py", stdout)
        self.assertIn("+print('ok')", stdout)

    def test_review_rejects_file_outside_scope(self) -> None:
        self.start_branch()
        (self.repository / "README.md").write_text(
            "changed\n",
            encoding="utf-8",
            newline="\n",
        )

        result, stdout, stderr = self.run_main(
            ["review", "--allow", "tools"]
        )

        self.assertEqual(result, 1)
        self.assertIn("OUTSIDE ALLOWED SCOPE", stdout)
        self.assertIn("outside the allowed scope", stderr)

    def test_review_runs_quality_when_requested(self) -> None:
        self.start_branch()
        target = self.repository / "tools" / "new_tool.py"
        target.parent.mkdir()
        target.write_text(
            "print('ok')\n",
            encoding="utf-8",
            newline="\n",
        )

        with mock.patch.object(
            package_workflow,
            "run_quality",
            return_value=0,
        ) as run_quality:
            result, _, stderr = self.run_main(
                ["review", "--allow", "tools", "--quality"]
            )

        self.assertEqual(result, 0, stderr)
        run_quality.assert_called_once_with(self.repository)

    def test_review_manifest_accepts_exact_scope_and_utf8_diff(
        self,
    ) -> None:
        self.start_branch()
        target = self.repository / "tools" / "zażółć.py"
        target.parent.mkdir()
        target.write_text(
            'print("gęślą jaźń")\n',
            encoding="utf-8",
            newline="\n",
        )
        manifest = self.write_manifest(
            paths=["tools/zażółć.py"],
        )

        result, stdout, stderr = self.run_main(
            [
                "review",
                "--manifest",
                str(manifest),
                "--show-diff",
            ]
        )

        self.assertEqual(result, 0, stderr)
        self.assertIn("PACKAGE MANIFEST", stdout)
        self.assertIn("tools/zażółć.py", stdout)
        self.assertIn('+print("gęślą jaźń")', stdout)

    def test_review_manifest_rejects_wrong_branch(self) -> None:
        self.start_branch()
        target = self.repository / "tools" / "example.py"
        target.parent.mkdir()
        target.write_text("print('ok')\n", encoding="utf-8")
        manifest = self.write_manifest(branch="tooling/other")

        result, _, stderr = self.run_main(
            ["review", "--manifest", str(manifest)]
        )

        self.assertEqual(result, 1)
        self.assertIn("manifest branch", stderr)

    def test_review_manifest_rejects_wrong_base_sha(self) -> None:
        self.start_branch()
        target = self.repository / "tools" / "example.py"
        target.parent.mkdir()
        target.write_text("print('ok')\n", encoding="utf-8")
        manifest = self.write_manifest(base_sha="0" * 40)

        result, _, stderr = self.run_main(
            ["review", "--manifest", str(manifest)]
        )

        self.assertEqual(result, 1)
        self.assertIn("origin/main moved", stderr)

    def test_review_manifest_rejects_path_mismatch(self) -> None:
        self.start_branch()
        (self.repository / "README.md").write_text(
            "changed\n",
            encoding="utf-8",
        )
        manifest = self.write_manifest(
            paths=["tools/example.py"],
        )

        result, _, stderr = self.run_main(
            ["review", "--manifest", str(manifest)]
        )

        self.assertEqual(result, 1)
        self.assertIn("working tree path manifest differs", stderr)

    def test_finish_manifest_accepts_exact_commit(self) -> None:
        self.start_branch()
        self.commit_file()
        manifest = self.write_manifest()

        result, stdout, stderr = self.run_main(
            ["finish", "--manifest", str(manifest)]
        )

        self.assertEqual(result, 0, stderr)
        self.assertIn("Manifest: PASS", stdout)
        self.assertIn("Subject: package change", stdout)

    def test_finish_manifest_rejects_multiple_commits(self) -> None:
        self.start_branch()
        self.commit_file()
        self.commit_file(
            path="tools/second.py",
            content="print('second')\n",
        )
        manifest = self.write_manifest(
            paths=["tools/example.py", "tools/second.py"],
        )

        result, _, stderr = self.run_main(
            ["finish", "--manifest", str(manifest)]
        )

        self.assertEqual(result, 1)
        self.assertIn("expected exactly 1 commit", stderr)

    def test_finish_manifest_rejects_wrong_subject(self) -> None:
        self.start_branch()
        self.commit_file()
        manifest = self.write_manifest(
            commit_message="different subject",
        )

        result, _, stderr = self.run_main(
            ["finish", "--manifest", str(manifest)]
        )

        self.assertEqual(result, 1)
        self.assertIn("commit subject differs", stderr)

    def test_finish_manifest_rejects_wrong_paths(self) -> None:
        self.start_branch()
        self.commit_file()
        manifest = self.write_manifest(
            paths=["README.md"],
        )

        result, _, stderr = self.run_main(
            ["finish", "--manifest", str(manifest)]
        )

        self.assertEqual(result, 1)
        self.assertIn("committed path manifest differs", stderr)

    def test_finish_reports_clean_committed_package(self) -> None:
        self.start_branch()
        self.commit_file()

        result, stdout, stderr = self.run_main(["finish"])

        self.assertEqual(result, 0, stderr)
        self.assertIn("Commits: 1", stdout)
        self.assertIn("tools/example.py", stdout)
        self.assertIn("git push -u origin tooling/test", stdout)

    def test_finish_rejects_dirty_working_tree(self) -> None:
        self.start_branch()
        self.commit_file()
        (self.repository / "README.md").write_text(
            "dirty\n",
            encoding="utf-8",
            newline="\n",
        )

        result, _, stderr = self.run_main(["finish"])

        self.assertEqual(result, 1)
        self.assertIn("working tree is not clean", stderr)

    def test_finish_rejects_branch_without_commits(self) -> None:
        self.start_branch()

        result, _, stderr = self.run_main(["finish"])

        self.assertEqual(result, 1)
        self.assertIn("no commits ahead", stderr)

    def test_path_is_allowed_handles_files_and_directories(self) -> None:
        self.assertTrue(
            package_workflow.path_is_allowed(
                "tools/dkb.py",
                ["tools"],
            )
        )
        self.assertTrue(
            package_workflow.path_is_allowed(
                "README.md",
                ["README.md"],
            )
        )
        self.assertFalse(
            package_workflow.path_is_allowed(
                "tests/test_dkb.py",
                ["tools"],
            )
        )


if __name__ == "__main__":
    unittest.main()
