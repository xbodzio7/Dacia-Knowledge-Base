#!/usr/bin/env python3
"""Resolve the next autonomous-maintainer action from a structured event."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import project_state


EVENT_VERSION = 1
DECISION_VERSION = 1
DEFAULT_STATE = Path("project/state.json")
STAGES = (
    "analysis",
    "implementation",
    "quality",
    "publication",
    "pull_request",
    "ci",
    "merge",
    "state_update",
)
OUTCOMES = ("pass", "fail", "blocked")
PASS_ACTIONS = {
    "analysis": "implement_package",
    "implementation": "run_tests_and_quality",
    "quality": "publish_package",
    "publication": "create_pull_request",
    "pull_request": "monitor_ci",
    "merge": "update_project_state_and_documentation",
    "state_update": "start_next_package",
}


class DecisionError(RuntimeError):
    """Raised when an autonomy event cannot be interpreted safely."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise DecisionError(f"cannot read {label} {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise DecisionError(f"invalid {label} JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise DecisionError(f"{label} root must be an object")
    return value


def _required_string(event: Mapping[str, Any], key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str) or not value.strip():
        raise DecisionError(f"event.{key} must be a non-empty string")
    return value


def _optional_boolean(event: Mapping[str, Any], key: str) -> bool | None:
    value = event.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise DecisionError(f"event.{key} must be a boolean when present")
    return value


def validate_event(event: Mapping[str, Any]) -> None:
    if event.get("version") != EVENT_VERSION:
        raise DecisionError(f"event.version must equal {EVENT_VERSION}")
    stage = _required_string(event, "stage")
    if stage not in STAGES:
        raise DecisionError(f"event.stage must be one of {list(STAGES)}")
    outcome = _required_string(event, "outcome")
    if outcome not in OUTCOMES:
        raise DecisionError(f"event.outcome must be one of {list(OUTCOMES)}")

    reason_code = event.get("reason_code")
    if reason_code is not None and (
        not isinstance(reason_code, str) or not reason_code.strip()
    ):
        raise DecisionError(
            "event.reason_code must be a non-empty string when present"
        )
    if outcome != "pass" and reason_code is None:
        raise DecisionError(
            "event.reason_code is required for fail or blocked outcomes"
        )

    in_scope = _optional_boolean(event, "in_scope")
    if outcome == "fail" and in_scope is None:
        raise DecisionError("event.in_scope is required for fail outcomes")

    for key in ("head_current", "checks_passed", "mergeable"):
        _optional_boolean(event, key)

    if stage == "ci" and outcome == "pass":
        for key in ("head_current", "checks_passed", "mergeable"):
            if event.get(key) is None:
                raise DecisionError(
                    f"event.{key} is required for a passing ci event"
                )


def _action_required(
    *,
    stage: str,
    reason_code: str,
    required_action: str,
    consequences: str,
) -> dict[str, Any]:
    return {
        "version": DECISION_VERSION,
        "disposition": "ACTION_REQUIRED",
        "stop": True,
        "action": None,
        "reason_code": reason_code,
        "action_required": {
            "reason": reason_code.replace("_", " "),
            "required_action": required_action,
            "options_and_consequences": consequences,
            "resume_stage": stage,
        },
    }


def _continue(
    disposition: str,
    action: str,
    reason_code: str | None = None,
) -> dict[str, Any]:
    return {
        "version": DECISION_VERSION,
        "disposition": disposition,
        "stop": False,
        "action": action,
        "reason_code": reason_code,
        "action_required": None,
    }


def resolve_decision(
    state: Mapping[str, Any],
    event: Mapping[str, Any],
) -> dict[str, Any]:
    """Return the deterministic next action for one workflow event."""
    project_state.validate_state(state)
    validate_event(event)

    stage = str(event["stage"])
    outcome = str(event["outcome"])
    reason_code = event.get("reason_code")
    stop_conditions = set(state["autonomy"]["stop_conditions"])

    if reason_code in stop_conditions:
        return _action_required(
            stage=stage,
            reason_code=str(reason_code),
            required_action=(
                "Resolve the named blocking condition or provide the missing "
                "decision, source, access or approval."
            ),
            consequences=(
                "Work cannot continue safely without this input; no unrelated "
                "package action will be taken."
            ),
        )

    if outcome == "blocked":
        return _action_required(
            stage=stage,
            reason_code=str(reason_code),
            required_action="Remove or decide the unresolved blocking condition.",
            consequences=(
                "The workflow remains paused at the current stage until the "
                "block is resolved."
            ),
        )

    if outcome == "fail":
        if event["in_scope"]:
            return _continue(
                "REPAIR_AND_RETRY",
                f"repair_{stage}_and_retry",
                str(reason_code),
            )
        return _action_required(
            stage=stage,
            reason_code="scope_expansion_beyond_current_milestone",
            required_action=(
                "Approve an expanded package scope or choose a separate package."
            ),
            consequences=(
                "Approving expansion changes the current manifest; choosing a "
                "separate package preserves the existing package boundary."
            ),
        )

    if stage == "ci":
        if not event["head_current"]:
            return _continue("CONTINUE", "reverify_pull_request_head")
        if not event["checks_passed"]:
            return _continue("REPAIR_AND_RETRY", "inspect_ci_and_repair")
        if not event["mergeable"]:
            return _continue("RETRY", "refresh_mergeability_and_retry")
        return _continue("CONTINUE", "merge_pull_request")

    return _continue("CONTINUE", PASS_ACTIONS[stage])


def render_json(value: Mapping[str, Any]) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        temporary.write_text(content, encoding="utf-8", newline="\n")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve CONTINUE, REPAIR_AND_RETRY, RETRY or ACTION_REQUIRED "
            "from one structured autonomous-maintainer event."
        )
    )
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--json", dest="json_path", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    repository = repository_root()
    state_path = arguments.state
    event_path = arguments.event
    if not state_path.is_absolute():
        state_path = repository / state_path
    if not event_path.is_absolute():
        event_path = repository / event_path

    try:
        state = project_state.read_state(state_path)
        event = read_json(event_path, "autonomy event")
        decision = resolve_decision(state, event)
        rendered = render_json(decision)
        if arguments.json_path is not None:
            write_atomic(arguments.json_path, rendered)
            print(f"Autonomy decision written to {arguments.json_path}")
        else:
            print(rendered, end="")
        return 2 if decision["stop"] else 0
    except (DecisionError, OSError, project_state.StateError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
