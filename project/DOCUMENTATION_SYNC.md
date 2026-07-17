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

Linux and Windows CI run `project-state --check`. The check validates:

- the state schema and controlled values,
- exact agreement between canonical baseline and live repository counters,
- exact generated `STATE_SUMMARY.md` content,
- all managed documentation baseline blocks,
- required startup and autonomy-document references.

A Pull Request cannot pass Quality while these surfaces disagree.

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
```

The resulting state and documentation changes belong to the same logical package that changed the baseline. A separate counter-only cleanup Pull Request should normally be unnecessary.
