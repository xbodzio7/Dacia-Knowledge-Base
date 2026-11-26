# Repository Governance and Workflow Integrity

## Purpose

This document defines the automated controls protecting the Dacia Knowledge Base repository configuration, required CI gates, workflow provenance and package closeout lifecycle. These controls supplement—not replace—the owner-confirmed GitHub protection settings.

## Owner-confirmed repository baseline

The Project Owner confirmed the following main protection settings on 2026-11-26. CI audits repository-level settings and the declared/emitted required-check contract read-only. Branch-protection toggle values remain the owner-confirmed baseline because the standard Actions token cannot read the branch-protection endpoint.

- Pull request required before merge: enabled.
- Required approvals: 0.
- Dismiss stale approvals, Code Owner review and most-recent-push approval: disabled.
- Required status checks: exactly the six names below.
- Require branches to be up to date: disabled; Quality independently checks freshness.
- Conversation resolution, signed commits, linear history and deployments: not required.
- Bypass protection: disabled.
- Force pushes, deletions and branch locking: disabled.

Required contexts (names are exact):

1. Python 3.14
2. Repository state / project-state --check
3. Python 3.10
4. Python 3.13
5. Package workflow / Windows
6. Generated documentation / documentation-baseline --check

The repository-level merge configuration is also audited against the observed baseline: Allow update branch enabled; squash, merge-commit and rebase methods enabled; auto-merge disabled; automatic branch deletion disabled. The audit does not change these settings.

## Four automatic safeguards

### 1. Repository Configuration Audit

The main-only governance audit reads repository-level merge settings and compares the canonical required-check list with the workflow job-name contract. It does not change settings. The GitHub Actions REST response may omit `allow_update_branch`; an absent field is reported as unverifiable, never as false drift. The owner-confirmed connector value remains the recorded baseline.

GitHub's standard Actions token cannot read the branch-protection endpoint, so CI does not claim to verify the live toggle values or bypass setting. The 2026-11-26 owner screenshot remains the source of truth for those settings. The audit fails if repository settings or the canonical/workflow required-check contract drift from that baseline. Never interpret an API 403 as proof that protection is absent or safe.

### 2. PR Freshness Guard

Quality checks out the exact PR head SHA, fetches the current target branch and verifies that its current SHA is an ancestor of the tested head. A stale PR fails before the test matrix. This remains mandatory even though GitHub's require-branches-up-to-date setting is off.

### 3. Unprivileged Pull-request Execution and Main-only Governance Audit

Quality and Repository Baselines use only the ordinary `pull_request` event. These workflows check out the exact PR head with `persist-credentials: false`, grant read-only permissions, and do not expose repository secrets or write tokens to PR code. They never use `pull_request_target` or `workflow_run` to execute, build, or consume artifacts from PR code.

The separate governance audit runs only after a push to `main` or a manual dispatch from `main`. It reads the trusted main-branch workflow files and repository metadata through a read-only API token; it does not check out or execute PR code. It verifies immutable action pins, the ordinary PR trigger, the exact six required-check contract and repository merge settings. A missing REST field such as `allow_update_branch` is reported as unverifiable rather than treated as false drift.

Package-closeout receipts are validated by the ordinary read-only Quality job through the canonical transition validator. The baseline-repair workflow remains a main-dispatched two-job workflow with isolated read-only generation and privileged allowlisted write-back. Never execute PR code with write credentials.

### 4. Package Closure Integrity Guard

When a PR newly marks the current package complete, the trusted Repository Baselines workflow verifies all of the following from GitHub:

- the completion receipt names the current PR and exact package commit;
- the package commit changed the report declared by canonical state and is an ancestor of the exact PR head;
- the report exists at the PR head and has an accepted completed status;
- the report's package identity matches the canonical current package;
- the report registry contains the exact report ID and JSON path;
- a registered Markdown companion, when declared, exists.

A partial closeout, stale receipt, missing registry entry or mismatched report blocks the required Repository state check.

## Safe execution model

- The six existing required status-check names remain unchanged. These safeguards run inside the existing required Repository state job.
- Pull-request validation is read-only. PR code is never given write credentials, and checkout credentials are not persisted.
- Third-party actions in the core workflows are pinned to full commit SHAs.
- The exact tested head SHA must still match the current PR head immediately before merge.
- The six owner-confirmed protection checks remain enabled; do not weaken or bypass them to repair a failed workflow.
- Workflow changes are validated as ordinary read-only PR code. The main-only governance audit validates the merged workflow configuration after it reaches main. Never add a privileged PR event merely to make a workflow definition trusted.

## Failure handling

A failed audit is an actionable configuration or provenance discrepancy, not a reason to skip CI. Identify the exact setting or receipt field, correct the repository configuration only through an explicitly authorized administrative change, and rerun the complete required matrix on the new exact head SHA. Do not infer settings from missing API fields and do not mark an inaccessible check as passed.
