#!/usr/bin/env python3
"""Publish one exact manifest-driven package safely and reproducibly."""

from __future__ import annotations

import argparse
import io
import json
import sys
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import package_receipt
import package_workflow
from package_workflow import GitCommandError, PackageManifest


@dataclass(frozen=True)
class PublishPaths:
    output_dir: Path
    receipt: Path
    quality_log: Path
    publish_log: Path
    handoff: Path


class PublishLog:
    """Small console logger mirrored to the complete publication log."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("", encoding="utf-8", newline="\n")

    def write(self, message: str = "", *, console: bool = True) -> None:
        text = message.rstrip("\n")
        with self.path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(text + "\n")
        if console:
            print(text)

    def section(self, title: str) -> None:
        self.write()
        self.write(f"===== {title} =====")

    def append_file(self, title: str, path: Path) -> None:
        self.section(title)
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            self.write(f"[cannot read {path}: {exc}]", console=False)
            return
        with self.path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            if content and not content.endswith("\n"):
                stream.write("\n")


def _outside_path(repository: Path, path: Path) -> Path:
    return package_receipt.require_external_output(repository, path)


def resolve_publish_paths(
    repository: Path,
    manifest_path: Path,
    output_dir: Path | None,
    receipt_path: Path | None,
) -> PublishPaths:
    """Resolve all generated files outside the repository."""
    resolved_output = (
        output_dir.expanduser().resolve()
        if output_dir is not None
        else manifest_path.expanduser().resolve().parent
    )
    handoff = _outside_path(repository, resolved_output / "handoff.json")
    publish_log = _outside_path(
        repository, resolved_output / "package-publish.log"
    )
    quality_log = _outside_path(repository, resolved_output / "quality.log")
    receipt = _outside_path(
        repository,
        receipt_path
        if receipt_path is not None
        else resolved_output / "quality-receipt.json",
    )
    return PublishPaths(
        output_dir=resolved_output,
        receipt=receipt,
        quality_log=quality_log,
        publish_log=publish_log,
        handoff=handoff,
    )


def _handoff_template(manifest: PackageManifest) -> dict[str, Any]:
    return {
        "status": "FAIL",
        "phase": "start",
        "branch": manifest.branch,
        "base_sha": manifest.base_sha,
        "head_sha": None,
        "commit_message": manifest.commit_message,
        "paths": list(manifest.paths),
        "tests": None,
        "quality": "NOT_RUN",
        "package_review": "NOT_RUN",
        "package_finish": "NOT_RUN",
        "push": "NOT_REQUESTED",
        "exit_code": 1,
    }


def write_handoff(path: Path, payload: dict[str, Any]) -> None:
    """Write the stable publication handoff."""
    package_receipt.write_json_atomic(path, payload)


def _capture_finish(
    repository: Path,
    manifest: PackageManifest,
    base_ref: str,
    log: PublishLog,
) -> int:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        result = package_workflow.finish_package(
            repository,
            base_ref=base_ref,
            manifest=manifest,
        )
    output = stdout.getvalue()
    error = stderr.getvalue()
    if output:
        print(output, end="")
        with log.path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(output)
    if error:
        print(error, end="", file=sys.stderr)
        with log.path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(error)
    return result


def _ensure_empty_staging(repository: Path) -> None:
    staged = package_workflow.staged_paths(repository)
    if staged:
        raise GitCommandError(
            "package-publish requires an empty staging area before start: "
            f"{staged}"
        )


def _publication_mode(
    repository: Path,
    manifest: PackageManifest,
    base_ref: str,
) -> str:
    """Return precommit or committed for a safely resumable package."""
    branch = package_workflow.current_branch(repository)
    if branch != manifest.branch:
        raise GitCommandError(
            f"manifest branch is {manifest.branch!r}, current branch is {branch!r}"
        )
    package_workflow.verify_manifest_base(repository, manifest, base_ref)
    _ensure_empty_staging(repository)
    head = package_workflow.git_output(repository, "rev-parse", "HEAD")
    if head == manifest.base_sha:
        package_workflow.verify_review_manifest(
            repository,
            manifest,
            base_ref,
            package_workflow.changed_paths(repository),
        )
        return "precommit"

    package_workflow.ensure_clean(repository)
    package_workflow.verify_finish_manifest(repository, manifest, base_ref)
    return "committed"


def _ensure_receipt(
    repository: Path,
    manifest: PackageManifest,
    *,
    base_ref: str,
    paths: PublishPaths,
    mode: str,
    log: PublishLog,
) -> int:
    """Reuse an exact receipt or run quality and create a new one."""
    state = package_receipt.package_state(repository, manifest)
    validation = package_receipt.validate_receipt(
        paths.receipt,
        manifest,
        state,
    )
    if validation.valid:
        log.write(f"Quality receipt: PASS ({validation.tests} tests)")
        return validation.tests or 0

    log.write(f"Quality receipt rejected: {validation.reason}")
    result = package_receipt.run_quality_and_write_receipt(
        repository,
        manifest,
        base_ref=base_ref,
        receipt_path=paths.receipt,
        log_path=paths.quality_log,
        require_review_state=mode == "precommit",
    )
    log.append_file("FULL QUALITY LOG", paths.quality_log)
    if result != 0:
        raise GitCommandError(
            f"quality checks failed with exit code {result}"
        )

    state = package_receipt.package_state(repository, manifest)
    validation = package_receipt.validate_receipt(
        paths.receipt,
        manifest,
        state,
    )
    if not validation.valid or validation.tests is None:
        raise GitCommandError(
            "new quality receipt is invalid: "
            f"{validation.reason}"
        )
    log.write(f"Quality receipt created: PASS ({validation.tests} tests)")
    return validation.tests


def _stage_and_commit(
    repository: Path,
    manifest: PackageManifest,
    receipt_path: Path,
    log: PublishLog,
) -> str:
    """Stage exactly the manifest and create the one allowed commit."""
    _ensure_empty_staging(repository)
    package_workflow.exact_paths(
        package_workflow.changed_paths(repository),
        manifest.paths,
        label="working tree before staging",
    )
    state = package_receipt.package_state(repository, manifest)
    validation = package_receipt.validate_receipt(
        receipt_path,
        manifest,
        state,
    )
    if not validation.valid:
        raise GitCommandError(
            "quality receipt became invalid before staging: "
            f"{validation.reason}"
        )

    log.section("STAGING")
    package_workflow.run_git(
        repository,
        "add",
        "-A",
        "--",
        *manifest.paths,
    )
    package_workflow.exact_paths(
        package_workflow.staged_paths(repository),
        manifest.paths,
        label="staged",
    )
    remaining = sorted(
        set(package_workflow.unstaged_paths(repository))
        | set(package_workflow.untracked_paths(repository))
    )
    if remaining:
        raise GitCommandError(
            f"unstaged or untracked paths remain after exact staging: {remaining}"
        )
    cached_tree = package_workflow.git_output(repository, "write-tree")
    if cached_tree != state.tree_sha:
        raise GitCommandError(
            "staged tree differs from the quality receipt tree"
        )
    diff_check = package_workflow.run_git(
        repository,
        "diff",
        "--cached",
        "--check",
        check=False,
    )
    if diff_check.returncode != 0:
        detail = (diff_check.stderr or diff_check.stdout or "").strip()
        raise GitCommandError(
            "git diff --cached --check failed"
            + (f"\n{detail}" if detail else "")
        )
    log.write(f"Staged paths: {len(manifest.paths)}")

    log.section("COMMIT")
    completed = package_workflow.run_git(
        repository,
        "commit",
        "-m",
        manifest.commit_message,
        check=False,
    )
    if completed.stdout:
        log.write(completed.stdout, console=False)
    if completed.stderr:
        log.write(completed.stderr, console=False)
    if completed.returncode != 0:
        raise GitCommandError(
            f"git commit failed with exit code {completed.returncode}"
        )
    head = package_workflow.git_output(repository, "rev-parse", "HEAD")
    log.write(f"Commit: {head}")
    return head


def _push_branch(
    repository: Path,
    branch: str,
    log: PublishLog,
) -> None:
    log.section("PUSH")
    upstream = package_workflow.run_git(
        repository,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
        check=False,
    )
    arguments = ["push"] if upstream.returncode == 0 else [
        "push",
        "-u",
        "origin",
        branch,
    ]
    completed = package_workflow.run_git(
        repository,
        *arguments,
        check=False,
    )
    if completed.stdout:
        log.write(completed.stdout, console=False)
    if completed.stderr:
        log.write(completed.stderr, console=False)
    if completed.returncode != 0:
        raise GitCommandError(
            f"git {' '.join(arguments)} failed with exit code "
            f"{completed.returncode}"
        )

    remote_line = package_workflow.run_git(
        repository,
        "ls-remote",
        "--heads",
        "origin",
        f"refs/heads/{branch}",
        check=False,
    )
    head = package_workflow.git_output(repository, "rev-parse", "HEAD")
    remote_sha = remote_line.stdout.split()[0] if remote_line.stdout.strip() else ""
    if remote_line.returncode != 0 or remote_sha != head:
        raise GitCommandError(
            f"remote branch does not point to published HEAD {head}"
        )
    log.write(f"Remote HEAD: {remote_sha}")


def publish_package(
    repository: Path,
    manifest: PackageManifest,
    *,
    manifest_path: Path,
    base_ref: str = "origin/main",
    output_dir: Path | None = None,
    receipt_path: Path | None = None,
    push: bool = False,
) -> int:
    """Publish one exact package and always produce a structured handoff."""
    paths = resolve_publish_paths(
        repository,
        manifest_path,
        output_dir,
        receipt_path,
    )
    handoff = _handoff_template(manifest)
    if not push:
        handoff["push"] = "SKIPPED"
    log = PublishLog(paths.publish_log)

    try:
        log.section("PACKAGE PUBLISH")
        log.write(f"Branch : {manifest.branch}")
        log.write(f"Base   : {manifest.base_sha}")
        log.write(f"Subject: {manifest.commit_message}")
        log.write(f"Files  : {len(manifest.paths)}")

        handoff["phase"] = "review"
        mode = _publication_mode(repository, manifest, base_ref)
        handoff["package_review"] = "PASS"
        log.write(f"Mode   : {mode}")

        handoff["phase"] = "quality"
        tests = _ensure_receipt(
            repository,
            manifest,
            base_ref=base_ref,
            paths=paths,
            mode=mode,
            log=log,
        )
        handoff["tests"] = tests
        handoff["quality"] = "PASS"

        if mode == "precommit":
            handoff["phase"] = "commit"
            head = _stage_and_commit(
                repository,
                manifest,
                paths.receipt,
                log,
            )
        else:
            head = package_workflow.git_output(repository, "rev-parse", "HEAD")
            log.write(f"Existing package commit reused: {head}")
        handoff["head_sha"] = head

        handoff["phase"] = "finish"
        log.section("PACKAGE FINISH")
        finish_result = _capture_finish(
            repository,
            manifest,
            base_ref,
            log,
        )
        if finish_result != 0:
            raise GitCommandError(
                f"package-finish failed with exit code {finish_result}"
            )
        handoff["package_finish"] = "PASS"

        if push:
            handoff["phase"] = "push"
            _push_branch(repository, manifest.branch, log)
            handoff["push"] = "PASS"

        handoff["status"] = "PASS"
        handoff["phase"] = "complete"
        handoff["head_sha"] = package_workflow.git_output(
            repository, "rev-parse", "HEAD"
        )
        handoff["exit_code"] = 0
        write_handoff(paths.handoff, handoff)
        log.section("COMPLETE")
        log.write(f"Handoff: {paths.handoff}")
        log.write("PASS")
        return 0
    except (GitCommandError, OSError, ValueError, json.JSONDecodeError) as exc:
        try:
            handoff["head_sha"] = package_workflow.git_output(
                repository, "rev-parse", "HEAD"
            )
        except GitCommandError:
            handoff["head_sha"] = None
        failed_phase = handoff.get("phase")
        if failed_phase == "review":
            handoff["package_review"] = "FAIL"
        elif failed_phase == "quality":
            handoff["quality"] = "FAIL"
        elif failed_phase == "finish":
            handoff["package_finish"] = "FAIL"
        elif failed_phase == "push":
            handoff["push"] = "FAIL"
        handoff["status"] = "FAIL"
        handoff["exit_code"] = 1
        write_handoff(paths.handoff, handoff)
        log.section("FAIL")
        log.write(f"ERROR: {exc}", console=False)
        print(f"ERROR: {exc}", file=sys.stderr)
        print(f"Handoff: {paths.handoff}", file=sys.stderr)
        return 1


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publish one exact manifest-driven package."
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="External directory for log, receipt and handoff files.",
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        help="Existing or generated quality receipt path.",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Explicitly push the current package branch after finish.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    repository = package_workflow.repository_root()
    try:
        manifest = package_workflow.load_manifest(arguments.manifest)
    except GitCommandError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return publish_package(
        repository,
        manifest,
        manifest_path=arguments.manifest,
        base_ref=arguments.base_ref,
        output_dir=arguments.output_dir,
        receipt_path=arguments.receipt,
        push=arguments.push,
    )


if __name__ == "__main__":
    raise SystemExit(main())
