#!/usr/bin/env python3
"""Automate safe Git package workflows for Dacia Knowledge Base."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


class GitCommandError(RuntimeError):
    """Raised when a required Git command fails."""


@dataclass(frozen=True)
class PackageManifest:
    """Validated package workflow contract."""

    branch: str
    base_sha: str
    commit_message: str
    paths: tuple[str, ...]
    expected_commits: int = 1


GIT_CONTEXT_VARIABLES = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_COMMON_DIR",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
)


def git_environment(
    extra: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Return a deterministic UTF-8 environment without ambient Git context."""
    environment = os.environ.copy()
    for variable in GIT_CONTEXT_VARIABLES:
        environment.pop(variable, None)
    environment["PYTHONUTF8"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["LANG"] = "C.UTF-8"
    environment["LC_ALL"] = "C.UTF-8"
    if extra:
        environment.update(extra)
    return environment


def repository_root() -> Path:
    """Return the repository root containing this script."""
    return Path(__file__).resolve().parent.parent


def run_git(
    repository: Path,
    *arguments: str,
    check: bool = True,
    capture_output: bool = True,
    extra_environment: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run Git with deterministic UTF-8 text decoding."""
    command = ["git", *arguments]
    try:
        completed = subprocess.run(
            command,
            cwd=repository,
            env=git_environment(extra_environment),
            check=False,
            capture_output=capture_output,
            text=True,
            encoding="utf-8",
            errors="replace",
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


def run_git_bytes(
    repository: Path,
    *arguments: str,
    check: bool = True,
    extra_environment: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[bytes]:
    """Run Git and preserve byte-exact NUL-separated path output."""
    command = ["git", *arguments]
    try:
        completed = subprocess.run(
            command,
            cwd=repository,
            env=git_environment(extra_environment),
            check=False,
            capture_output=True,
        )
    except OSError as exc:
        raise GitCommandError(
            f"cannot run {' '.join(command)!r}: {exc}"
        ) from exc

    if check and completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or b"").decode(
            "utf-8", errors="replace"
        ).strip()
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
        raise GitCommandError(f"working tree is not clean:\n{status}")


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
    extra_environment: Mapping[str, str] | None = None,
) -> set[str]:
    """Return UTF-8 paths from byte-exact NUL-separated Git output."""
    output = run_git_bytes(
        repository,
        *arguments,
        extra_environment=extra_environment,
    ).stdout
    paths: set[str] = set()
    for raw_path in output.split(b"\0"):
        if not raw_path:
            continue
        try:
            path = raw_path.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise GitCommandError(
                "Git returned a path that is not valid UTF-8"
            ) from exc
        paths.add(path.replace("\\", "/"))
    return paths


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


def staged_paths(repository: Path) -> list[str]:
    """Return staged paths."""
    return sorted(
        null_separated_paths(
            repository,
            "diff",
            "--cached",
            "--name-only",
            "-z",
        )
    )


def unstaged_paths(repository: Path) -> list[str]:
    """Return tracked unstaged paths."""
    return sorted(
        null_separated_paths(
            repository,
            "diff",
            "--name-only",
            "-z",
        )
    )


def changed_paths(repository: Path) -> list[str]:
    """Return staged, unstaged and untracked paths."""
    return sorted(
        set(staged_paths(repository))
        | set(unstaged_paths(repository))
        | set(untracked_paths(repository))
    )


def committed_paths(repository: Path, base_ref: str) -> list[str]:
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


def normalize_manifest_path(path: str) -> str:
    """Validate and normalize one repository-relative manifest path."""
    normalized = path.replace("\\", "/").strip()
    if (
        not normalized
        or normalized.startswith("/")
        or re.match(r"^[A-Za-z]:", normalized)
    ):
        raise GitCommandError(
            f"manifest path must be repository-relative: {path!r}"
        )
    parts = normalized.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise GitCommandError(f"invalid manifest path: {path!r}")
    return normalized


def load_manifest(path: Path) -> PackageManifest:
    """Load and validate a package manifest JSON file."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise GitCommandError(
            f"cannot read package manifest {path}: {exc}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise GitCommandError(
            f"invalid package manifest JSON {path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise GitCommandError("package manifest root must be an object")

    allowed_keys = {
        "version",
        "branch",
        "base_sha",
        "commit_message",
        "expected_commits",
        "paths",
    }
    unknown_keys = sorted(set(payload) - allowed_keys)
    if unknown_keys:
        raise GitCommandError(
            f"unknown package manifest fields: {unknown_keys}"
        )
    if payload.get("version") != 1:
        raise GitCommandError("package manifest version must be 1")

    branch = payload.get("branch")
    base_sha = payload.get("base_sha")
    commit_message = payload.get("commit_message")
    expected_commits = payload.get("expected_commits", 1)
    raw_paths = payload.get("paths")

    if not isinstance(branch, str) or not branch.strip():
        raise GitCommandError("manifest branch must be a non-empty string")
    if (
        not isinstance(base_sha, str)
        or re.fullmatch(r"[0-9a-f]{40}", base_sha) is None
    ):
        raise GitCommandError(
            "manifest base_sha must be a lowercase 40-character SHA"
        )
    if (
        not isinstance(commit_message, str)
        or not commit_message.strip()
        or "\n" in commit_message
        or "\r" in commit_message
    ):
        raise GitCommandError(
            "manifest commit_message must be one non-empty line"
        )
    if expected_commits != 1:
        raise GitCommandError(
            "package workflow requires expected_commits = 1"
        )
    if not isinstance(raw_paths, list) or not raw_paths:
        raise GitCommandError("manifest paths must be a non-empty list")
    if not all(isinstance(item, str) for item in raw_paths):
        raise GitCommandError("manifest paths must contain only strings")

    paths = tuple(normalize_manifest_path(item) for item in raw_paths)
    if len(set(paths)) != len(paths):
        raise GitCommandError("manifest paths must be unique")
    return PackageManifest(
        branch=branch.strip(),
        base_sha=base_sha,
        commit_message=commit_message.strip(),
        paths=paths,
        expected_commits=expected_commits,
    )


def exact_paths(
    actual: Sequence[str],
    expected: Sequence[str],
    *,
    label: str,
) -> None:
    """Require an exact path manifest match."""
    actual_paths = sorted(actual)
    expected_paths = sorted(expected)
    if actual_paths != expected_paths:
        raise GitCommandError(
            f"{label} path manifest differs\n"
            f"expected: {expected_paths}\n"
            f"actual:   {actual_paths}"
        )


def verify_manifest_base(
    repository: Path,
    manifest: PackageManifest,
    base_ref: str,
) -> None:
    """Require the configured remote base to equal the manifest SHA."""
    base_check = run_git(
        repository,
        "rev-parse",
        "--verify",
        "--quiet",
        f"{base_ref}^{{commit}}",
        check=False,
    )
    if base_check.returncode != 0:
        raise GitCommandError(f"base reference does not exist: {base_ref}")
    actual_base_sha = git_output(
        repository,
        "rev-parse",
        f"{base_ref}^{{commit}}",
    )
    if actual_base_sha != manifest.base_sha:
        raise GitCommandError(
            f"{base_ref} moved: expected {manifest.base_sha}, "
            f"found {actual_base_sha}"
        )


def verify_review_manifest(
    repository: Path,
    manifest: PackageManifest,
    base_ref: str,
    paths: Sequence[str],
) -> None:
    """Require exact pre-commit branch, base, HEAD and path state."""
    branch = current_branch(repository)
    if branch != manifest.branch:
        raise GitCommandError(
            f"manifest branch is {manifest.branch!r}, "
            f"current branch is {branch!r}"
        )
    verify_manifest_base(repository, manifest, base_ref)
    head_sha = git_output(repository, "rev-parse", "HEAD")
    if head_sha != manifest.base_sha:
        raise GitCommandError(
            "pre-commit HEAD must equal manifest base SHA "
            f"{manifest.base_sha}; found {head_sha}"
        )
    exact_paths(paths, manifest.paths, label="working tree")


def verify_finish_manifest(
    repository: Path,
    manifest: PackageManifest,
    base_ref: str,
) -> list[str]:
    """Require the exact one-commit package contract."""
    branch = current_branch(repository)
    if branch != manifest.branch:
        raise GitCommandError(
            f"manifest branch is {manifest.branch!r}, "
            f"current branch is {branch!r}"
        )
    verify_manifest_base(repository, manifest, base_ref)
    ahead = int(
        git_output(
            repository,
            "rev-list",
            "--count",
            f"{manifest.base_sha}..HEAD",
        )
    )
    if ahead != manifest.expected_commits:
        raise GitCommandError(
            f"expected exactly {manifest.expected_commits} commit(s) "
            f"after {manifest.base_sha}; found {ahead}"
        )
    parent_sha = git_output(repository, "rev-parse", "HEAD^")
    if parent_sha != manifest.base_sha:
        raise GitCommandError(
            f"package commit parent must equal {manifest.base_sha}; "
            f"found {parent_sha}"
        )
    subject = git_output(repository, "log", "-1", "--pretty=%s")
    if subject != manifest.commit_message:
        raise GitCommandError(
            "commit subject differs\n"
            f"expected: {manifest.commit_message}\n"
            f"actual:   {subject}"
        )
    paths = committed_paths(repository, manifest.base_sha)
    exact_paths(paths, manifest.paths, label="committed")
    return paths


def path_is_allowed(path: str, allowed: Sequence[str]) -> bool:
    """Return whether a path is covered by an allowed file or directory."""
    if not allowed:
        return True
    normalized_path = path.replace("\\", "/")
    for candidate in allowed:
        normalized_candidate = candidate.replace("\\", "/").rstrip("/")
        if not normalized_candidate:
            continue
        if normalized_path == normalized_candidate:
            return True
        if normalized_path.startswith(f"{normalized_candidate}/"):
            return True
    return False


def ahead_behind(repository: Path, base_ref: str) -> tuple[int, int]:
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


def print_git_output(repository: Path, *arguments: str) -> None:
    """Print output from a Git command when it is not empty."""
    output = git_output(repository, *arguments)
    if output:
        print(output)


def print_untracked_files(repository: Path, paths: Sequence[str]) -> None:
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
            env=git_environment(),
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
        raise GitCommandError(f"package start requires branch {base!r}")
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
        raise GitCommandError(f"local branch already exists: {branch}")
    if ref_exists(repository, remote_ref):
        raise GitCommandError(
            f"remote branch already exists: {remote}/{branch}"
        )

    base_sha = git_output(repository, "rev-parse", base)
    remote_sha = git_output(repository, "rev-parse", f"{remote}/{base}")
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
    print_git_output(repository, "status", "--short", "--branch")
    return 0


def review_package(
    repository: Path,
    *,
    allowed: Sequence[str] = (),
    manifest: PackageManifest | None = None,
    base_ref: str = "origin/main",
    quality: bool = False,
    show_diff: bool = False,
    receipt_path: Path | None = None,
    quality_log: Path | None = None,
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

    if manifest is not None:
        if allowed:
            raise GitCommandError(
                "--allow cannot be combined with --manifest"
            )
        verify_review_manifest(repository, manifest, base_ref, paths)
        allowed = manifest.paths
        print_section("PACKAGE MANIFEST")
        print(f"Branch : {manifest.branch}")
        print(f"Base   : {manifest.base_sha}")
        print(f"Subject: {manifest.commit_message}")
        print(f"Files  : {len(manifest.paths)}")
    elif receipt_path is not None or quality_log is not None:
        raise GitCommandError(
            "quality receipt options require --manifest"
        )

    print_section("PACKAGE STATUS")
    print_git_output(repository, "status", "--short", "--branch")
    print_section("CHANGED PATHS")
    for path in paths:
        print(path)

    outside_scope = [
        path for path in paths if not path_is_allowed(path, allowed)
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
        if manifest is not None and receipt_path is not None:
            from package_receipt import run_quality_and_write_receipt

            quality_result = run_quality_and_write_receipt(
                repository,
                manifest,
                base_ref=base_ref,
                receipt_path=receipt_path,
                log_path=quality_log,
            )
        else:
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
    manifest: PackageManifest | None = None,
) -> int:
    """Verify a committed package before push or Pull Request creation."""
    branch = current_branch(repository)
    if branch == "main":
        raise GitCommandError(
            "package finish must run on a package branch"
        )
    ensure_clean(repository)

    if manifest is not None:
        paths = verify_finish_manifest(repository, manifest, base_ref)
        comparison_ref = manifest.base_sha
        ahead = manifest.expected_commits
    else:
        base_check = run_git(
            repository,
            "rev-parse",
            "--verify",
            "--quiet",
            f"{base_ref}^{{commit}}",
            check=False,
        )
        if base_check.returncode != 0:
            raise GitCommandError(f"base reference does not exist: {base_ref}")
        behind, ahead = ahead_behind(repository, base_ref)
        if ahead == 0:
            raise GitCommandError(
                f"branch has no commits ahead of {base_ref}"
            )
        if behind != 0:
            raise GitCommandError(
                f"branch is {behind} commit(s) behind {base_ref}"
            )
        comparison_ref = base_ref
        paths = committed_paths(repository, base_ref)

    diff_check = run_git(
        repository,
        "diff",
        "--check",
        f"{comparison_ref}...HEAD",
        check=False,
        capture_output=False,
    )
    if diff_check.returncode != 0:
        raise GitCommandError(
            "committed diff contains whitespace errors"
        )

    print_section("PACKAGE FINISH")
    print(f"Branch : {branch}")
    print(f"Base   : {comparison_ref}")
    print(f"HEAD   : {git_output(repository, 'rev-parse', 'HEAD')}")
    print(f"Commits: {ahead}")
    print(f"Files  : {len(paths)}")
    if manifest is not None:
        print(f"Subject: {manifest.commit_message}")
        print("Manifest: PASS")

    print_section("COMMITS")
    print_git_output(
        repository,
        "log",
        "--oneline",
        "--decorate",
        f"{comparison_ref}..HEAD",
    )
    print_section("CHANGED PATHS")
    for path in paths:
        print(path)
    print_section("DIFF STAT")
    print_git_output(
        repository,
        "diff",
        "--stat",
        f"{comparison_ref}...HEAD",
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


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse package workflow arguments."""
    parser = argparse.ArgumentParser(
        description="Automate safe Git package workflow checks."
    )
    subparsers = parser.add_subparsers(dest="action", required=True)

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
        "--manifest",
        type=Path,
        help="Validate exact branch, base SHA, subject and path manifest.",
    )
    review_parser.add_argument(
        "--base-ref",
        default="origin/main",
        help="Remote base ref that must equal the manifest base SHA.",
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
    review_parser.add_argument(
        "--receipt",
        type=Path,
        help=(
            "Write a reusable quality receipt. Requires --manifest and "
            "--quality. Defaults beside the manifest."
        ),
    )
    review_parser.add_argument(
        "--quality-log",
        type=Path,
        help=(
            "Write the full quality log. Requires --manifest and "
            "--quality. Defaults beside the manifest."
        ),
    )

    finish_parser = subparsers.add_parser(
        "finish",
        help="Verify committed package state before push.",
    )
    finish_parser.add_argument("--base-ref", default="origin/main")
    finish_parser.add_argument(
        "--manifest",
        type=Path,
        help="Validate the exact one-commit package contract.",
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
            manifest = (
                load_manifest(arguments.manifest)
                if arguments.manifest is not None
                else None
            )
            if (
                (arguments.receipt is not None or arguments.quality_log is not None)
                and (arguments.manifest is None or not arguments.quality)
            ):
                raise GitCommandError(
                    "--receipt and --quality-log require --manifest --quality"
                )
            receipt_path = arguments.receipt
            quality_log = arguments.quality_log
            if manifest is not None and arguments.quality:
                receipt_path = receipt_path or arguments.manifest.with_name(
                    "quality-receipt.json"
                )
                quality_log = quality_log or arguments.manifest.with_name(
                    "quality.log"
                )
            return review_package(
                repository,
                allowed=arguments.allow,
                manifest=manifest,
                base_ref=arguments.base_ref,
                quality=arguments.quality,
                show_diff=arguments.show_diff,
                receipt_path=receipt_path,
                quality_log=quality_log,
            )
        if arguments.action == "finish":
            manifest = (
                load_manifest(arguments.manifest)
                if arguments.manifest is not None
                else None
            )
            return finish_package(
                repository,
                base_ref=arguments.base_ref,
                manifest=manifest,
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
