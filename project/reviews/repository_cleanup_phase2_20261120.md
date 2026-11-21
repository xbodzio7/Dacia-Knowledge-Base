# Repository cleanup — phase 2

**Date:** 2026-11-20  
**Base:** `main` at `66626ee8afa81b46a3c7bc5b97662cc6aa9e88bf`  
**Scope:** Remove the one-off Bigster snapshot workflow.

## Removed

- `.github/workflows/temporary-bigster-snapshot.yml`

The workflow only ran for pull requests whose head branch was exactly `agent/bigster-catalogue-foundation`, and uploaded a whole-repository snapshot with a one-day retention period. Its original work is complete: PR #192 and PR #193, which established the Bigster catalogue foundation, are both merged. No currently open PR uses this branch or this workflow.

## Deferred, not deleted

- `.github/workflows/ai-rematerialize-sandero-modal-reconciliation.yml` remains in place for now. Its dedicated branch `ai/sandero-stepway-full-modal-reconciliation-001` still exists, and the workflow can remove and rematerialize source-scoped master records before committing and pushing. Although its original PR #629 is merged, deleting this automation without first resolving the surviving branch's lifecycle would leave an incomplete retirement. No remote branch is deleted by this cleanup.

## Safety and validation

- No data, source files, import tools, tests or current reporting artifacts are changed.
- No local tests are claimed. The PR's required GitHub Actions checks must validate the exact head.
