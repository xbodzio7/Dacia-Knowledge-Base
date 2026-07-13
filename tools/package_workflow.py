#!/usr/bin/env python3
"""
Automate safe Git package workflow checks for Dacia Knowledge Base.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence


class GitCommandError(RuntimeError):
    """Raised when a required Git command fails."""


GIT_CONTEXT_VARIABLES = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_COMMON_DIR",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
)


def git_environment() -> dict[str, str]:
    """Return the process environment without inherited Git context."""
    environment = os.environ.copy()
    for variable in GIT_CONTEXT_VARIABLES:
        environment.pop(variable, None)
    return environment


def repository_root() -> Path:
    """Return the repository root containing this script."""
    return Path(__file__).resolve().parent.parent


def run_git(
    repository: Path,
    *arguments: str,
    check: bool = True,
    capture_output: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run Git in the repository and optionally require success."""
    command = ["git", *arguments]

    try:
        completed = subprocess.run(
            command,
            cwd=repository,
            env=git_environment(),
            check=False,
            capture_output=capture_output,
            text=True,
        )
    except OSError as exc:
        raise GitCommandError(
            f"cannot run {' '.join(command)!r}: {exc}"
        ) from exc

    if check and completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        message = (
            f"command failed ({completed.returncode}): "
            f"{' '.join(command)}"
        )
        if detail:
            message = f"{message}\n{detail}"
        raise GitCommandError(message)

    return completed


def git_output(repository: Path, *arguments: str) -> str:
    """Return stripped standard output from a successful Git command."""
    return run_git(repository, *arguments).stdout.strip()


def current_branch(repository: Path) -> str:
    """Return the currently checked-out branch name."""
    branch = git_output(repository, "branch", "--show-current")
    if not branch:
        raise GitCommandError(
            "detached HEAD is not supported by package workflow commands"
        )
    return branch


def working_tree_status(repository: Path) -> str:
    """Return porcelain working-tree status."""
    return git_output(repository, "status", "--porcelain")


def ensure_clean(repository: Path) -> None:
    """Require a clean index and working tree."""
    status = working_tree_status(repository)
    if status:
        raise GitCommandError(
            "working tree is not clean:\n"
            f"{status}"
        )


def ref_exists(repository: Path, ref: str) -> bool:
    """Return whether a Git reference exists."""
    completed = run_git(
        repository,
        "show-ref",
        "--verify",
        "--quiet",
        ref,
        check=False,
    )
    return completed.returncode == 0


def null_separated_paths(
    repository: Path,
    *arguments: str,
) -> set[str]:
    """Return paths from a NUL-separated Git command."""
    output = run_git(repository, *arguments).stdout
    return {
        path
        for path in output.split("\0")
        if path
    }


def untracked_paths(repository: Path) -> list[str]:
    """Return untracked paths not ignored by Git."""
    return sorted(
        null_separated_paths(
            repository,
            "ls-files",
            "--others",
            "--exclude-standard",
            "-z",
        )
    )


def changed_paths(repository: Path) -> list[str]:
    """Return staged, unstaged and untracked paths."""
    paths: set[str] = set()
    paths.update(
        null_separated_paths(
            repository,
            "diff",
            "--name-only",
            "-z",
        )
    )
    paths.update(
        null_separated_paths(
            repository,
            "diff",
            "--cached",
            "--name-only",
            "-z",
        )
    )
    paths.update(untracked_paths(repository))
    return sorted(paths)


def committed_paths(
    repository: Path,
    base_ref: str,
) -> list[str]:
    """Return paths changed between the base ref and HEAD."""
    return sorted(
        null_separated_paths(
            repository,
            "diff",
            "--name-only",
            "-z",
            f"{base_ref}...HEAD",
        )
    )


def path_is_allowed(path: str, allowed: Sequence[str]) -> bool:
    """Return whether a path is covered by an allowed file or directory."""
    if not allowed:
        return True

    normalized_path = path.replace("\\", "/")

    for candidate in allowed:
        normalized_candidate = (
            candidate.replace("\\", "/").rstrip("/")
        )
        if not normalized_candidate:
            continue
        if normalized_path == normalized_candidate:
            return True
        if normalized_path.startswith(f"{normalized_candidate}/"):
            return True

    return False


def ahead_behind(
    repository: Path,
    base_ref: str,
) -> tuple[int, int]:
    """Return commits behind and ahead of the base ref."""
    output = git_output(
        repository,
        "rev-list",
        "--left-right",
        "--count",
        f"{base_ref}...HEAD",
    )
    behind_text, ahead_text = output.split()
    return int(behind_text), int(ahead_text)


def print_section(title: str) -> None:
    """Print a visible output section."""
    print()
    print(f"===== {title} =====")


def print_git_output(
    repository: Path,
    *arguments: str,
) -> None:
    """Print output from a Git command when it is not empty."""
    output = git_output(repository, *arguments)
    if output:
        print(output)


