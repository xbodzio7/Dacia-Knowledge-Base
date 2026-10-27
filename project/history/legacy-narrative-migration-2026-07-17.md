# Legacy Narrative Documentation Migration

## Purpose

This record preserves the boundary between the former narrative current-state documents and the canonical machine-readable project state introduced in July 2026.

Before this migration, `project/ROADMAP.md` and `project/SESSION_STATE.md` mixed three different concerns:

- durable project direction,
- historical sprint records,
- volatile current package and repository status.

The volatile sections became stale after later Pull Requests because they duplicated information that was already available from Git and GitHub.

## Historical snapshot

The complete pre-migration versions of both active documents remain available in Git at commit:

```text
bceab5405a294b0b785b4fd206f3af37e164e85c
```

Relevant paths at that commit:

- `project/ROADMAP.md`,
- `project/SESSION_STATE.md`.

The detailed package history is also preserved in:

- merged Pull Requests,
- `project/reviews/`,
- `CHANGELOG.md`,
- repository commit history.

No historical delivery record was rewritten or discarded by this migration.

## New boundary

After this migration:

- `project/state.json` is the canonical machine-readable current state,
- `project/STATE_SUMMARY.md` is its generated human-readable projection,
- `project/ROADMAP.md` contains durable direction and backlog only,
- `project/SESSION_STATE.md` contains stable operating rules and the verified baseline only,
- current and next package names are not duplicated in narrative documents.

Use:

```bash
python tools/dkb.py project-state --check
```

to verify state, counters, managed documentation blocks and the generated summary.
