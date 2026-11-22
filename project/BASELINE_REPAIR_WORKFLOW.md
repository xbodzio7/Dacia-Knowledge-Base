# Canonical Baseline Repair Workflow

## Purpose

Use the GitHub Actions workflow **Repository Baselines** to regenerate repository-owned counters and managed documentation on an exact open pull-request head when local repository execution is unavailable.

This is a repair operation, not a bypass of validation. The workflow runs the canonical generators and then reruns both required checks on the same candidate tree.

## Scope

The workflow may write only these six generated files:

- `project/state.json`
- `project/STATE_SUMMARY.md`
- `README.md`
- `CHANGELOG.md`
- `project/ROADMAP.md`
- `project/SESSION_STATE.md`

It must never edit master data, source files, package manifests, tests, code, workflow definitions or arbitrary paths.

## Security model

The workflow must be dispatched from the protected `main` branch (never from the PR branch) and requires the PR number, exact head branch, and exact current 40-character head SHA. The workflow file must already be present on `main` before it is used. This means it cannot safely repair the PR that first introduces this workflow; it is available for later PRs after the workflow has been merged.

1. A maintainer selects `main` as the workflow ref. The read-only job verifies that the PR is open, targets `main`, belongs to this repository (fork PRs are rejected), and still has the supplied branch and head SHA.
2. The trusted workflow definition from `main` checks out that immutable PR SHA and runs only the canonical project-state/documentation generators and their check commands.
3. It rejects any changed path outside the six-file allowlist and uploads only those generated text files.
4. A separate job defined by the trusted `main` workflow receives `contents: write`, but does not check out or execute PR code. It re-fetches the PR, verifies the same branch and exact head SHA again, validates the allowlisted artifact files, creates a commit whose sole parent is the expected head, and updates the PR branch without force.
5. If the PR head changes during the run, the final update is rejected rather than overwriting newer work.

The artifact is data only; the write-enabled job never executes scripts or commands from it. Do not add broader paths or permissions without a separate security review.

## How to run

1. Open the PR and copy its current **head commit SHA** (not the merge commit SHA).
2. Open the repository's **Actions** tab and select **Repository Baselines**.
3. Choose **Run workflow** with workflow ref set to `main`; enter the PR number, exact PR branch name, and exact head SHA, then start the workflow.
4. Wait for both jobs to finish. A successful run adds a generated-baseline commit to that PR branch.
5. Confirm the PR head changed to the new commit and allow the normal Quality and Repository Baselines workflows to run again. Do not merge based on the repair workflow alone.

Never select the PR branch as the workflow ref. If the PR head changes before or during the run, copy the new head SHA and start a fresh run. If GitHub rejects the write because branch protection or token policy blocks it, do not weaken protection; use the documented repository-owner action to resolve the permission boundary.

## Required post-repair checks

The following commands must both pass on the same resulting PR head:

```bash
python tools/dkb.py project-state --check
python tools/dkb.py documentation-baseline --check
```

The normal required Python matrix, Windows package workflow, source/domain review and exact-head merge gates remain in force.
