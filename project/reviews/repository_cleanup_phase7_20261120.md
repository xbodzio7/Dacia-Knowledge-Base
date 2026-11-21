# Repository cleanup phase 7 — Sandero rematerialization workflow

Date: 2026-11-20

## Decision

Retire `.github/workflows/ai-rematerialize-sandero-modal-reconciliation.yml` from the active workflow directory.

## Evidence

- The workflow is narrowly bound to the historical branch `ai/sandero-stepway-full-modal-reconciliation-001`.
- Its only documented purpose was to rematerialize the conservative Sandero/Sandero Stepway modal reconciliation from the 2026-08-09 snapshot.
- The corresponding PR #629 was merged on 2026-08-09 (merge commit `2cf23fc4fd1c30a2c3db5b3d5d1b7bb8e09c9d3d`).
- PR #629 records that the import and verification completed, the final local-equivalent suite passed at that time, and the resulting data was merged.
- The workflow has write permission to repository contents and commits/pushes data automatically. Leaving this one-off mechanism active after the completed reconciliation is not justified without a new explicitly scoped task.

## Safety boundary

- Only the workflow definition is retired.
- No branch is deleted or modified by this package.
- No Sandero source evidence, importer, import specification, master CSV, report, test, or historical package is deleted or modified.
- The historical importer remains available for reproducibility and controlled future re-runs.
- This change does not imply that the 2026-08-09 data should be rematerialized again.

## Verification

- PR #629 state and merge commit were checked through GitHub.
- No open PR matching the historical rematerialization task was found.
- This package is based directly on main at `66626ee8afa81b46a3c7bc5b97662cc6aa9e88bf`.
- No local tests are claimed. The required GitHub Actions checks must validate the exact PR head before review/merge.
- Protected `main` remains unchanged; this package must not be merged automatically.
