# Session Continuity and Fast Resume

**Project:** Dacia Knowledge Base (DKB)  
**Status:** Mandatory  
**Authority:** `project/state.json` remains the canonical project/package selector.

## 1. Purpose

A new chat started with **“kontynuuj”** is a continuation request, not a request to repeat the complete project audit. Resume from the last durable checkpoint and verify only facts that may have changed.

Conversation memory and summaries may help locate the checkpoint, but they never override GitHub or repository evidence.

## 2. Fast-resume procedure

At the beginning of every continuation:

1. Identify the repository and its default branch from the connected GitHub repository.
2. Read the current `project/state.json` from the default branch. Record its package IDs and execution/autonomy policies.
3. Read this file's **Latest durable checkpoint** below.
4. Verify the current default-branch SHA, the checkpoint's active PR/branch (if any), and the exact PR head/base SHAs. Read current PR state and check conclusions for that exact head.
5. Compare the current remote state with the checkpoint. Inspect only commits, changed files, merges, PR updates and check runs newer than the checkpoint or directly relevant to its active task.
6. If the checkpoint is valid and no material drift or blocker is found, continue directly with its **Next action**. Do not repeat completed analysis, source extraction, tests or audits.
7. Update the checkpoint after each meaningful completed step, PR/CI transition, merge, blocker, or session boundary.

The checkpoint is an operational resume pointer, not a second source of truth. If it disagrees with `state.json`, GitHub, a merged PR or source evidence, the authoritative evidence wins and the checkpoint is repaired before work continues.

## 3. What counts as a valid checkpoint

A checkpoint is usable when it identifies:

- last verified default-branch SHA and verification time;
- canonical current/next package IDs from `state.json`;
- last completed logical step and its durable GitHub location;
- active branch and PR number, exact head SHA and base SHA, if applicable;
- required CI checks and their conclusions on that exact head;
- the single next actionable task;
- unresolved blockers, decisions or owner actions;
- relevant source/report/manifest paths needed for that next task.

Do not mark work complete because it was discussed, generated in an ephemeral session, or merely committed to an unmerged branch. State whether it is drafted, committed, in a PR, merged, validated or blocked.

## 4. Triggers for a deeper recovery or full audit

Do not perform a full startup audit by default. Escalate only when one or more of these conditions applies:

- the checkpoint is missing, malformed, too old to establish a safe resume point, or cannot be reconciled;
- the canonical package selector, generated state summary, report registry, manifest or source registry conflicts with GitHub evidence;
- the default branch or active PR head moved in a way that changes the task's scope or dependencies;
- a PR was merged, closed, retargeted, rebased, conflicted, or its required checks changed;
- a relevant required CI check failed, is missing, or belongs to a different SHA;
- source identity, source bytes, provenance, configuration scope or prior-import status is uncertain;
- a new task touches architecture, schema, CI, repository governance, branch protection, credentials or another high-risk boundary;
- the execution environment or permissions materially changed;
- evidence suggests duplicate work, regression, data loss or an unrecorded external action.

Escalation is scope-limited: inspect the governing documents and artifacts for the affected area, not every project document automatically.

## 5. Validation without repeating work

- Reuse a passing check only when it belongs to the exact unchanged commit SHA and the check's inputs have not changed.
- Any commit/head change invalidates exact-head CI evidence for that new head.
- Do not rerun tests merely because a new chat started.
- When local execution is unavailable or disallowed, do not request local terminal/Git Bash steps. Use the repository's approved GitHub Actions/remote validation path when available.
- If remote validation cannot be started or inspected, record the exact missing capability and stop only the affected validation-dependent action. Never claim a test passed without evidence.
- Keep all six required `main` protection checks and existing merge gates unchanged. Never bypass checks or alter branch protection as a shortcut.

## 6. Checkpoint maintenance

Update **Latest durable checkpoint** below:

- after a logical task is completed;
- after creating/updating a branch or PR;
- when CI changes from pending to a conclusion, or a failure is diagnosed;
- immediately after a merge or other repository-state transition;
- before stopping at an `ACTION_REQUIRED` boundary or ending a work session.

Write concise facts and exact identifiers. Keep historical detail in commits, PRs and reports; the checkpoint should contain only enough information to resume safely. Never copy a guessed SHA or stale package pointer into it.

## 7. Latest durable checkpoint

**Snapshot date:** 2026-11-28  
**Repository:** `xbodzio7/Dacia-Knowledge-Base`  
**Verified default-branch SHA:** `7e9c5c4c6c6dbcf9a38b75d5985a48c381350a88`  
**Last merged continuity work:** PR #925 — durable fast-resume workflow; merged 2026-11-28. PR #926 is also included in the current main history.

