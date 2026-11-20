# Repository cleanup — phase 1

**Date:** 2026-11-20  
**Base:** `main` at `66626ee8afa81b46a3c7bc5b97662cc6aa9e88bf`  
**Scope:** Retire closed-PR automation and unsafe/ephemeral root artifacts.

## Removed

| Path | Reason |
|---|---|
| `.github/ai-trigger-pr465-repair.txt` | One-off trigger artifact for PR #465, merged 2026-08-02. |
| `.github/workflows/ai-repair-pr465-contracts.yml` | Workflow guarded exclusively by `github.event.pull_request.number == 465`; the target PR is closed/merged. |
| `.github/workflows/ai-repair-pr465-final.yml` | Reopen-only validation workflow guarded exclusively by PR #465; the target PR is closed/merged. |
| `upload.bat` | Executes `git add .`, commits every working-tree change and pushes. This bypasses the project's controlled, reviewable package workflow and can include unrelated files. |
| `jogger-quality-diagnostic.txt` | A one-off historical compile/test output log from 2026-08-01, not a maintained report or executable project input. |

## Safety checks

- Confirmed the current default branch is `main` at the base SHA above.
- Reviewed the current open pull-request inventory; none targets PR #465 or lists these retired artifacts as changed files.
- The two PR465 workflows are explicitly restricted to PR #465. No active workflow purpose is being generalized or transferred.
- No source PDFs, owner-supplied documents, master data, import specifications, tests, package history or project decisions are removed.
- No project-state counters or generated data baselines are changed by this package.

## Validation boundary

This change was authored through GitHub's repository API. No local checkout or Python test runtime is available in this session, so no local tests are claimed. The pull request's required GitHub Actions checks must validate the exact PR head before any merge decision.

## Follow-up

Continue with a separate package for other temporary workflows and verified duplicate artifacts. Keep legacy validators and dated import/review tools until their references and reproducibility role are fully checked. Preserve source files and intentional historical records.
