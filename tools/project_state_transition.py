#!/usr/bin/env python3
"""Validate legal package-state transitions and source-backed next-package selection."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
STATUS_TRANSITIONS = {
    "planned": {"planned", "active", "blocked", "complete"},
    "active": {"active", "blocked", "complete"},
    "blocked": {"blocked", "active", "complete"},
    "complete": {"complete"},
}
IDENTITY_FIELDS = ("package_id", "kind", "name", "goal", "source_paths")


class TransitionError(RuntimeError):
    """Raised when a proposed canonical package-state transition is unsafe."""


def _git(repository: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=repository,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise TransitionError(f"git {' '.join(arguments)} failed: {detail}")
    return result.stdout.strip()


def _package(state: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = state.get(key)
    if not isinstance(value, dict):
        raise TransitionError(f"state.{key} must be an object")
    for field in ("package_id", "kind", "name", "status", "goal"):
        item = value.get(field)
        if not isinstance(item, str) or not item.strip():
            raise TransitionError(f"state.{key}.{field} must be a non-empty string")
    if value["status"] not in STATUS_TRANSITIONS:
        raise TransitionError(f"state.{key}.status is invalid: {value['status']!r}")
    return value


def _safe_repository_file(repository: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise TransitionError(f"{label} must be a non-empty repository-relative path")
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts or "\\" in value:
        raise TransitionError(f"{label} is not a safe repository-relative path: {value!r}")
    root = repository.resolve()
    path = (root / Path(*relative.parts)).resolve()
    if not path.is_relative_to(root):
        raise TransitionError(f"{label} resolves outside the repository: {value!r}")
    if not path.is_file():
        raise TransitionError(f"{label} does not exist in the candidate tree: {value}")
    return path


def _changed_paths(repository: Path, base_ref: str, head_ref: str) -> set[str]:
    output = _git(repository, "diff", "--name-only", f"{base_ref}...{head_ref}")
    return {line.strip().replace("\\\\", "/") for line in output.splitlines() if line.strip()}


def _report_declares_completion(repository: Path, report_path: str) -> bool:
    path = _safe_repository_file(repository, report_path, "next_package.report_path")
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TransitionError(f"cannot read package completion report {report_path}: {exc}") from exc
    if not isinstance(report, dict):
        return False
    source = report.get("source")
    source = source if isinstance(source, dict) else {}
    statuses = {report.get("status"), report.get("coverage_state"), source.get("coverage_state")}
    return bool(statuses & {"complete", "completed", "fully_assimilated", "fully_assimilated_with_deferrals", "fully_reconciled"})


def _validate_completion(
    package: Mapping[str, Any],
    repository: Path,
    head_ref: str,
    *,
    changed_paths: set[str],
    pull_request_number: int | None,
) -> None:
    completion = package.get("completion")
    if not isinstance(completion, dict):
        raise TransitionError(
            "a package newly marked complete requires current_package.completion evidence"
        )
    pull_request = completion.get("pull_request")
    if not isinstance(pull_request, int) or isinstance(pull_request, bool) or pull_request < 1:
        raise TransitionError("completion.pull_request must be a positive integer")
    package_sha = completion.get("package_commit_sha")
    merge_sha = completion.get("merge_commit_sha")
    if package_sha is not None:
        if not isinstance(package_sha, str) or SHA_RE.fullmatch(package_sha) is None:
            raise TransitionError("completion.package_commit_sha must be a lowercase 40-character SHA")
        if pull_request_number is not None and pull_request != pull_request_number:
            raise TransitionError(
                f"completion.pull_request must match the current PR #{pull_request_number}"
            )
    elif not isinstance(merge_sha, str) or SHA_RE.fullmatch(merge_sha) is None:
        raise TransitionError(
            "completion requires a valid package_commit_sha (PR closeout) or merge_commit_sha (post-merge repair)"
        )
    completed_on = completion.get("completed_on")
    if not isinstance(completed_on, str):
        raise TransitionError("completion.completed_on must be an ISO date")
    try:
        date.fromisoformat(completed_on)
    except ValueError as exc:
        raise TransitionError("completion.completed_on must be an ISO date") from exc

    report_path = completion.get("report_path")
    _safe_repository_file(repository, report_path, "completion.report_path")
    package_report = package.get("report_path")
    if package_report and package_report != report_path:
        raise TransitionError(
            "completion.report_path must match current_package.report_path"
        )

    evidence_sha = package_sha or merge_sha
    if package_sha is None:
        message = _git(repository, "show", "-s", "--format=%B", merge_sha)
        if f"#{pull_request}" not in message:
            raise TransitionError(
                "completion merge commit message does not reference "
                f"the recorded PR #{pull_request}"
            )
    elif report_path not in changed_paths:
        raise TransitionError(
            "PR package closeout must change the exact current_package.report_path"
        )
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", evidence_sha, head_ref],
        cwd=repository,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if ancestor.returncode != 0:
        raise TransitionError(
            f"completion evidence commit {evidence_sha} is not an ancestor of candidate {head_ref}"
        )


def _validate_next_sources(package: Mapping[str, Any], repository: Path) -> None:
    paths = package.get("source_paths")
    source_kind = str(package.get("kind", "")).startswith("source_")
    if paths is None:
        if source_kind:
            raise TransitionError(
                "source-kind next_package must declare non-empty source_paths"
            )
        return
    if not isinstance(paths, list) or not paths:
        raise TransitionError("next_package.source_paths must be a non-empty list")
    if any(not isinstance(value, str) or not value.strip() for value in paths):
        raise TransitionError("next_package.source_paths must contain non-empty strings")
    if len(paths) != len(set(paths)):
        raise TransitionError("next_package.source_paths must not contain duplicates")
    for index, value in enumerate(paths):
        _safe_repository_file(
            repository,
            value,
            f"next_package.source_paths[{index}]",
        )


def _require_replanning(
    state: Mapping[str, Any],
    expected_from: str,
    expected_to: str,
) -> None:
    replan = state.get("package_replanning")
    if not isinstance(replan, dict):
        raise TransitionError(
            "current package skips previous next_package; add an explicit package_replanning record"
        )
    if (
        replan.get("from_package_id") != expected_from
        or replan.get("to_package_id") != expected_to
    ):
        raise TransitionError(
            "package_replanning from_package_id/to_package_id do not match the actual transition"
        )
    for field in ("reason", "decision_ref"):
        value = replan.get(field)
        if not isinstance(value, str) or not value.strip():
            raise TransitionError(f"package_replanning.{field} must be non-empty")


def validate_transition(
    previous: Mapping[str, Any],
    current: Mapping[str, Any],
    repository: Path,
    *,
    head_ref: str = "HEAD",
    base_ref: str | None = None,
    pull_request_number: int | None = None,
) -> None:
    """Validate one state change against the exact base state and candidate tree."""
    changed_paths = (
        _changed_paths(repository, base_ref, head_ref) if base_ref is not None else set()
    )
    old_current = _package(previous, "current_package")
    old_next = _package(previous, "next_package")
    new_current = _package(current, "current_package")
    new_next = _package(current, "next_package")

    old_id = old_current["package_id"]
    new_id = new_current["package_id"]
    old_status = old_current["status"]
    new_status = new_current["status"]

    if old_id == new_id:
        if new_status not in STATUS_TRANSITIONS[old_status]:
            raise TransitionError(
                f"illegal current_package status transition: {old_status} -> {new_status}"
            )
    else:
        if old_status != "complete":
            raise TransitionError(
                "cannot replace current_package while the previous current package is not complete"
            )
        if new_id != old_next["package_id"]:
            _require_replanning(current, str(old_next["package_id"]), str(new_id))
        selection = current.get("next_package_selection")
        rationale = current.get("rationale")
        if not isinstance(selection, str) or not selection.strip():
            raise TransitionError("package promotion requires next_package_selection")
        if not isinstance(rationale, str) or not rationale.strip():
            raise TransitionError("package promotion requires a non-empty rationale")

    old_next_report = old_next.get("report_path")
    if (
        isinstance(old_next_report, str)
        and old_next_report in changed_paths
        and _report_declares_completion(repository, old_next_report)
        and (new_id != old_next["package_id"] or new_status != "complete")
    ):
        raise TransitionError(
            "the current next_package report declares completion, but project/state.json "
            "does not promote that package to current_package=complete in the same PR"
        )

    if new_status == "complete":
        if old_id != new_id or old_status != "complete":
            _validate_completion(
                new_current,
                repository,
                head_ref,
                changed_paths=changed_paths,
                pull_request_number=pull_request_number,
            )
        elif new_current.get("completion") is not None:
            _validate_completion(
                new_current,
                repository,
                head_ref,
                changed_paths=changed_paths,
                pull_request_number=pull_request_number,
            )
    elif new_current.get("completion") is not None:
        raise TransitionError("current_package.completion is allowed only for a complete package")

    identity_changed = any(
        old_next.get(field) != new_next.get(field)
        for field in IDENTITY_FIELDS
    )
    if identity_changed and old_id == new_id:
        selection = current.get("next_package_selection")
        rationale = current.get("rationale")
        if (
            not isinstance(selection, str)
            or not selection.strip()
            or selection == previous.get("next_package_selection")
        ):
            raise TransitionError(
                "changing next_package identity/scope requires a new next_package_selection"
            )
        if (
            not isinstance(rationale, str)
            or not rationale.strip()
            or rationale == previous.get("rationale")
        ):
            raise TransitionError(
                "changing next_package identity/scope requires a new rationale"
            )
    _validate_next_sources(new_next, repository)


def self_test() -> int:
    """Exercise completed-report detection and exact PR-bound closeout evidence."""
    with tempfile.TemporaryDirectory(prefix="dkb-state-transition-") as temporary:
        repository = Path(temporary)
        _git(repository, "init", "-b", "main")
        _git(repository, "config", "user.name", "DKB lifecycle self-test")
        _git(repository, "config", "user.email", "dkb-self-test@example.invalid")
        report = repository / "reports" / "package.json"
        report.parent.mkdir(parents=True)
        report.write_text(json.dumps({"status": "in_progress"}) + "\n", encoding="utf-8")
        _git(repository, "add", ".")
        _git(repository, "commit", "-m", "test: create package report")
        base_ref = _git(repository, "rev-parse", "HEAD")

        report.write_text(
            json.dumps({"status": "fully_assimilated_with_deferrals"}) + "\\n",
            encoding="utf-8",
        )
        _git(repository, "add", ".")
        _git(repository, "commit", "-m", "test: complete package report")
        package_sha = _git(repository, "rev-parse", "HEAD")

        previous = {
            "current_package": {
                "package_id": "previous",
                "kind": "review",
                "name": "Previous",
                "status": "complete",
                "goal": "Previous package",
            },
            "next_package": {
                "package_id": "candidate",
                "kind": "review",
                "name": "Candidate",
                "status": "active",
                "goal": "Candidate package",
                "report_path": "reports/package.json",
            },
        }
        try:
            validate_transition(
                previous,
                previous,
                repository,
                head_ref="HEAD",
                base_ref=base_ref,
                pull_request_number=123,
            )
        except TransitionError as exc:
            if "does not promote" not in str(exc):
                raise
        else:
            raise TransitionError("completed next-package report was not required to close")

        promoted = {
            "current_package": {
                **previous["next_package"],
                "status": "complete",
                "completion": {
                    "pull_request": 123,
                    "package_commit_sha": package_sha,
                    "completed_on": "2026-11-25",
                    "report_path": "reports/package.json",
                },
            },
            "next_package": {
                "package_id": "following",
                "kind": "review",
                "name": "Following",
                "status": "planned",
                "goal": "Following package",
            },
            "next_package_selection": "Following package",
            "rationale": "Selected from the verified repository backlog.",
        }
        validate_transition(
            previous,
            promoted,
            repository,
            head_ref="HEAD",
            base_ref=base_ref,
            pull_request_number=123,
        )
        try:
            validate_transition(
                previous,
                promoted,
                repository,
                head_ref="HEAD",
                base_ref=base_ref,
                pull_request_number=124,
            )
        except TransitionError as exc:
            if "must match the current PR" not in str(exc):
                raise
        else:
            raise TransitionError("completion evidence accepted the wrong PR number")
    print("PROJECT STATE TRANSITION SELF-TEST: PASS")
    return 0


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TransitionError(f"cannot read candidate state {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise TransitionError("candidate project/state.json must contain an object")
    return value


def _read_base_state(repository: Path, base_ref: str) -> dict[str, Any]:
    raw = _git(repository, "show", f"{base_ref}:project/state.json")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TransitionError(f"base state at {base_ref} is invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise TransitionError(f"base state at {base_ref} must contain an object")
    return value


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref")
    parser.add_argument("--head-ref", default="HEAD")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--pull-request-number", type=int)
    parser.add_argument(
        "--repository",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.base_ref:
        parser.error("--base-ref is required unless --self-test is used")
    repository = args.repository.resolve()
    try:
        previous = _read_base_state(repository, args.base_ref)
        current = _read_json(repository / "project" / "state.json")
        validate_transition(
            previous,
            current,
            repository,
            head_ref=args.head_ref,
            base_ref=args.base_ref,
            pull_request_number=args.pull_request_number,
        )
    except (OSError, TransitionError) as exc:
        print(f"PROJECT STATE TRANSITION: FAIL\n{exc}", file=sys.stderr)
        return 1
    print("PROJECT STATE TRANSITION: PASS")
    print(f"Base state: {args.base_ref}")
    print(f"Candidate: {args.head_ref}")
    print(f"Current package: {current['current_package']['name']}")
    print(f"Next package: {current['next_package']['name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
