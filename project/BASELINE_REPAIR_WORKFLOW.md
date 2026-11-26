# Canonical Baseline Repair Workflow

## Purpose

Use the GitHub Actions workflow **Baseline Repair** to regenerate repository-owned counters and managed documentation on an exact open pull-request head when local repository execution is unavailable.

The workflow is a controlled repair operation, not a validation bypass. It derives the PR branch and immutable head SHA from GitHub using only the PR number supplied by the maintainer. It applies the canonical generators, checks both generated baselines, and writes back only the six allowlisted generated files.

## Scope

The workflow may produce and write back only these six files:

- `project/state.json`
- `project/STATE_SUMMARY.md`
- `README.md`
- `CHANGELOG.md`
- `project/ROADMAP.md`
- `project/SESSION_STATE.md`

It must never write master data, source files, package manifests, tests, code, workflow definitions or arbitrary paths.

## Security model

The workflow must be dispatched from the protected `main` branch (never from the PR branch). The workflow definition must already be present on `main`; it cannot safely repair the PR that first introduces or changes this workflow.

1. The maintainer supplies only the PR number. The read-only job retrieves the PR through the GitHub API and independently derives its branch, head SHA and base SHA.
2. The job fails closed unless the PR is open, targets `main`, belongs to this repository (fork PRs are rejected), has a valid branch/head, and its base SHA exactly matches current `main`.
3. The trusted workflow checks out the immutable PR head with persisted credentials disabled. The generator job has read-only permissions and runs the canonical project-state and documentation-baseline generators and checks. No write token is exposed to code from the PR.
4. The workflow rejects any changed path outside the exact six-file allowlist and uploads those files as a short-lived artifact.
5. A separate write-back job re-queries the PR and `main`, and refuses to proceed if the PR identity, branch, head SHA or base SHA changed. It checks out the already verified immutable head, downloads the artifact, rejects symlinks and any manifest other than the exact six files, then commits and pushes without force.
6. After pushing, the workflow verifies that the PR head is exactly the new repair commit and that `main` has not advanced. It explicitly dispatches Quality and Repository Baselines for the updated branch because pushes made with the default `GITHUB_TOKEN` do not automatically trigger ordinary PR workflow events.

The privileged write-back job does not execute scripts, tests, build tools or other code from the PR. It only installs the validated six-file artifact and performs Git operations. Do not replace this two-job separation with `pull_request_target`, do not run PR code with write credentials, and do not broaden the allowlist without a separate security review.

The separate Quality and Repository Baselines validation workflows use only ordinary pull_request events with read-only permissions and checkout credentials persistence disabled. They must never use pull_request_target or workflow_run to execute, build, test, or consume artifacts from PR code. The baseline-repair workflow remains a separate workflow_dispatch operation from main with its own two-job security boundary.

## How to run

1. Open the repository's **Actions** tab and select **Baseline Repair**.
2. Choose **Run workflow** with workflow ref set to `main`.
3. Enter only the open PR number and start the workflow.
4. Wait for both jobs to finish. The run summary/log records the branch, exact head SHA and base SHA discovered from GitHub.
5. Confirm that the write-back job reports the new repair commit and that Quality and Repository Baselines have been dispatched.
6. Review the resulting PR diff. The repair must contain only the six allowlisted generated files in addition to the PR's original changes.
7. Wait for all six normal required checks to pass on the new exact PR head SHA. The repair workflow itself is not a substitute for those checks.

Never select the PR branch as the workflow ref. Never merge based on the repair workflow alone. If the branch advances, the base changes, the push is rejected, or a required check is missing, stop and diagnose; do not weaken branch protection.

## Required post-repair checks

The following commands must both pass on the same resulting PR head:

```bash
python tools/dkb.py project-state --check
python tools/dkb.py documentation-baseline --check
```

The normal required Python matrix, Windows package workflow, source/domain review and exact-head merge gates remain in force.

## No-op repairs and dispatch guarantees

A successful baseline generation may produce no content changes on the PR branch. This is a valid result, not a workflow failure. The workflow must still upload the exact six-file artifact, complete the isolated write-back job, and explicitly dispatch both **Quality** and **Repository Baselines** for the verified PR branch and exact unchanged head SHA. The dispatch step must depend on successful artifact application, not on `changed == true`.

When generated files do differ, the workflow pushes the allowlisted repair commit without force and then performs the same final verification and dispatch path. The final verification retries bounded GitHub API reads to tolerate short-lived stale PR-head responses after a successful push; it must never accept a different head SHA, branch, PR identity or base SHA. If the expected head does not become visible within the retry window, the workflow fails closed and does not dispatch checks against an unverified revision.

The baseline-repair contract assertions in `tests/test_package_workflow.py` protect both paths: no-op generation must remain successful, both paths must publish an exact target head SHA, and required-check dispatch must run after every successful apply. Keep this test in the Windows package-workflow test list as well as the normal Python quality suite.
