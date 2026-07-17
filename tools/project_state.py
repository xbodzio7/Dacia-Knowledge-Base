#!/usr/bin/env python3
"""Validate and synchronize canonical project state and documentation."""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence

import documentation_baseline


STATE_VERSION = 1
DEFAULT_STATE = Path("project/state.json")
DEFAULT_SUMMARY = Path("project/STATE_SUMMARY.md")
REQUIRED_REFERENCES = {
    "project/START_HERE.md": (
        "state.json",
        "STATE_SUMMARY.md",
        "AUTONOMOUS_MAINTAINER.md",
    ),
    "project/AUTONOMOUS_MAINTAINER.md": (
        "project/state.json",
        "ACTION_REQUIRED",
        "autonomous",
    ),
    "project/DOCUMENTATION_SYNC.md": (
        "project-state --check",
        "project-state --apply",
        "documentation-baseline",
    ),
}
STATE_BASELINE_FIELDS = {
    "tests": "tests",
    "csv_files": "csv_files",
    "rows": "master_rows",
    "configuration_values": "configuration_values",
    "configuration_import_specs": "configuration_import_specs",
    "availability_records": "configuration_availability",
    "attributes": "attributes",
    "attribute_categories": "attribute_categories",
}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
PACKAGE_STATUSES = {"planned", "active", "blocked", "complete"}


