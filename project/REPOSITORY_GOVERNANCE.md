# Repository Governance and Workflow Integrity

## Purpose

This document defines the automated controls protecting the Dacia Knowledge Base repository configuration, required CI gates, workflow provenance and package closeout lifecycle. These controls supplement—not replace—the owner-confirmed GitHub protection settings.

## Owner-confirmed repository baseline

The Project Owner confirmed the following main protection settings on 2026-11-26. CI audits them read-only and fails closed on drift.

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

The existing required Repository state job reads repository settings and the main branch protection API. It checks the merge methods, update-branch setting, exact six required status contexts, PR/review settings, bypass enforcement and the remaining owner-confirmed toggles. It does not change settings.

A missing API permission, 403, missing protection object or unexpected response fails the audit. It must never be interpreted as a successful or absent protection rule. The connector's inability to read branch protection does not invalidate the owner-confirmed baseline; GitHub Actions uses its own read-only administration permission for this audit.

### 2. PR Freshness Guard

Quality checks out the exact PR head SHA, fetches the current target branch and verifies that its current SHA is an ancestor of the tested head. A stale PR fails before the test matrix. This remains mandatory even though GitHub's require-branches-up-to-date setting is off.

### 3. Workflow Provenance Guard

Quality and Repository Baselines use pull_request_target for steady-state PR validation. GitHub therefore loads the workflow definition from the trusted base branch, not from the proposed PR revision. The workflows then check out the exact PR head with persist-credentials: false and read-only permissions.

The trusted audit verifies that the workflow SHA is an ancestor of the PR base, that core workflow actions are pinned to immutable 40-character commit SHAs, and that the proposed workflow files preserve the trusted event, exact-head checkout, freshness and read-only boundaries.

The baseline-repair workflow is deliberately excluded from this model: it remains a main-dispatched two-job workflow with isolated read-only generation and privileged allowlisted write-back. Never execute PR code with write credentials.

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
- Workflow changes are bootstrapped through the currently trusted checks. Once the target-based workflow is present on main, the follow-up migration removes the legacy pull_request trigger so steady-state validation uses only pull_request_target.

## Failure handling

A failed audit is an actionable configuration or provenance discrepancy, not a reason to skip CI. Identify the exact setting or receipt field, correct the repository configuration only through an explicitly authorized administrative change, and rerun the complete required matrix on the new exact head SHA. Do not infer settings from missing API fields and do not mark an inaccessible check as passed.
