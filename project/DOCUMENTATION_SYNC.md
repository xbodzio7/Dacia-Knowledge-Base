# Automated Documentation and Baseline Sync

## Purpose

Project counters and current operating state must not be copied manually between documents. The command below is the single synchronization entry point:

```bash
python tools/dkb.py project-state --check
```

To regenerate managed content from the live repository:

```bash
python tools/dkb.py project-state --apply
```

## Managed sources

The synchronization combines two existing sources:

1. `documentation-baseline` calculates live repository counters from tests, master CSV files, configuration data, catalogue data and SQLite-compatible master statistics.
2. `project/state.json` stores the project phase, package queue, reference delivery, autonomy boundary and review policy.

The live baseline always wins over copied counter values. `project-state --check` fails when any canonical counter differs from the repository.

## Managed outputs

`project-state --apply` updates:

- the `baseline` object in `project/state.json`,
- `project/STATE_SUMMARY.md`,
- managed `documentation-baseline` blocks in `README.md`,
- managed `documentation-baseline` blocks in `CHANGELOG.md`,
- managed `documentation-baseline` blocks in `project/ROADMAP.md`,
- managed `documentation-baseline` blocks in `project/SESSION_STATE.md`.

Writes use UTF-8, LF endings and atomic replacement.

## CI enforcement

Linux and Windows CI run `project-state --check` as an early preflight before unit/package tests on every supported Python matrix line and the Windows job. GitHub Actions supplies the expected repository name and default branch from the event; a Pull Request targeting a non-default branch is rejected. The check validates:

- the state schema and controlled values,
- exact agreement between canonical baseline and live repository counters,
- exact generated `STATE_SUMMARY.md` content,
- all managed documentation baseline blocks,
- required startup and autonomy-document references,
- consistency between `project/state.json` repository metadata and the active GitHub repository/default-branch context.

A Pull Request cannot pass Quality while these surfaces disagree. CI is check-only and never applies generated changes. The maintainer must inspect and apply the supported generator in the working branch, then rerun the checks on the exact candidate tree.

## Narrative documentation boundary

Only counters and the generated state summary are synchronized automatically in this package. Historical prose, sprint history and long-form architectural explanations remain versioned narrative documentation.

When narrative text conflicts with current package or phase information, startup rules require `project/state.json` and `project/STATE_SUMMARY.md` to be used. Migration of stale narrative current-sprint sections is a separate, bounded package so historical records are not rewritten accidentally.

## Workflow

At the start of work:

```bash
python tools/dkb.py project-state --check
```

After adding tests, data, attributes or import specifications:

```bash
python tools/dkb.py project-state --apply
python tools/dkb.py project-state --check
python tools/dkb.py documentation-baseline --check
```

The resulting state and documentation changes belong to the same logical package that changed the baseline. A separate counter-only cleanup Pull Request should normally be unnecessary. The Windows package tests are isolated in disposable repositories and local bare remotes; their deliberate failed-push and `extra.txt` cases are expected negative-path assertions, not real GitHub pushes.
