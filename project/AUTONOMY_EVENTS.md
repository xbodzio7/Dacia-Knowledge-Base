# Autonomous Workflow Events

## Purpose

The autonomous maintainer contract defines when work may continue and when user action is required. This document makes that boundary machine-readable and testable.

Use:

```bash
python tools/dkb.py autonomy-decision --event ../event.json
```

The command reads `project/state.json`, validates one event and returns the next action as deterministic JSON.

## Event format

```json
{
  "version": 1,
  "stage": "ci",
  "outcome": "pass",
  "head_current": true,
  "checks_passed": true,
  "mergeable": true
}
```

Controlled stages:

- `analysis`,
- `implementation`,
- `quality`,
- `publication`,
- `pull_request`,
- `ci`,
- `merge`,
- `state_update`.

Controlled outcomes:

- `pass`,
- `fail`,
- `blocked`.

A failed event must include `reason_code` and `in_scope`. A blocked event must include `reason_code`. Passing CI also requires `head_current`, `checks_passed` and `mergeable`.

## Decisions

The output uses one of these dispositions:

- `CONTINUE` — execute the returned action without asking for a generic continuation command;
- `REPAIR_AND_RETRY` — repair an in-scope problem and repeat the failed stage;
- `RETRY` — repeat a safe transient verification such as mergeability refresh;
- `ACTION_REQUIRED` — stop because repository evidence or standing authorization is insufficient.

Example successful CI decision:

```json
{
  "action": "merge_pull_request",
  "action_required": null,
  "disposition": "CONTINUE",
  "reason_code": null,
  "stop": false,
  "version": 1
}
```

## ACTION_REQUIRED

A reason code listed in `project/state.json` under `autonomy.stop_conditions` always produces `ACTION_REQUIRED`. The result contains exactly:

- `reason`,
- `required_action`,
- `options_and_consequences`,
- `resume_stage`.

Out-of-scope failures also produce `ACTION_REQUIRED` with reason code `scope_expansion_beyond_current_milestone`.

The command exits with:

- `0` for automatic continuation, repair or retry;
- `2` for a valid `ACTION_REQUIRED` decision;
- `1` for an invalid event, state or file.

## Stage progression

Normal successful progression is:

```text
analysis
→ implementation
→ quality
→ publication
→ pull_request
→ ci
→ merge
→ state_update
→ next package
```

At CI:

- stale head → `reverify_pull_request_head`,
- failed checks → `inspect_ci_and_repair`,
- temporarily non-mergeable PR → `refresh_mergeability_and_retry`,
- current green mergeable PR → `merge_pull_request`.

## Integration boundary

The command does not call GitHub or modify the repository. It resolves policy. ChatGPT Work, Codex, the GitHub connector or another orchestrator executes the returned action using the existing package, CI and merge safeguards.

This separation keeps policy deterministic while credentials and external side effects remain in their dedicated tools.