def print_untracked_files(
    repository: Path,
    paths: Sequence[str],
) -> None:
    """Print reviewable pseudo-diffs for untracked files."""
    print_section("UNTRACKED FILES")
    if not paths:
        print("(none)")
        return

    for path in paths:
        target = repository / path
        print("--- /dev/null")
        print(f"+++ b/{path}")

        try:
            data = target.read_bytes()
        except OSError as exc:
            print(f"[cannot read file: {exc}]")
            continue

        if b"\0" in data:
            print(f"[binary file: {len(data)} bytes]")
            continue

        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            print(f"[non-UTF-8 file: {len(data)} bytes]")
            continue

        if not text:
            print("[empty file]")
            continue

        for line in text.splitlines():
            print(f"+{line}")
        if not text.endswith(("\n", "\r")):
            print("\\ No newline at end of file")


def run_quality(repository: Path) -> int:
    """Run the complete project quality gate."""
    dkb = repository / "tools" / "dkb.py"

    try:
        completed = subprocess.run(
            [sys.executable, str(dkb), "quality"],
            cwd=repository,
            check=False,
        )
    except OSError as exc:
        print(
            f"ERROR: cannot run quality checks: {exc}",
            file=sys.stderr,
        )
        return 1

    return completed.returncode


def start_package(
    repository: Path,
    branch: str,
    *,
    base: str = "main",
    remote: str = "origin",
) -> int:
    """Synchronize the base branch and create a package branch."""
    if current_branch(repository) != base:
        raise GitCommandError(
            f"package start requires branch {base!r}"
        )

    ensure_clean(repository)

    branch_check = run_git(
        repository,
        "check-ref-format",
        "--branch",
        branch,
        check=False,
    )
    if branch_check.returncode != 0:
        raise GitCommandError(f"invalid branch name: {branch!r}")

    print_section("SYNCHRONIZE BASE")
    run_git(
        repository,
        "fetch",
        remote,
        "--prune",
        capture_output=False,
    )
    run_git(
        repository,
        "pull",
        "--ff-only",
        remote,
        base,
        capture_output=False,
    )

    ensure_clean(repository)

    local_ref = f"refs/heads/{branch}"
    remote_ref = f"refs/remotes/{remote}/{branch}"

    if ref_exists(repository, local_ref):
        raise GitCommandError(
            f"local branch already exists: {branch}"
        )
    if ref_exists(repository, remote_ref):
        raise GitCommandError(
            f"remote branch already exists: {remote}/{branch}"
        )

    base_sha = git_output(repository, "rev-parse", base)
    remote_sha = git_output(
        repository,
        "rev-parse",
        f"{remote}/{base}",
    )
    if base_sha != remote_sha:
        raise GitCommandError(
            f"{base} is not synchronized with {remote}/{base}"
        )

    print_section("CREATE PACKAGE BRANCH")
    run_git(
        repository,
        "switch",
        "-c",
        branch,
        capture_output=False,
    )

    print_section("PACKAGE STARTED")
    print(f"Branch : {current_branch(repository)}")
    print(f"Base   : {remote}/{base}")
    print(f"Commit : {git_output(repository, 'rev-parse', 'HEAD')}")
    print_git_output(
        repository,
        "status",
        "--short",
        "--branch",
    )
    return 0


def review_package(
    repository: Path,
    *,
    allowed: Sequence[str] = (),
    quality: bool = False,
    show_diff: bool = False,
) -> int:
    """Review working-tree scope and optionally run quality checks."""
    branch = current_branch(repository)
    if branch == "main":
        raise GitCommandError(
            "package review must run on a package branch"
        )

    paths = changed_paths(repository)
    untracked = untracked_paths(repository)
    if not paths:
        raise GitCommandError(
            "package review found no staged, unstaged or untracked changes"
        )

    print_section("PACKAGE STATUS")
    print_git_output(
        repository,
        "status",
        "--short",
        "--branch",
    )

    print_section("CHANGED PATHS")
    for path in paths:
        print(path)

    outside_scope = [
        path
        for path in paths
        if not path_is_allowed(path, allowed)
    ]

    if allowed:
        print_section("ALLOWED SCOPE")
        for item in allowed:
            print(item)

    print_section("DIFF CHECK")
    for arguments in (
        ("diff", "--check"),
        ("diff", "--cached", "--check"),
    ):
        completed = run_git(
            repository,
            *arguments,
            check=False,
            capture_output=False,
        )
        if completed.returncode != 0:
            raise GitCommandError(
                f"{' '.join(('git', *arguments))} failed"
            )
    print("PASS")

    print_section("DIFF STAT")
    print("Unstaged:")
    print_git_output(repository, "diff", "--stat")
    print("Staged:")
    print_git_output(repository, "diff", "--cached", "--stat")
    print("Untracked:")
    if untracked:
        for path in untracked:
            try:
                size = (repository / path).stat().st_size
            except OSError:
                print(f"{path} (unreadable)")
            else:
                print(f"{path} ({size} bytes)")
    else:
        print("(none)")

    if show_diff:
        print_section("UNSTAGED DIFF")
        print_git_output(repository, "diff", "--color=never")
        print_section("STAGED DIFF")
        print_git_output(
            repository,
            "diff",
            "--cached",
            "--color=never",
        )
        print_untracked_files(repository, untracked)

    if outside_scope:
        print_section("OUTSIDE ALLOWED SCOPE")
        for path in outside_scope:
            print(path)
        raise GitCommandError(
            "package contains changes outside the allowed scope"
        )

    if quality:
        print_section("QUALITY")
        quality_result = run_quality(repository)
        if quality_result != 0:
            return quality_result

    print_section("PACKAGE REVIEW")
    print("PASS")
    return 0