**Canonical package state from main (`project/state.json`):**
- Phase: `Dacia Official Brochure Assimilation`
- Current package: `official_dacia_brochure_portfolio_readiness_review_20261126_001` (`complete`)
- Next package: `sandero_stepway_full_brochure_inventory_and_source_to_master_reconciliation_20261126_001` (`planned`)
- The next package is the complete 21-page Sandero Stepway brochure inventory and source-to-master reconciliation. Reuse existing page 17-19 evidence; do not repeat resolved imports or promote unresolved candidates.

**Active data PR #922:** [Import missing Sandero Stepway brochure exterior dimensions](https://github.com/xbodzio7/Dacia-Knowledge-Base/pull/922)
- Branch: `data/sandero-stepway-page20-exterior-dimensions-20261126`
- Exact head: `7362e8352dc16b9fc5885d5da4f15abea42543d2`
- Base: `7e9c5c4c6c6dbcf9a38b75d5985a48c381350a88`; `mergeable=true` at last check.
- Exact-head Quality run `46173123225`: **FAIL**. Repository Baselines run `46173123127`: **FAIL**.
- Known blockers include stale missing-data analysis and dependent Stepway source-gap/evidence/resolution artifacts; stale cargo-resolution plans; documentation/test-count drift (state baseline 2055 vs discovered 2056 at the diagnostic run); and the change-impact matrix evidence/Tooling row. The PR contains a reports-only mode and a regression test for the missing-data analysis generator, but the canonical report still needs fingerprinted metadata and freshness registration, now being addressed by PR #929.
- Preserve the unresolved 1853 mm width/mirror-state conflict; do not infer or import it. Do not merge until the branch is reconciled with current main and all six required checks pass on its final exact head.

**Generated-artifact safeguard work:**
- PR #927 — policy/documentation only; head `7bfc842a4f13af651cb1e81267b8abc3b0341401`; all six required checks passed. It is now superseded by consolidated PR #929.
- PR #928 — safe dynamic `depends_on_globs` support in report-impact/freshness with regression cases; head `fcd9f552d2e44e9d15f7f52b19c50c579e4134ba`; all six required checks passed. It is now included in consolidated PR #929.
- PR #929 — [Register missing-data analysis with provenance and safe regeneration](https://github.com/xbodzio7/Dacia-Knowledge-Base/pull/929); branch `feat/register-missing-data-analysis-report-20261128`; exact head `94ea9498de409897e9a0b67ed14accfac6e5e407`; base main `7e9c5c4c6c6dbcf9a38b75d5985a48c381350a88`. Quality and Repository Baselines are running. Do not merge until all six required checks pass on this exact final head.
- PR #929 consolidates the report-glob implementation, policy documentation, and registration of `existing_configuration_missing_data_analysis`. The current report has 43 fingerprinted inputs: five master CSVs, its generator, 28 completeness JSON files and nine source-gap review JSON files. The registry declares two constrained dynamic globs. `--check` is read-only; `--reports-only` writes only the JSON/Markdown report pair and preserves project state/package metadata. The existing counted regression test covers allowlisting, idempotency and byte-for-byte preservation.
- `configuration_gap_evidence.json` and `configuration_gap_resolution_plan.json` are reviewed input specifications, not generated repository reports; do not register them as reports.

**Next actions:**
1. Finish PR #929 Quality and Repository Baselines validation on exact head `94ea9498de409897e9a0b67ed14accfac6e5e407`. Confirm Python 3.10/3.13/3.14, Windows package workflow, Repository state and Generated documentation all pass.
2. If PR #929 is green, leave it ready for the owner's merge decision; close PRs #927 and #928 as superseded only after confirming the consolidated PR includes their full changes.
3. After PR #929 is merged, reconcile PR #922 with the new main SHA. Regenerate the missing-data analysis with `--reports-only`, refresh only verified dependent reports/resolution plans, repair the change-impact matrix and run the full exact-head checks. Do not hand-edit generated reports or alter historical evidence.
4. After PR #922 is resolved, resume the canonical next package from `state.json`: the full 21-page Sandero Stepway brochure inventory and source-to-master reconciliation.

**Execution constraints:** GitHub-first only; no local repository synchronization, Git Bash, terminal, Work/Codex or TinyFish. Do not change main branch protection or required check names. Never claim a test passed without exact CI evidence. No merge before all six required checks pass on the final exact head.

## 8. Required behavior for the literal command “kontynuuj”

Treat the one-word command as:

> Resume from the latest durable checkpoint. Verify current GitHub state and only the changes since that checkpoint. If valid, perform the next action without repeating completed analysis or asking the owner to restate known constraints. Update the checkpoint as work progresses.

It does not mean “skip validation”; it means “do not repeat validation whose exact evidence remains valid.”