class StateError(RuntimeError):
    """Raised when canonical state is invalid or documentation has drifted."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise StateError(f"{label} must be an object")
    return value


def _string(mapping: Mapping[str, Any], key: str, label: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise StateError(f"{label}.{key} must be a non-empty string")
    return value


def _integer(mapping: Mapping[str, Any], key: str, label: str) -> int:
    value = mapping.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise StateError(f"{label}.{key} must be a positive integer")
    return value


def _boolean(mapping: Mapping[str, Any], key: str, label: str) -> bool:
    value = mapping.get(key)
    if not isinstance(value, bool):
        raise StateError(f"{label}.{key} must be a boolean")
    return value


def _string_list(
    mapping: Mapping[str, Any],
    key: str,
    label: str,
) -> list[str]:
    value = mapping.get(key)
    if not isinstance(value, list) or not value:
        raise StateError(f"{label}.{key} must be a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise StateError(f"{label}.{key} must contain non-empty strings")
    if len(value) != len(set(value)):
        raise StateError(f"{label}.{key} must not contain duplicates")
    return list(value)


def read_state(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise StateError(f"cannot read project state {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise StateError(f"invalid project state JSON {path}: {exc}") from exc
    return _object(value, "state")


def validate_state(state: Mapping[str, Any]) -> None:
    if state.get("version") != STATE_VERSION:
        raise StateError(f"state.version must equal {STATE_VERSION}")

    updated_on = _string(state, "updated_on", "state")
    try:
        date.fromisoformat(updated_on)
    except ValueError as exc:
        raise StateError("state.updated_on must be an ISO date") from exc

    repository = _object(state.get("repository"), "state.repository")
    _string(repository, "full_name", "state.repository")
    _string(repository, "default_branch", "state.repository")
    if repository.get("source_of_truth") != "repository":
        raise StateError(
            "state.repository.source_of_truth must equal 'repository'"
        )
    if repository.get("main_sha_tracking") != "dynamic":
        raise StateError(
            "state.repository.main_sha_tracking must equal 'dynamic'"
        )

    _string(state, "phase", "state")

    reference = _object(
        state.get("reference_delivery"),
        "state.reference_delivery",
    )
    _string(reference, "name", "state.reference_delivery")
    _integer(reference, "pull_request", "state.reference_delivery")
    head_sha = _string(reference, "head_sha", "state.reference_delivery")
    if SHA_RE.fullmatch(head_sha) is None:
        raise StateError(
            "state.reference_delivery.head_sha must be a lowercase 40-character SHA"
        )
    _integer(reference, "quality_run", "state.reference_delivery")

    baseline = _object(state.get("baseline"), "state.baseline")
    for key in STATE_BASELINE_FIELDS:
        _integer(baseline, key, "state.baseline")

    for key in ("current_package", "next_package"):
        package = _object(state.get(key), f"state.{key}")
        _string(package, "name", f"state.{key}")
        status = _string(package, "status", f"state.{key}")
        if status not in PACKAGE_STATUSES:
            raise StateError(
                f"state.{key}.status must be one of {sorted(PACKAGE_STATUSES)}"
            )
        _string(package, "goal", f"state.{key}")

    autonomy = _object(state.get("autonomy"), "state.autonomy")
    if autonomy.get("mode") != "autonomous_until_action_required":
        raise StateError(
            "state.autonomy.mode must equal "
            "'autonomous_until_action_required'"
        )
    _string_list(autonomy, "allowed_operations", "state.autonomy")
    _string_list(autonomy, "stop_conditions", "state.autonomy")
    action_fields = _string_list(
        autonomy,
        "action_required_fields",
        "state.autonomy",
    )
    expected_fields = [
        "reason",
        "required_action",
        "options_and_consequences",
        "resume_stage",
    ]
    if action_fields != expected_fields:
        raise StateError(
            "state.autonomy.action_required_fields must equal "
            f"{expected_fields}"
        )

    review = _object(state.get("review_policy"), "state.review_policy")
    if review.get("review_only_pull_requests") != "exception_only":
        raise StateError(
            "state.review_policy.review_only_pull_requests must equal "
            "'exception_only'"
        )
    _integer(
        review,
        "milestone_review_interval_packages",
        "state.review_policy",
    )
    _boolean(
        review,
        "one_logical_package_per_pull_request",
        "state.review_policy",
    )
    _boolean(
        review,
        "delete_remote_branches_automatically",
        "state.review_policy",
    )


def live_baseline_payload(
    value: documentation_baseline.Baseline,
) -> dict[str, int]:
    """Project the repository baseline into canonical state fields."""
    return {
        state_field: int(getattr(value, baseline_field))
        for state_field, baseline_field in STATE_BASELINE_FIELDS.items()
    }


def baseline_drift(
    state: Mapping[str, Any],
    value: documentation_baseline.Baseline,
) -> list[str]:
    """Return canonical baseline differences from the live repository."""
    current = _object(state.get("baseline"), "state.baseline")
    expected = live_baseline_payload(value)
    return [
        (
            f"project/state.json: baseline.{field} is {current.get(field)!r}; "
            f"live value is {expected_value}"
        )
        for field, expected_value in expected.items()
        if current.get(field) != expected_value
    ]


def synchronized_state(
    state: Mapping[str, Any],
    value: documentation_baseline.Baseline,
) -> dict[str, Any]:
    """Return a copy with live counters and the current update date."""
    result = copy.deepcopy(dict(state))
    result["baseline"] = live_baseline_payload(value)
    result["updated_on"] = date.today().isoformat()
    validate_state(result)
    return result


def render_summary(state: Mapping[str, Any]) -> str:
    repository = state["repository"]
    reference = state["reference_delivery"]
    baseline = state["baseline"]
    current = state["current_package"]
    following = state["next_package"]
    autonomy = state["autonomy"]
    review = state["review_policy"]

    def yes_no(value: bool) -> str:
        return "yes" if value else "no"

    lines = [
        "# Project State Summary",
        "",
        "> Generated from `project/state.json`. Do not edit manually.",
        "",
        "## Repository",
        "",
        f"- Repository: `{repository['full_name']}`",
        f"- Default branch: `{repository['default_branch']}`",
        f"- Source of truth: {repository['source_of_truth']}",
        f"- Main SHA tracking: {repository['main_sha_tracking']}",
        f"- State updated: {state['updated_on']}",
        "",
        "## Phase",
        "",
        f"**{state['phase']}**",
        "",
        "## Reference delivery",
        "",
        f"- Package: {reference['name']}",
        f"- Pull Request: #{reference['pull_request']}",
        f"- Verified head: `{reference['head_sha']}`",
        f"- Quality run: #{reference['quality_run']}",
        "",
        "## Verified baseline",
        "",
        f"- Tests: {baseline['tests']}",
        f"- Master CSV files: {baseline['csv_files']}",
        f"- Master rows: {baseline['rows']}",
        f"- Configuration values: {baseline['configuration_values']}",
        (
            "- Configuration import specifications: "
            f"{baseline['configuration_import_specs']}"
        ),
        f"- Availability records: {baseline['availability_records']}",
        f"- Canonical attributes: {baseline['attributes']}",
        f"- Attribute categories: {baseline['attribute_categories']}",
        "",
        "## Current package",
        "",
        f"**{current['name']}** — `{current['status']}`",
        "",
        current["goal"],
        "",
        "## Next package",
        "",
        f"**{following['name']}** — `{following['status']}`",
        "",
        following["goal"],
        "",
        "## Autonomy",
        "",
        f"Mode: `{autonomy['mode']}`",
        "",
        (
            "Standing authorization covers package branches, manifest-scoped "
            "edits, tests and quality, package commits, pushes, Pull Requests, "
            "in-scope CI repairs, green merges, state updates and generated "
            "documentation."
        ),
        "",
        (
            "Work stops only for a real source, access, authentication, policy, "
            "architecture, scope, destructive-operation or unresolved-evidence "
            "boundary. The stop message must begin with `ACTION_REQUIRED`."
        ),
        "",
        "## Review policy",
        "",
        (
            "- Review-only Pull Requests: "
            f"{review['review_only_pull_requests'].replace('_', ' ')}"
        ),
        (
            "- Milestone review interval: "
            f"{review['milestone_review_interval_packages']} logical packages"
        ),
        (
            "- One logical package per Pull Request: "
            f"{yes_no(review['one_logical_package_per_pull_request'])}"
        ),
        (
            "- Automatic remote-branch deletion: "
            f"{yes_no(review['delete_remote_branches_automatically'])}"
        ),
    ]
    return "\n".join(lines) + "\n"


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        temporary.write_text(content, encoding="utf-8", newline="\n")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def write_state(path: Path, state: Mapping[str, Any]) -> None:
    write_atomic(
        path,
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
    )


def check_references(repository: Path) -> list[str]:
    drift: list[str] = []
    for relative_path, required_values in REQUIRED_REFERENCES.items():
        path = repository / relative_path
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise StateError(f"cannot read {relative_path}: {exc}") from exc
        missing = [value for value in required_values if value not in text]
        if missing:
            drift.append(f"{relative_path}: missing {', '.join(missing)}")
    return drift


def project_drift(
    repository: Path,
    state: Mapping[str, Any],
    summary_path: Path,
    value: documentation_baseline.Baseline,
) -> list[str]:
    """Return state, generated-summary and managed-documentation drift."""
    drift = check_references(repository)
    drift.extend(baseline_drift(state, value))
    drift.extend(
        f"{path}: documentation baseline block differs"
        for path in documentation_baseline.check_documents(repository, value)
    )
    expected = render_summary(state)
    try:
        current = summary_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise StateError(f"cannot read project summary {summary_path}: {exc}") from exc
    if current != expected:
        drift.append(
            str(summary_path.relative_to(repository)).replace("\\", "/")
            + ": generated summary differs"
        )
    return sorted(set(drift))


def apply_synchronization(
    repository: Path,
    state_path: Path,
    summary_path: Path,
    state: Mapping[str, Any],
    value: documentation_baseline.Baseline,
) -> tuple[dict[str, Any], list[str]]:
    """Synchronize canonical counters, summary and managed document blocks."""
    synchronized = synchronized_state(state, value)
    changed = documentation_baseline.apply_documents(repository, value)
    write_state(state_path, synchronized)
    write_atomic(summary_path, render_summary(synchronized))
    changed.extend(
        [
            str(state_path.relative_to(repository)).replace("\\", "/"),
            str(summary_path.relative_to(repository)).replace("\\", "/"),
        ]
    )
    return synchronized, sorted(set(changed))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate canonical project state and verify or regenerate its "
            "baseline counters and human-readable documentation."
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    repository = repository_root()
    state_path = arguments.state
    summary_path = arguments.summary
    if not state_path.is_absolute():
        state_path = repository / state_path
    if not summary_path.is_absolute():
        summary_path = repository / summary_path

    try:
        state = read_state(state_path)
        validate_state(state)
        live = documentation_baseline.collect_baseline(repository)
        if arguments.apply:
            state, changed = apply_synchronization(
                repository,
                state_path,
                summary_path,
                state,
                live,
            )
            print("Synchronized project state and documentation:")
            for relative_path in changed:
                print(f"  {relative_path}")
        drift = project_drift(repository, state, summary_path, live)
        if drift:
            print("ERROR: project state drift detected:", file=sys.stderr)
            for item in drift:
                print(f"  {item}", file=sys.stderr)
            print(
                "Run: python tools/dkb.py project-state --apply",
                file=sys.stderr,
            )
            return 1
        print("Project state: PASS")
        print(f"Tests          : {live.tests}")
        print(f"Master rows    : {live.master_rows}")
        print(f"Phase          : {state['phase']}")
        print(f"Current package: {state['current_package']['name']}")
        print(f"Next package   : {state['next_package']['name']}")
        print(f"Autonomy mode  : {state['autonomy']['mode']}")
        return 0
    except (
        OSError,
        StateError,
        documentation_baseline.BaselineError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