def finish_package(
    repository: Path,
    *,
    base_ref: str = "origin/main",
) -> int:
    """Verify a committed package before push or Pull Request creation."""
    branch = current_branch(repository)
    if branch == "main":
        raise GitCommandError(
            "package finish must run on a package branch"
        )

    ensure_clean(repository)

    base_check = run_git(
        repository,
        "rev-parse",
        "--verify",
        "--quiet",
        f"{base_ref}^{{commit}}",
        check=False,
    )
    if base_check.returncode != 0:
        raise GitCommandError(
            f"base reference does not exist: {base_ref}"
        )

    behind, ahead = ahead_behind(repository, base_ref)
    if ahead == 0:
        raise GitCommandError(
            f"branch has no commits ahead of {base_ref}"
        )
    if behind != 0:
        raise GitCommandError(
            f"branch is {behind} commit(s) behind {base_ref}"
        )

    diff_check = run_git(
        repository,
        "diff",
        "--check",
        f"{base_ref}...HEAD",
        check=False,
        capture_output=False,
    )
    if diff_check.returncode != 0:
        raise GitCommandError(
            "committed diff contains whitespace errors"
        )

    paths = committed_paths(repository, base_ref)

    print_section("PACKAGE FINISH")
    print(f"Branch : {branch}")
    print(f"Base   : {base_ref}")
    print(f"HEAD   : {git_output(repository, 'rev-parse', 'HEAD')}")
    print(f"Commits: {ahead}")
    print(f"Files  : {len(paths)}")

    print_section("COMMITS")
    print_git_output(
        repository,
        "log",
        "--oneline",
        "--decorate",
        f"{base_ref}..HEAD",
    )

    print_section("CHANGED PATHS")
    for path in paths:
        print(path)

    print_section("DIFF STAT")
    print_git_output(
        repository,
        "diff",
        "--stat",
        f"{base_ref}...HEAD",
    )

    upstream = run_git(
        repository,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
        check=False,
    )
    print_section("PUSH")
    if upstream.returncode == 0:
        upstream_name = upstream.stdout.strip()
        print(f"Upstream: {upstream_name}")
        print("Command : git push")
    else:
        print("Upstream: not configured")
        print(f"Command : git push -u origin {branch}")

    print_section("PACKAGE FINISH CHECK")
    print("PASS")
    return 0


def parse_args(
    argv: Sequence[str] | None = None,
) -> argparse.Namespace:
    """Parse package workflow arguments."""
    parser = argparse.ArgumentParser(
        description="Automate safe Git package workflow checks."
    )
    subparsers = parser.add_subparsers(
        dest="action",
        required=True,
    )

    start_parser = subparsers.add_parser(
        "start",
        help="Synchronize main and create a package branch.",
    )
    start_parser.add_argument("branch")
    start_parser.add_argument("--base", default="main")
    start_parser.add_argument("--remote", default="origin")

    review_parser = subparsers.add_parser(
        "review",
        help="Review scope, diffs and optional quality checks.",
    )
    review_parser.add_argument(
        "--allow",
        action="append",
        default=[],
        metavar="PATH",
        help=(
            "Allow a changed file or directory. Repeat for multiple "
            "scope entries."
        ),
    )
    review_parser.add_argument(
        "--quality",
        action="store_true",
        help="Run the complete local quality gate.",
    )
    review_parser.add_argument(
        "--show-diff",
        action="store_true",
        help="Print staged and unstaged diffs.",
    )

    finish_parser = subparsers.add_parser(
        "finish",
        help="Verify committed package state before push.",
    )
    finish_parser.add_argument(
        "--base-ref",
        default="origin/main",
    )

    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the selected package workflow action."""
    arguments = parse_args(argv)
    repository = repository_root()

    try:
        if arguments.action == "start":
            return start_package(
                repository,
                arguments.branch,
                base=arguments.base,
                remote=arguments.remote,
            )
        if arguments.action == "review":
            return review_package(
                repository,
                allowed=arguments.allow,
                quality=arguments.quality,
                show_diff=arguments.show_diff,
            )
        if arguments.action == "finish":
            return finish_package(
                repository,
                base_ref=arguments.base_ref,
            )
    except GitCommandError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        f"ERROR: unsupported workflow action: {arguments.action}",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
