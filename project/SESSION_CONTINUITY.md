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
**Last verified default-branch SHA:** `18579349b065dbaf45bad5c21446569a246c9f37`  
**Last merged work:** PR #925 — durable fast-resume workflow; merged 2026-11-28. All six required checks passed on exact head `01fede57df05aed68b4086c184d8684e49bd6fad`.

**Canonical package state last read from main:** phase `Dacia Official Brochure Assimilation`; current package `official_dacia_brochure_portfolio_readiness_review_20261126_001` (`complete`); next package `sandero_stepway_full_brochure_inventory_and_source_to_master_reconciliation_20261126_001` (`planned`). The active PR branch has a package-scoped state transition; do not treat it as canonical until merged.

**Active data work:** PR #922 — [Import missing Sandero Stepway brochure exterior dimensions](https://github.com/xbodzio7/Dacia-Knowledge-Base/pull/922)  
- Branch: `data/sandero-stepway-page20-exterior-dimensions-20261126`
- Exact head: `58220caf9dfdaffdd8ee969224de359c83c3a165`
- Recorded PR base: `cb8c7f388034d018f654abc42ddc7c7914aa66d5`; current main advanced to the PR #925 merge commit `18579349b065dbaf45bad5c21446569a246c9f37`. A later GitHub metadata refresh reports `mergeable=true`; no merge conflict is currently reported, but re-check mergeability and exact base/head metadata before any merge decision.
- Exact-head CI: `Repository Baselines` passed; all reporting/export workflows passed; `Quality` failed (32 failures, 5 errors in 2,055 tests on Python 3.10/3.13; Python 3.14 failed the change-impact matrix); `Versioned Data Product Release` failed one release regression test. The Windows package workflow job passed.
- Quality root causes evidenced in logs:
  1. Five historical Sandero Stepway source-gap materialized verifiers reject stale missing-data analysis JSON.
  2. Brochure residual/generic-dimension evidence is stale after adding front/rear track; old review keys still classify these attributes as missing.
  3. Dependent completeness/comparison/coverage artifacts and their frozen expectations are inconsistent with the 15 new rows and updated Stepway scopes (e.g. old 23,490 master-row expectation vs 23,505 actual; old 411 comparison-difference expectation vs 431).
  4. Bigster/Jogger/Duster and broader brochure closure tests also report stale resolution plans/review outputs; inspect dependency graph before regenerating, do not blindly rewrite historical baselines.
  5. Package lifecycle negative-path tests report fixture contamination (`extra.txt` in staging/working-tree path manifest) and a temporary bare-remote push failure; isolate fixture/environment cause before changing production package code.
  6. Python 3.14 change-impact matrix fails because its checklist has an extra non-template item, Tooling is marked FAIL, and the evidence cell combines two artifact paths into one path. The current matrix also records an older base SHA.
  7. Release regression failure: generated shortlist HTML no longer contains the legacy marker `niepodane w dokładnym źródle`; determine whether the generator output or test contract is authoritative before changing either.
- The report correctly preserves the unresolved 1853 mm width/mirror-state semantic conflict; do not infer or import it.
- Do not change master data or tests merely to silence totals. Regenerate only declared dependent reports with canonical generators; retain immutable historical fixtures and verify source fidelity.

**Last completed task:** PR #925 merged and fast-resume documentation is now on main.  
**Next action:** First reconcile PR #922's base against current main and inspect its exact changed-file/dependency scope. Then repair the change-impact matrix contract and classify the stale dependent reports, historical tests and release marker failure. Use canonical generators and package-owned evidence; do not weaken invariants or alter historical baselines. Re-run focused tests and all six required checks on the final exact head. Do not merge until the PR is mergeable and all six checks pass.

**Execution constraints:** GitHub-first only; no local repository synchronization, Git Bash, terminal, Work/Codex; do not change `main` branch protection; do not merge without all six required checks passing on the exact final head.

---

## 8. Required behavior for the literal command “kontynuuj”

Treat the one-word command as:

> Resume from the latest durable checkpoint. Verify current GitHub state and only the changes since that checkpoint. If valid, perform the next action without repeating completed analysis or asking the owner to restate known constraints. Update the checkpoint as work progresses.

It does not mean “skip validation”; it means “do not repeat validation whose exact evidence remains valid.”
