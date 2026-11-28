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
- Latest verified head before this checkpoint commit: `2f897aaeb23866fe4b58e9459365199ca79bd370`; resolve the exact head dynamically after this update.
- Exact base: `7e9c5c4c6c6dbcf9a38b75d5985a48c381350a88`; PR remains open and GitHub reports `mergeable=true`.
- Data package: 15 source-backed scalar observations across front track, rear track and ground clearance for five exact Eco-G 120 configurations; unresolved 1853 mm width/mirror-state conflict remains excluded. Package state on PR branch marks this package complete and selects Sandero Stepway remaining brochure reconciliation next; canonical main state is not advanced until merge.

**Latest exact-head CI before the two safety commits:** head `421c31a1b4bd442ea8ee87c90fe66cb0aaed6429`, Quality run `46171461424`. Windows package workflow, Repository Baselines and cross-platform checks passed; reporting/export/release verification workflows passed (release publishing skipped). Python 3.10, 3.13 and 3.14 Quality jobs all failed with the same 23 failures and 5 errors (2055 tests; 16 skipped). The Tooling change-impact row is no longer the Python 3.14 cause.

**Confirmed Quality failure groups and representative assertions:**
1. Five historical Sandero Stepway source-gap materialization tests error because their shared `existing_configuration_missing_data_analysis.json` is stale. The deterministic-output test independently confirms tracked JSON differs from fresh `collect()` (missing technical count 97 vs tracked 81). Spring importer and Jogger completeness aligner also reject this same stale shared JSON/Markdown.
2. Bigster, Duster, Jogger and Sandero Stepway cargo checks fail because the versioned configuration-gap resolution plan differs from current evidence/model. Semantic mapping and residual-evidence checks reject the approved generic-dimension package. Inspect evidence spec, plan spec and model derivation before regeneration; do not replace the plan blindly.
3. Brochure/global count assertions are stale relative to current materialized rows: Bigster expects 23,431 but sees 23,505; approved generic dimensions expects 396 but sees 411; brochure scalar closure expects 1,559 but sees 1,574. These mutable global counts are not automatically proof of bad rows.
4. Reviewed-gap materialization expects 12 technical review states but sees 2. Determine whether report generation lost states or the expected scope is obsolete.
5. Sandero Eco-G 120 manual reporting tests contain stale comparison, completeness, evidence and source-coverage expectations (e.g. technical coverage 96%/288 present vs current 98%/294; evidence total 57 vs 51). Sandero Stepway automatic comparison expects 63 technical comparisons but current output has 65.
6. Duster reporting test expects 411 comparison differences but current report yields 431. Preserve independent denominators; do not merely edit expected numbers.
7. Jogger aligner explicitly lists only the shared missing-data JSON and Markdown as outdated. Spring common-technical importer fails on the same JSON.
8. Earlier Tooling matrix failure was corrected. Temporary `extra.txt` / simulated git-push messages are test-fixture output; the dedicated Windows package suite passed.

**Safety implementation added on PR #922 (CI not yet verified):**
- Commit `bd01d331eafa925d2211452bb775b371236bb63e`: `tools/existing_configuration_missing_data_analysis.py` now supports mutually exclusive `--check` and `--reports-only`. The latter calls `apply(..., update_project_state=False)`, writing only the JSON/Markdown report and returning before touching `project/state.json` or the package markdown. Default apply behavior is preserved.
- Commit `2f897aaeb23866fe4b58e9459365199ca79bd370`: added a temporary-repository regression test proving reports-only regeneration leaves both canonical state and package metadata byte-for-byte unchanged while updating the report outputs.
- These commits trigger a new full PR CI run. The latest checks observed immediately after commit `2f897aa...` were queued; no success is claimed yet. This reports-only interface has not been executed against the live repository outputs.

**Remaining generator/dependency caution:** `tools/configuration_gap_evidence.py` and `tools/configuration_gap_resolution_plan.py` need their output/input dependencies inspected before any generation. Resolution-plan `--write-plan-spec` writes a spec and must not be used as a blind repair. The new reports-only option addresses only the missing-data report generator; it does not make downstream evidence, plan, comparison or closure generators safe by default.

**Last completed task:** assertion-level CI diagnosis plus a state-safe reports-only regeneration mode and regression test. No source/master data or canonical state changed.  
**Next action:** fetch current PR #922 head and wait for its exact-head CI. Confirm the new reports-only regression test and all Quality jobs. If it passes, use the new mode only on an isolated branch/worktree or in an approved remote execution step to regenerate the shared missing-data JSON/Markdown, then inspect the resulting diff before committing. Next inspect evidence/plan dependency graphs and regenerate only proven-stale dependent outputs. Review mutable test expectations separately and preserve source-family regression coverage. Re-run all six required checks on the final exact head. Do not merge until all six pass.
**Execution constraints:** GitHub-first only; no local repository synchronization, Git Bash, terminal, Work/Codex; do not change `main` branch protection; do not merge without all six required checks passing on the exact final head.

---

## 8. Required behavior for the literal command “kontynuuj”

Treat the one-word command as:

> Resume from the latest durable checkpoint. Verify current GitHub state and only the changes since that checkpoint. If valid, perform the next action without repeating completed analysis or asking the owner to restate known constraints. Update the checkpoint as work progresses.

It does not mean “skip validation”; it means “do not repeat validation whose exact evidence remains valid.”
