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
- Last verified head before this checkpoint update: `22140624c665bdcef132be5561ccd0682e25e809`; resolve the current exact head dynamically because this checkpoint update itself advances the branch.
- Exact base: `7e9c5c4c6c6dbcf9a38b75d5985a48c381350a88`; PR metadata reports `mergeable=true`, and comparison reports 46 commits ahead / 0 behind.
- Package changes: 15 source-backed scalar observations across front track, rear track and ground clearance for five exact Eco-G 120 configurations; no inference on the unresolved 1853 mm width/mirror-state conflict. Package state on the PR branch marks this package complete and selects Sandero Stepway remaining brochure reconciliation next; canonical main state is not advanced until merge.
- Latest exact-head CI before the matrix amendment (head `7a991e98e3047fb8c4fbb63381a2a813ace3feba`): Windows package workflow passed all 154 tests; Repository Baselines passed; reporting/export workflows passed; Versioned Data Product Release build-and-verify passed (publish step skipped); Quality failed on Python 3.10/3.13 (23 failures, 5 errors), while Python 3.14 failed only the change-impact matrix because Tooling was still marked FAIL. The matrix was amended on the next commit to record the successful Windows package suite and current base SHA; CI for the amended head had not yet appeared when recorded.
- Confirmed failure families from Quality logs:
  1. Five historical Sandero Stepway source-gap verifiers reject stale `existing_configuration_missing_data_analysis.json`.
  2. Brochure generic-dimension/residual-evidence verifiers and their tests disagree with the now-expanded master data (15 new rows); affected checks include old 23,431/23,490/1,559/396/411-style global expectations and versioned resolution-plan drift. Do not mass-rewrite counts.
  3. Dependent Sandero manual/automatic comparison, completeness and evidence reports have stale summaries after the new rows and scope changes; examples include comparison differences 431 vs 411 and technical coverage 98% vs 96%. Regenerate only with declared canonical generators after inspecting dependencies.
  4. Bigster/Jogger/Duster cargo and brochure-closure verifiers also reject stale shared resolution-plan/review outputs; inspect whether their inputs genuinely changed before regeneration.
  5. The Spring common-technical importer verifier reports stale existing-configuration missing-data analysis JSON. This is a shared downstream artifact, not evidence that the Spring source rows should be re-imported.
  6. Python 3.14 matrix failure was specifically the Tooling row marked FAIL. The matrix now records the successful Windows package workflow command/result and updates Base SHA to the exact PR base; verify the exact template checklist and matrix gate on the amended head.
- The previous log's isolated `extra.txt` / temporary remote-push messages were captured test output; the dedicated Windows package suite passed. Do not infer a production defect from those messages without a failing test assertion.
- The report correctly preserves the unresolved 1853 mm width/mirror-state semantic conflict; do not infer or import it.

**Last completed task:** PR #925 merged; PR #922 matrix Tooling evidence and base SHA refreshed using current-head CI evidence.  
**Next action:** Fetch CI for the latest PR #922 head. Confirm Python 3.14 matrix now passes. Then diagnose and regenerate the stale shared `existing_configuration_missing_data_analysis`, gap-resolution and dependent completeness/comparison/coverage artifacts only through their canonical generators and declared dependency graph. Review immutable historical test contracts separately; update only tests whose intended invariant is legitimately mutable and preserve source-family regression coverage. Re-run all six required checks on the final exact head. Do not merge until all six pass.
**Execution constraints:** GitHub-first only; no local repository synchronization, Git Bash, terminal, Work/Codex; do not change `main` branch protection; do not merge without all six required checks passing on the exact final head.

---

## 8. Required behavior for the literal command “kontynuuj”

Treat the one-word command as:

> Resume from the latest durable checkpoint. Verify current GitHub state and only the changes since that checkpoint. If valid, perform the next action without repeating completed analysis or asking the owner to restate known constraints. Update the checkpoint as work progresses.

It does not mean “skip validation”; it means “do not repeat validation whose exact evidence remains valid.”
