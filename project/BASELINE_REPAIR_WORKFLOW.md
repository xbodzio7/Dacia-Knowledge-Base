# Canonical Baseline Repair Workflow

## Purpose

Use the GitHub Actions workflow **Baseline Repair** to regenerate repository-owned counters and managed documentation on an exact open pull-request head when local repository execution is unavailable.

This is a repair operation, not a bypass of validation. The workflow runs the canonical generators, rechecks both generated baselines on the same candidate tree, and uploads the generated files as a short-lived artifact for review.

## Scope

The workflow may produce only these six generated files:

- `project/state.json`
- `project/STATE_SUMMARY.md`
- `README.md`
- `CHANGELOG.md`
- `project/ROADMAP.md`
- `project/SESSION_STATE.md`

It must never edit master data, source files, package manifests, tests, code, workflow definitions or arbitrary paths.

## Security model

The workflow must be dispatched from the protected `main` branch (never from the PR branch) and requires the PR number, exact head branch, and exact current 40-character head SHA. The workflow file must already be present on `main` before it is used. It cannot safely repair the PR that first introduces this workflow.

1. A maintainer selects `main` as the workflow ref. The read-only job verifies that the PR is open, targets `main`, belongs to this repository (fork PRs are rejected), and still has the supplied branch and head SHA.
2. The trusted workflow definition from `main` checks out that immutable PR SHA with persisted checkout credentials disabled.
3. It runs only the canonical project-state and documentation-baseline generators and their check commands.
4. It rejects any changed path outside the six-file allowlist and uploads the generated text files as a one-day artifact.
5. The workflow has no write permission and never commits to a branch. The artifact is data only. A maintainer must review its contents and apply the generated files to the exact PR branch through an authenticated repository write integration or the normal GitHub UI.
6. After the reviewed commit, the normal PR workflows must run on the new exact head SHA. Do not use a workflow job that pushes with the default `GITHUB_TOKEN` as a substitute: such pushes do not automatically trigger the normal PR workflow events.

Do not add broader paths, secrets or write permissions without a separate security review.

## How to run

1. Open the PR and copy its current **head commit SHA** (not the merge commit SHA).
2. Open the repository's **Actions** tab and select **Baseline Repair**.
3. Choose **Run workflow** with workflow ref set to `main`; enter the PR number, exact PR branch name, and exact head SHA, then start the workflow.
4. Wait for the read-only job to finish successfully and download the `canonical-baseline-repair` artifact.
5. Review that the artifact contains only the six allowlisted files and that its source run used the exact PR head SHA.
6. Apply those files to the same PR branch as a new commit. If the PR head has changed since the artifact was generated, discard the artifact and run a fresh repair against the new SHA.
7. Confirm that the new commit is the PR head and wait for all normal required checks to pass on that exact SHA.

Never select the PR branch as the workflow ref. Never merge based on the repair workflow or artifact alone. If the write integration or branch policy rejects the commit, do not weaken branch protection.

## Required post-repair checks

The following commands must both pass on the same resulting PR head:

```bash
python tools/dkb.py project-state --check
python tools/dkb.py documentation-baseline --check
```

The normal required Python matrix, Windows package workflow, source/domain review and exact-head merge gates remain in force.
