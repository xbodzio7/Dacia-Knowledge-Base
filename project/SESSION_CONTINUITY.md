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
**Last verified default-branch SHA:** `cb8c7f388034d018f654abc42ddc7c7914aa66d5` (PR #922 base SHA; re-verify before relying on it)  
**Last merged work:** PR #924 — Jogger MY26 2026-10-01 special non-metallic paint surcharge correction; merge commit `cb8c7f388034d018f654abc42ddc7c7914aa66d5`.

**Canonical package state last read from main:** phase `Dacia Official Brochure Assimilation`; current package `official_dacia_brochure_portfolio_readiness_review_20261126_001` (`complete`); next package `sandero_stepway_full_brochure_inventory_and_source_to_master_reconciliation_20261126_001` (`planned`). Re-read `state.json` on current main before selecting work because PRs may have advanced the queue.

**Continuity implementation:** PR #925 — [durable fast-resume workflow](https://github.com/xbodzio7/Dacia-Knowledge-Base/pull/925)  
- Branch: `docs/session-continuity-fast-resume-20261128`  
- Previous recorded head before the final checkpoint amendment: `57bd538987bde902f07d3ba062e0654e5a6edd11`. That amendment advanced the PR again; resolve the current exact head dynamically from GitHub rather than treating this historical SHA as current.  
- Last observed state: open; no exact-head workflow runs or classic status checks were returned for the subsequently observed head. Re-fetch current checks before relying on this snapshot.

**Active data work:** PR #922 — [Import missing Sandero Stepway brochure exterior dimensions](https://github.com/xbodzio7/Dacia-Knowledge-Base/pull/922)  
- Branch: `data/sandero-stepway-page20-exterior-dimensions-20261126`
- Last observed head: `58220caf9dfdaffdd8ee969224de359c83c3a165`
- Last observed base: `cb8c7f388034d018f654abc42ddc7c7914aa66d5`
- Last observed state: open, mergeable, not merged.
- Last observed required-check outcomes: `Repository Baselines` passed; `Quality` failed; `Versioned Data Product Release` failed. Other package/reporting workflows shown for that SHA succeeded. Re-fetch the exact PR and inspect the two failing workflow logs before deciding the repair.
- Scope: 15 exact page-20 exterior-dimension observations for five Eco-G 120 configurations; preserve the unresolved 1853 mm width/mirror-state conflict; do not infer.

**Last completed task before PR #922:** Jogger paint surcharge correction merged in PR #924.  
**Next action:** Diagnose the failed `Quality` and `Versioned Data Product Release` jobs on PR #922 head `58220caf9dfdaffdd8ee969224de359c83c3a165`, classify root causes, then repair only in-scope failures and validate the resulting exact head. Do not merge until all six required checks pass on the final exact head and normal merge requirements are met.

**Canonical package note:** Read `project/state.json` on current `main` before selecting any new package. This checkpoint does not override its current/next package fields.

**Execution constraints:** GitHub-first only; no local repository synchronization, Git Bash, terminal, Work/Codex; do not change `main` branch protection; do not merge without all six required checks passing on the exact final head.

---

## 8. Required behavior for the literal command “kontynuuj”

Treat the one-word command as:

> Resume from the latest durable checkpoint. Verify current GitHub state and only the changes since that checkpoint. If valid, perform the next action without repeating completed analysis or asking the owner to restate known constraints. Update the checkpoint as work progresses.

It does not mean “skip validation”; it means “do not repeat validation whose exact evidence remains valid.”
