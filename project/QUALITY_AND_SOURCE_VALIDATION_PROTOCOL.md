# Mandatory Quality and Source-Validation Protocol

**Project:** Dacia Knowledge Base (DKB)  
**Status:** Active and mandatory  
**Effective from:** 2026-11-06  
**Applies to:** Every AI session, chat, handoff, execution profile, package, model family and repository change.

## 1. Authority and persistence

This protocol is part of the mandatory startup contract. Every AI maintainer must read and apply it in every new chat/session before any DKB work. It is not activated by a user reminder, conversation memory or a special prompt.

project/START_HERE.md must list this file in its required reading order. The startup procedure must be followed even when the user says only "kontynuuj", "continue", or otherwise gives a short continuation instruction.

If a future change moves or renames this file, update START_HERE.md in the same commit. Do not leave a broken reference or silently make this protocol optional.

The protocol governs work quality and does not override the canonical state, approved architecture decisions, source evidence, autonomy boundaries or current package scope.

## 2. Mandatory package lifecycle

No master-data or code implementation begins until the following stages are completed or explicitly recorded as blocked/deferred:

1. **Bootstrap:** read project/state.json, generated state summary, this protocol, the startup-required governance documents and the current package manifest.
2. **Freshness and scope:** verify current remote main, open PRs, recent merges, exact package branch/head, changed paths, source IDs, configuration IDs and whether equivalent work already exists.
3. **Evidence inventory:** identify exact source identity, market, model year, effective/issue dates, version, pages/tables and source coverage status. Distinguish preliminary/partial review from full assimilation.
4. **Source-to-master reconciliation:** build a candidate inventory and compare each fact against existing master data and prior source observations before editing.
5. **Change plan:** define exact files, records, expected additions/updates, non-changes, exclusions, unresolved items and acceptance criteria.
6. **Implementation:** change only the approved package scope; preserve provenance, history and applicability boundaries.
7. **Focused validation:** run the smallest relevant tests and deterministic checks during development.
8. **Independent evidence validation:** compare the resulting records back to the source, independently of the importer and its tests.
9. **Final quality gate:** after all edits and generated outputs are stable, run the complete required quality matrix on the exact final commit/head SHA.
10. **Publication and continuity:** verify commit, PR, CI, merge state and changed paths; update canonical state and generated documentation as required; persist the next safe package.

A stage may be skipped only when it is genuinely inapplicable and the reason is recorded. A conversation statement that a stage was completed is not evidence; verify its durable repository result.

## 3. Evidence-first data rules

For every candidate fact, record or retain enough information to identify:

- exact source ID and source revision/date;
- page and table/section (or exact machine-readable source location);
- exact model, model year, market, grade, engine/fuel, transmission, body/seating and other applicability dimensions present in the source;
- printed value, unit, currency and source notation;
- interpretation and any normalization applied;
- whether the fact is new, already correct, changed, contradicted, superseded, unavailable explicitly, or unresolved.

Never transfer a value between configurations, grades, fuels, transmissions, seat counts, model years, markets or source revisions without explicit source evidence.

Never interpret omission as unavailability. A printed dash or explicit exclusion may establish unavailability only for the exact scope covered by that statement. Do not replace unresolved evidence with zero, an empty typed value, not_available, or a guess. Use the workflow status Do sprawdzenia only in an approved deferred-gap/reporting structure, never as a typed master-data value.

For PDFs, parsed text is not sufficient where layout, columns, symbols, footnotes, colours or visual grouping determine meaning. Inspect rendered pages and record page-level evidence. Check headings, legends, notes and footnotes that qualify table cells.

## 4. Mandatory pre-import reconciliation report

Before editing master data, prepare a deterministic or reviewable comparison with one disposition per candidate fact:

- already_correct — represented accurately; do not duplicate;
- missing_importable — supported by explicit evidence and model;
- requires_update — existing fact is superseded or incorrect for a specific validity scope; preserve history;
- explicitly_unavailable — source explicitly says unavailable for the exact applicability;
- source_conflict — authoritative evidence conflicts; do not choose silently;
- model_limitation — data model cannot preserve meaning; defer and identify the needed model decision;
- out_of_scope — not part of the accepted package;
- Do sprawdzenia — evidence is insufficient; state the next verification action.

The report must make duplicate prevention visible. A source observation already represented correctly is a verified no-op, not a reason to create another master row.

If no report generator exists, a concise versioned Markdown/CSV/JSON reconciliation artifact is acceptable. Do not build a new framework solely for a small package when a simple auditable artifact is sufficient.

## 5. Test design: verify invariants, not incidental totals

Tests must primarily verify durable contracts and business rules:

- schema and required-field validity;
- unique identifiers and referential integrity;
- correct source/configuration/applicability links;
- correct validity dates and historical versioning;
- allowed status transitions and explicit unavailability semantics;
- exact source-backed values for representative or critical records;
- no duplicate facts and no unintended overwrites;
- deterministic outputs and importer idempotency where applicable.

Avoid hard-coding mutable global catalogue totals, current offer counts, minimum prices or unrelated cross-model totals in tests whose purpose is to validate a local importer or invariant.

A count assertion is appropriate only when the count is itself a stable, intentional contract for the exact scoped fixture/source inventory. Scope it explicitly by source ID, date, configuration set or fixture. Explain why the count is invariant.

Do not weaken a test merely because it fails after new data arrives. First establish whether the failure is caused by:
1. incorrect source interpretation;
2. incorrect master data;
3. importer or transformation defect;
4. invalid/obsolete test expectation;
5. a real data-model or validator limitation;
6. unrelated repository drift.

Change the test only after the intended invariant and authoritative evidence are established. When an expectation legitimately changes, document the source-backed reason in the test or adjacent fixture/report.

## 6. Two independent quality gates

A green CI run is necessary but does not by itself prove domain-data correctness. Every data package must pass both gates.

### Gate A — Technical integrity

Run the applicable focused tests during development, then the full required quality workflow on the final head. Verify all required operating systems and supported Python versions, repository/state contracts, generated artifacts and cross-platform checks. A skipped job is not a pass unless the workflow explicitly defines it as not applicable and the required alternative check passed.

### Gate B — Source fidelity

Independently compare the final imported/updated master records and their provenance against the original official source. This review must not rely solely on the importer output, a test fixture generated by the importer, or the same transformation logic used to create the data.

At minimum, verify:
- every expected source row/cell has a disposition;
- each imported value and applicability mapping matches the printed source;
- unavailable/optional/standard states are not confused;
- no source row was shifted into an adjacent grade/configuration column;
- prices, units, dates, footnotes and exceptions are correct;
- existing correct records were not duplicated or overwritten;
- unresolved cases remain explicitly deferred.

The package is not complete until both gates pass or a documented, non-blocking deferral is accepted under project governance.

## 7.1 Mandatory code preflight before commit and push

Every code or test change must pass a fail-fast preflight before it is committed or pushed. This applies even when the change is small, generated mechanically, or appears to be a one-line correction.

Required order:

1. Inspect the complete diff and confirm that every changed path belongs to the package manifest.
2. Compile every changed Python file (at minimum, run `python -m py_compile <changed-file.py>`; for broad Python changes run `python -m compileall -q tools tests`).
3. Import the changed production and test modules, then run the repository's test-discovery command or the narrowest equivalent used by CI.
4. Run the focused test module and the directly affected contract/regression tests.
5. Run the relevant repository validator and deterministic artifact checks.
6. Only after all applicable checks pass may the change be committed and pushed.

For test-file changes, syntax compilation and import/discovery are mandatory before running the test itself. A test command that cannot import its module is not a substitute for this preflight; record the import/discovery result explicitly.

Do not use broad text replacement or generated code edits without inspecting the resulting complete changed block and diff. After every automated edit, re-read the edited file from the repository and verify the exact changed lines. Reject literal escape sequences (for example, a textual `\\n` accidentally inserted into Python source) where real source newlines are required.

If local execution is unavailable, do not claim the preflight passed and do not publish the change as validated. Use an available repository CI/check workflow only when it can validate the candidate branch before merge; otherwise record the blocker and leave the change uncommitted/unpublished where possible.

A failed preflight blocks commit/push. Fix the first causal error, repeat the preflight from the beginning for the changed paths, and then run the final quality gate on the exact resulting head SHA. A later edit invalidates earlier validation of that file and requires the relevant checks to be repeated.

## 7. Efficient validation cadence

To reduce repeated CI failures without weakening quality:

- during implementation, run focused tests for each changed contract/path;
- after a logical batch, run the relevant importer/check and reconciliation comparison;
- batch deterministic mechanical updates (generated summaries, snapshots, counters and manifests) before final validation;
- diagnose a failure before changing code, data or test expectations;
- fix the root cause, not only the first visible assertion;
- after the last code/data/generated-file change, run the complete required quality matrix once on that exact final SHA;
- if any change is made after the full run, the previous full run no longer validates the new head; rerun the affected focused checks and the required final gate.

Do not repeatedly run the full matrix after each mechanical correction. Do not open a PR merely to discover basic focused-test failures when branch-only validation is available.

## 7.2 Mandatory repository-baseline and generated-documentation preflight

A package that adds, removes, renames or changes tests, tracked data files, source/import specifications, reports or project metadata may change repository-wide counters and generated documentation. The package author must reconcile these derived values before opening or updating a PR.

Required sequence after the final package edits and before PR publication:

1. Run the canonical state updater in check mode first:
   `python tools/dkb.py project-state --check`.
2. If the check identifies stale canonical counters or generated state, inspect the exact diff and update the canonical state using the repository-supported workflow:
   `python tools/dkb.py project-state --apply`.
3. Regenerate/check the managed documentation baseline:
   `python tools/dkb.py documentation-baseline --check`.
   If stale, run `python tools/dkb.py documentation-baseline --apply`, inspect every changed block, then rerun the check.
4. Rerun both check commands after all changes. Both must pass on the same candidate tree.
5. Inspect the complete diff and confirm that generated changes are limited to expected managed sections. Do not hand-edit generated summaries or counters when the canonical generator owns them.
6. Reconcile every changed baseline count with its actual source of truth (for example, discovered test count, tracked CSV inventory, or master-row count). Never copy a count from a prior PR, a conversation summary, or a stale report.
7. Include the baseline and documentation reconciliation in the PR validation notes. If local execution is unavailable, use a CI workflow that checks the candidate branch before merge; do not claim the checks passed without an observed result.

A test-count increase is not automatically a defect in the test suite. Determine whether the new test is intentional, discoverable and passing, then update the canonical baseline and generated documentation through the supported tooling. Do not delete a valid test, weaken an assertion, or change the expected count merely to make CI green.

The PR must not be considered ready while repository-baseline or generated-documentation checks are stale. A successful unit-test run does not override a failure in these repository consistency contracts.

**Failure-prevention rule:** after any test or tracked-file change, the pre-PR checklist must explicitly include both `project-state --check` and `documentation-baseline --check`; these checks are not optional just because the change appears local or adds only one test.

**Remote repair rule:** when local execution is unavailable, use the guarded GitHub Actions procedure in `project/BASELINE_REPAIR_WORKFLOW.md`. The workflow must verify an open same-repository PR and its exact head SHA, run canonical generators in a read-only job, restrict generated output to the six documented paths, and commit through a separate write-enabled job that does not execute PR code. It is a repair mechanism only; both baseline checks and the complete required CI matrix must pass again on the resulting exact PR head. Never hand-edit generated counters or weaken branch protection to make the repair work.

## 7.3 Enforced pre-PR release gate and branch-freshness control

This section converts the baseline/documentation preflight into a publication rule. It applies to every PR, including documentation-only, test-only, generated-data and one-line changes. A PR is not eligible for publication as ready-for-review, merge or release until the applicable checks below have passed on the exact candidate head.

### A. Separate validation layers

Record these outcomes separately; never summarize them as one generic "tests passed" result:

1. **Code/test integrity:** syntax compilation, import/discovery, focused tests and the complete required test suite.
2. **Repository-state integrity:** `project-state --check` and consistency of canonical counters.
3. **Generated-documentation integrity:** `documentation-baseline --check` and any other repository-defined generated-file checks.
4. **Source/domain fidelity:** independent evidence reconciliation under Gate B in section 6.
5. **CI/platform integrity:** all required workflow jobs, supported Python versions, operating systems and packaging checks.

A pass in one layer does not compensate for a failure or missing result in another. Mark an inapplicable layer explicitly with its reason and approved alternative; do not silently omit it.

### B. Mandatory publication sequence

On the candidate branch, in this order:

1. Fetch the latest target branch and record its exact SHA.
2. Confirm the candidate branch includes the latest target branch changes. If it does not, update/rebase/merge the target branch using the repository's approved workflow, resolve conflicts, and restart validation for the resulting tree.
3. Freeze implementation edits for the validation pass. Record the candidate head SHA.
4. Run syntax compilation, import/discovery, focused tests and directly affected regression/contract tests.
5. Run the full required test suite and repository validators.
6. Run `python tools/dkb.py project-state --check`; apply the canonical updater only if required, then rerun the check.
7. Run `python tools/dkb.py documentation-baseline --check`; apply the supported generator only if required, inspect its diff, then rerun the check.
8. If the package adds or materially refreshes any registered analytical report, run `python tools/dkb.py report-freshness` after the final JSON, Markdown, registry and finding edits. Resolve every reported error locally before commit/push; do not rely on the later CI run as the first report-contract check.
9. Run all remaining package-specific deterministic checks and independent source-fidelity review.
9. Inspect the complete diff, including generated files. Confirm no unexpected paths, stale counters, stale managed documentation, unrelated edits or unreviewed generated changes remain.
10. Commit/push the candidate and open/update the PR. Record the exact tested SHA and each validation result in the PR.
11. Confirm CI ran against that exact head SHA and every required job passed. If the head changes, the previous CI result no longer validates the PR; repeat the affected checks and the required full gate.
12. Recheck target-branch freshness and mergeability immediately before merge. If the target branch advanced and the candidate is no longer current under repository policy, update the branch and repeat validation.

### C. Hard stop conditions

Do not mark a PR ready, request final review, merge, or describe it as validated when any of these is true:

- a required validation layer has failed, has not run, or has no observable result;
- `project-state --check` or `documentation-baseline --check` reports drift;
- generated files were changed after the last relevant check;
- the tested SHA differs from the current PR head SHA;
- the PR branch is behind the target branch and has not been reconciled;
- a required CI job is pending, skipped without an approved alternative, cancelled or failed;
- the complete diff has not been inspected.

Keep the PR in draft/blocked state where supported, or leave it unpublished if the repository workflow allows. State the exact blocker and the command/job needed to clear it. Never bypass a failed check by weakening tests, editing generated counters manually, or treating a partial green run as full success.

### D. Failure recovery and revalidation

When a gate fails:

1. Diagnose the first causal failure using section 8; distinguish a product/test defect from stale repository metadata, generated-documentation drift, branch divergence or infrastructure failure.
2. Correct the root cause in scope.
3. Re-run the failed check and all checks invalidated by the correction.
4. Re-run both repository-state and generated-documentation checks together on the same tree.
5. Re-run the full required quality matrix on the final candidate SHA.
6. Verify that the PR head still equals the tested SHA.

A generated-file correction, test addition/removal, tracked-file change, merge/rebase or any other commit after validation invalidates at least the checks affected by that change. When in doubt, repeat the complete gate rather than infer that an earlier result still applies.

### E. CI enforcement expectation

The repository now defines `.github/workflows/repository-baselines.yml` with two independent GitHub Actions jobs:

- `Repository state / project-state --check`;
- `Generated documentation / documentation-baseline --check`.

Both run on pull requests, pushes to `main` and `dev/**`, and manual workflow dispatch. Their separate job names make each result independently visible. The existing `Quality` workflow remains responsible for the broader test and platform matrix.

These workflow definitions provide automatic PR feedback, but a workflow job is not necessarily a merge-blocking required check. The Project Owner confirmed on 2026-11-20 that the `main` branch protection rule requires all six status checks listed in section 15 and has **Require branches to be up to date before merging** enabled. Treat this owner-confirmed configuration as the standing repository baseline; do not ask the Project Owner to reconfirm it in later sessions. If direct API inspection is unavailable or returns a permissions error, retain this recorded confirmation rather than treating the setting as unknown. Re-check silently when an authorized inspection path is available, and ask the Project Owner again only if concrete evidence indicates that the rule may have changed.

Documentation alone does not enforce branch protection. Continue to verify that the required workflows actually ran successfully on the exact current PR head; the recorded protection rule does not replace exact-SHA CI validation.

### F. No local execution capability

If the active profile cannot execute the canonical generators or tests, do not fabricate their output, manually guess generated counters, or publish the candidate as validated. Use a verified CI workflow capable of running the checks on the candidate branch. If no such workflow is available, leave the PR blocked/unpublished and record the exact capability blocker.

## 7.4 Static analysis and report-contract regression gates

The required Quality workflow runs a pinned Ruff static-analysis pass on Python 3.14 before the full test suite:

```bash
python -m pip install --disable-pip-version-check ruff==0.14.10
python -m ruff check --select F821 tools scripts tests
```

This gate rejects undefined names in production code, scripts and tests before runtime test execution. It is deliberately limited to the undefined-name rule in this first rollout so it catches defects such as a test referring to an uninitialised or misspelled variable without introducing unrelated style churn. The check is part of the required `Python 3.14` Quality job; a failure blocks that required status check. Do not suppress a finding unless the code genuinely requires the exception and the suppression is narrowly documented.

For every change to master-data semantics, configuration contexts, report completeness specifications or report-generation behavior, add or update a focused regression test that asserts the exact expected contract—not merely that the report command exits successfully. Where a field is context-dependent (for example, fuel-specific capacity), assert each required context separately and verify that the generated report exposes each expected slot. Preserve a generic slot only when it remains an intentional part of the contract. A successful report generation is not proof that the specification includes every required context.

When a package changes a report specification or the data dimensions it describes, the PR validation notes must name the affected specification, the exact context/item combinations covered, and the regression test that protects them. If no executable contract exists for the affected specification, add one before publication or explicitly block the package pending an approved alternative.

The full test-discovery run remains mandatory: static analysis complements compilation and runtime tests; it does not replace either. The same pinned static-analysis command must be rerun on the final candidate tree after any Python edit.

### 7.4.1 Automatic exact-head and base-freshness gate

The required `Quality` workflow checks out the exact Pull Request head SHA, not GitHub's synthetic merge ref, and fetches the current target branch before validation. It fails closed unless the current target-branch commit is an ancestor of the tested PR head. This prevents a green run on a stale branch from being mistaken for validation of a branch that has not incorporated the current base.

The check runs automatically for every `pull_request` event in the Python quality matrix and does not require a maintainer prompt or manual opt-in. A failure means the branch must be updated from the current target branch; after that update, the complete required matrix must run again on the new exact head. The workflow's checkouts use full history so ancestry is evaluated from Git data, not from a shallow or synthetic merge checkout.

This check closes the time-of-run freshness gap, but it does not eliminate a race where the target branch advances after CI finishes. Immediately before merge, the maintainer must still re-fetch the PR and target branch, verify mergeability and exact current head SHA, and rely on GitHub's required status checks/up-to-date branch policy to block a stale merge.

## 8. CI failure diagnosis protocol

For every failed job:

1. Capture the exact workflow run ID, job name/ID, commit SHA and failing step.
2. Read the complete relevant log and identify the first causal error; later failures may be cascading symptoms.
3. Classify the failure using the six causes in section 5, or as environment/workflow infrastructure failure.
4. Inspect the exact source, changed paths, test, importer and relevant history.
5. State the root cause and evidence before editing.
6. Make the smallest in-scope correction.
7. Run the focused reproducer first.
8. Run the full required matrix on the final head.
9. Confirm the current PR head SHA still equals the SHA tested.

Do not claim CI passed based on a previous head, a partial workflow, a successful subset, or an unverified run.

## 9. Pull Request and merge gate

Before opening/updating a PR, verify:
- one logical package per PR;
- exact base and head SHA;
- only manifest/in-scope paths changed;
- source reconciliation artifact and acceptance criteria are present;
- focused checks passed;
- no unresolved evidence/model blocker is hidden.

Before merge, verify:
- PR is open and mergeable;
- current head SHA is the one with successful required CI;
- both technical-integrity and source-fidelity gates passed;
- no unresolved review, conflict or policy block exists;
- state/documentation can be advanced consistently.

A green badge alone is not a merge decision.

## 10. Session-start enforcement and reporting

At the start of every new chat/session and every continuation after a handoff:

- follow project/START_HERE.md from the beginning;
- read this protocol, not a remembered summary of it;
- verify canonical state and current GitHub state dynamically;
- identify the active user priority and package scope from repository state;
- apply both quality gates to every relevant data package.

If repository access is unavailable, do not pretend the bootstrap or validation happened. Continue only with safe analysis and clearly label it unverified.

Every package handoff/report must distinguish:
- implemented;
- focused-tested;
- source-reconciled;
- full-quality-tested (exact SHA);
- committed;
- pushed/published;
- PR-open;
- merged;
- deferred/blocked.

Never collapse these into a single word such as "done" when their states differ.

## 11. End-of-package review

At each package boundary, ask:

- Did we introduce a test tied to a mutable total that should instead test a scoped invariant?
- Did any test expectation change without independent source evidence?
- Did we verify the final data against the original source rather than only the importer?
- Did we preserve history, dates and exact applicability?
- Did we accidentally expand scope or duplicate existing facts?
- Are canonical state and generated documentation consistent?
- Can the next session resume from repository state without asking the user to repeat context?

Record material lessons and update this protocol only when a durable process change is justified.


## 12. Failure classification and test-suite health

A failing check is a diagnostic signal, not by itself proof that the feature under development is defective. Every failure must be classified before any corrective edit.

Use these distinct classes in reports and CI triage:

- **functional/regression failure** — production behavior or a durable business/data invariant is wrong;
- **test discovery/import failure** — the intended tests were not collected or could not be imported; this is a test-suite execution defect and must not be reported as a feature assertion failure;
- **test expectation defect** — the assertion encodes an obsolete or incorrectly scoped expectation, established only after reviewing the intended invariant and authoritative evidence;
- **canonical baseline drift** — a derived repository counter (including test count) is stale relative to the candidate tree;
- **generated-documentation drift** — a managed generated block is stale and must be regenerated by its canonical tool;
- **environment/workflow failure** — runner, dependency, permissions or workflow infrastructure prevented a valid check;
- **source-fidelity failure** — imported facts, mappings or provenance do not match the authoritative source.

Reports must identify the first causal error, not merely list downstream failures. State separately whether functional tests passed, whether all tests were discovered/imported, whether baseline checks passed, whether documentation checks passed, and whether source fidelity was accepted.

A changed discovered-test count is not a functional failure. Confirm the added/removed tests are intentional and discoverable, then update the canonical baseline through the supported generator. Never remove a valid test or weaken an assertion solely to restore a count.

## 13. Generator and test-independence requirements

For every data importer, report generator, baseline updater or documentation generator, add or retain checks for the following properties where applicable:

1. **Determinism:** identical inputs and tool versions produce byte-identical outputs; verify with repeated generation or an explicit check mode.
2. **Idempotency:** applying the same import/update twice does not create duplicate facts, duplicate events, repeated migrations or further file changes.
3. **No-op stability:** when inputs are unchanged, check mode succeeds and the working tree remains unchanged.
4. **Input/output boundary:** tests identify the exact source IDs, fixtures, dates and configuration scope; they do not silently use mutable global totals as local contracts.
5. **Independent oracle:** at least critical mappings and representative values are checked against source evidence or independently curated fixtures, not only against output produced by the same transformation logic.
6. **Negative-space safety:** omission, blank cells, explicit dashes and unknown states remain distinct; tests prevent unsupported inference.
7. **Regression safety:** existing correct records are preserved, and the importer does not overwrite unrelated scopes.

Do not claim that a generator is correct merely because its output matches a snapshot it generated itself. Snapshot tests are useful for deterministic formatting, but source fidelity requires an independent evidence check.

## 14. Candidate-tree and exact-SHA validation discipline

The final validation target is an immutable candidate tree identified by its exact head SHA. The required sequence is:

1. Finish code, tests, data and documentation edits.
2. Reconcile canonical state and generated documentation using the prescribed check/apply/check sequence.
3. Inspect the complete diff, including generated blocks and source manifests.
4. Run focused checks, then the complete required CI matrix on the candidate SHA.
5. Confirm every required job reports success for that exact SHA; record skipped jobs separately with their workflow-defined reason.
6. Re-fetch the PR and branch immediately before merge; confirm the current head SHA is unchanged and the target branch is up to date.
7. If any commit, rebase, generated-file update or other edit changes the candidate tree, invalidate the previous final validation and repeat all affected checks plus the required final matrix.

A successful run on a parent commit, another branch, an earlier PR head or only a subset of jobs does not validate the current candidate. Never infer that a PR is merge-safe from a green badge without checking run SHA, required jobs, source-fidelity result and branch freshness.

## 15. Branch protection and merge enforcement

CI reporting and merge enforcement are separate controls. A workflow that reports failed checks does not block merging unless repository rules require the relevant checks.

### Recorded `main` protection baseline — Project Owner confirmed 2026-11-20

The Project Owner explicitly confirmed that the `main` branch protection rule requires all six checks below and has **Require branches to be up to date before merging** enabled:

1. `Package workflow / Windows`
2. `Repository state / project-state --check`
3. `Generated documentation / documentation-baseline --check`
4. `Python 3.10`
5. `Python 3.13`
6. `Python 3.14`

This is a durable owner-confirmed repository fact. Future maintainers must use it as the default baseline and must not ask the Project Owner to repeat the confirmation merely because the GitHub API/connector cannot read branch-protection settings. A 403/permission limitation is an inspection limitation, not evidence that the rule is absent or unknown. If an authorized API inspection later becomes available, verify the rule without interrupting the Project Owner. Request reconfirmation only when concrete repository evidence suggests that the protection rule has changed or been removed.

The recorded configuration does not replace per-PR verification: immediately before merge, confirm that all six required checks succeeded on the exact current PR head and that the branch is up to date with `main`. If a PR is behind, update/rebase it and rerun the complete required matrix on the resulting exact head. Never bypass or silently weaken repository policy.

If future direct evidence shows that any required check or the up-to-date requirement is missing, treat that as a governance regression and apply the procedural no-merge rule until an authorized administrator restores the recorded baseline.

## 16. Recommended failure-repair sequence

For a failed CI run, use this order and stop at the first causal defect:

1. Verify run ID, workflow, job, runner, branch and exact tested SHA.
2. Read the failing step and preceding log context; distinguish the first cause from cascades.
3. Reproduce with the narrowest available check where execution is available.
4. Classify the failure using section 12.
5. Inspect the relevant source, test, canonical baseline or generated block.
6. Correct only the confirmed root cause using the canonical tool where one exists.
7. Re-run the focused reproducer and all checks invalidated by the edit.
8. Run final validation on the exact resulting head SHA.
9. Report the classification, evidence, repair, remaining uncertainty and exact SHA.

A test must not compare a newly generated result to a previous mutable result unless the test is explicitly verifying historical compatibility. Prefer fixed, independently curated fixtures and invariants. Historical comparison is valid only when the historical artifact is an intentional, versioned contract and its role is documented.


## End of protocol

## 17. Cross-file change transaction and regression-prevention controls

This section is mandatory for every package that changes source registries, import specifications, master data, tests, repository metadata, generated artifacts or documentation. Its purpose is to prevent a valid change in one file from leaving dependent contracts stale elsewhere.

### A. Build the dependency impact list before editing

Before the first edit, identify the complete dependency set for the changed object. At minimum consider:

- source files and their registry rows;
- source IDs, archive paths, external references and SHA-256 values;
- import specifications, importer contracts and source-specific tests;
- master CSVs, manifests, reconciliation reports and derived indexes;
- canonical counters and project/state.json;
- generated state summaries and managed documentation blocks;
- workflow definitions, validation scripts and release artifacts.

Record affected and deliberately unaffected paths in the package manifest. Do not assume a change is local merely because only one source file was initially edited.

### B. Treat related updates as one logical transaction

A source or schema change and its dependent contracts must be updated in the same package/PR unless a documented dependency requires a separate ordered package. Do not leave a known inconsistent intermediate state marked complete.

For every registered archived file:
- verify that a non-empty repository path resolves to an existing tracked file;
- compute SHA-256 from the exact original bytes when those bytes are available;
- never infer or fabricate a digest;
- distinguish an external source URL, an owner-supplied original, and a repository-archived binary;
- if binary transfer is unavailable, record the exact limitation and keep the archive state explicitly pending.

For every source-registry/importer/test change, inspect all contracts that assert the affected source ID, path, digest, date, scope or expected status. Update expectations only after verifying the authoritative source and the intended invariant.

### C. Canonical generators own derived state

Never manually synchronize counters or generated baseline blocks by copying numbers between files.

Use the repository's canonical generators/checks for project-state counters and summaries, documentation baseline blocks, generated manifests, snapshots and other deterministic outputs.

Run check mode first, inspect the proposed changes, apply only through the supported generator, then rerun check mode. All relevant checks must pass on the same candidate tree. If the generator cannot run in the active environment, use a CI job that demonstrably runs it on the exact candidate SHA; otherwise mark the package blocked rather than hand-editing generated output and claiming validation.

### D. Diagnose before changing expectations

For every failure, preserve the first causal error and classify it before editing. Determine whether the source, implementation, importer, test expectation, canonical baseline, generated documentation, branch state or CI environment is wrong.

Never change an assertion only to make CI green; compare current generated output with a previous mutable output unless historical compatibility is the explicit contract; weaken a correct invariant to accommodate a defect; treat fixture/setup log messages as failures without checking the test result; or treat a stale count as proof of a functional regression.

When an expectation legitimately changes, cite the source-backed reason in the test or adjacent fixture/report. Prefer stable invariants and independently curated expected values over mutable global totals.

### E. Mandatory pre-PR consistency matrix

Before publishing or updating any PR, record an explicit pass/fail/not-applicable result for each applicable item:

1. Changed-file syntax, import and test discovery.
2. Focused tests for every changed contract/importer.
3. Full required test suite on the candidate tree or observable CI equivalent.
4. Source registry ↔ import specification ↔ importer ↔ tests consistency.
5. Archive path existence and independently computed hashes where binary bytes are available.
6. Master data, manifest and reconciliation consistency.
7. python tools/dkb.py project-state --check.
8. python tools/dkb.py documentation-baseline --check.
9. Complete diff and changed-path scope review.
10. Independent source-fidelity review where source/domain data changed.
11. Exact candidate HEAD SHA and target-branch freshness.
12. All required CI jobs on that exact HEAD SHA.

A result is not a pass if it is unknown, assumed, inherited from a different SHA, or represented only by an unverified statement. Use BLOCKED for checks that cannot be run; do not silently mark them not applicable.

### F. Change invalidation rules

Any new commit, edit, generated-file update, source registry change, test addition/removal, rebase or merge invalidates the checks affected by that change. A changed candidate HEAD requires the full required final quality matrix to run against the new SHA. Immediately before merge, fetch the PR again and confirm the tested SHA is still its current head.

### G. Completion and session handoff

A package may be described as complete only when all applicable matrix items have observable passing evidence; source fidelity is accepted or an explicitly approved non-blocking deferral is recorded; the exact tested SHA and PR/commit are recorded; canonical state and generated documentation reflect the durable repository result; and unresolved limitations and the next package are recorded.

Every new chat/session must load this protocol through project/START_HERE.md. A short user instruction such as kontynuuj does not waive any control. If the protocol cannot be read or a mandatory check cannot be verified, enter recovery/diagnostic mode and report the exact blocker.

## 7.3 PDF extraction toolchain reproducibility

Repository-generated PDF text artifacts are byte-sensitive to the Poppler tools used for extraction. A moving runner image or an opportunistic system package upgrade must not silently change canonical extraction output.

For the committed official PDF candidate ledger:

- use the `ubuntu-24.04` GitHub Actions runner for the Linux quality job;
- use Poppler `pdftotext` and `pdfinfo` version `24.02.0`, matching the committed ledger metadata;
- verify both executable versions explicitly before running the repository PDF artifact check;
- make `tools/pdf_candidate_ledger.py` fail closed when `pdftotext` is missing or has a different version;
- compare the freshly generated backend-version metadata with the committed artifact before comparing complete output bytes.

Do not regenerate and commit a PDF-derived artifact merely to accommodate a newer runner. A toolchain change requires a deliberate package: review the extraction differences against the registered source PDFs, update the toolchain contract and documentation, regenerate the artifacts, and independently validate the changed candidate inventory. A mismatch is an environment/toolchain failure until proven otherwise; it is not permission to weaken or skip the artifact test.


## 7.4 Fail-fast data package preflight

Before the full test and quality matrix, run:

```bash
python tools/dkb.py package-preflight
```

The command performs a read-only structural pass over all CSV and JSON files under `data/`:

- every CSV is parsed with the canonical strict CSV validator, including exact row-width and quoting checks;
- every JSON file is decoded as UTF-8 and parsed with the standard JSON parser;
- missing data roots, unreadable files, malformed quoting, unexpected CSV field counts and invalid JSON are fatal.

The Quality GitHub Actions workflow runs this preflight before Python compilation and tests. Run it again after any edit to a data CSV or JSON file. It is a fast structural gate, not a replacement for `python tools/dkb.py validate`, the complete quality gate, repository-state checks, generated-documentation checks or independent source-fidelity review.

All CSV-writing code must use `csv.writer`, `csv.DictWriter` or another standards-compliant CSV serializer. Do not build CSV rows by joining raw values with commas. Tests for a CSV-producing importer or report must include a field containing a comma (and, where relevant, quotes or a newline) so serialization regressions are caught.

When data changes, identify dependent reports, manifests, reconciliation receipts and historical closure summaries before editing. Refresh derived artifacts only through their canonical generator or documented deterministic procedure, then run their verification checks. A successful CSV parse does not prove dependent artifacts are current.


## 18. Semantic contracts for source-verification tests

Tests must validate source facts and machine-readable contracts, not incidental prose.

- Do not assert an entire `notes` sentence, paragraph, punctuation, word order or editorial phrase unless the exact text is itself a controlled identifier or externally mandated literal.
- For source verification, assert the structured facts that carry meaning: source identity/code, verification state where modeled, SHA-256, byte size, page count, expected source markers, archive path, provenance reference and manifest relationship. Validate only fields that actually exist in the canonical schema; do not invent parallel metadata fields solely to satisfy a test.
- When a fact is currently represented only in free text, prefer extracting a stable structured field in a separately scoped schema change. Until then, test the necessary evidence using narrowly scoped semantic predicates, and preserve human-readable notes as explanatory provenance rather than a machine interface.
- Tests must include both positive and negative cases: valid evidence with different wording passes; missing or contradictory integrity/provenance evidence fails.
- A change to explanatory prose must not require test edits when the underlying source facts are unchanged. Conversely, changing a hash, source identity, archive path or verification result must be detected.
- Before changing a failing assertion, inspect the producer, canonical data, schema, source artifact and all supported Python versions. Do not weaken a test merely to make CI green.

## 19. Failure classification and regression containment

For each failed CI job, identify the first causal assertion or command and classify it as one of: product/code defect, data/schema defect, stale test contract, generated-artifact drift, environment/dependency failure, or expected negative-test output. Correlated failures across Python versions count as one root cause when they share the same causal assertion.

The correction must be made at the authoritative layer: producer, canonical data, schema, test contract, generator or environment pin. Add a focused regression test for the root cause, then run focused tests before the full required matrix. Record the exact final HEAD SHA and require all mandatory checks to pass on that SHA before merge.


## 20. Source archive manifest integrity preflight

The read-only \`python tools/dkb.py package-preflight\` command validates CSV and JSON structure and, for every verified \`data/source_intake/*_capture.json\` manifest, checks the archive contract against the existing repository schema:

- exactly one source-registry row matches \`source_code\`;
- the registry URL and SHA-256 match the manifest;
- a populated registry \`file_path\` matches the manifest archive path (an intentionally blank path remains a separately visible registration gap until its source-registration package closes it);
- the archived binary exists inside the repository, its actual byte length matches \`file_size_bytes\`, and its SHA-256 is recomputed from the actual bytes and matches the manifest;
- the sibling \`.sha256\` sidecar matches both the manifest digest and archive path;
- the verification status is explicitly \`verified_*\`, the page count is positive, optional expected hash/size/page-count fields agree, and the recorded first-page markers are present in the captured first-page text with no missing markers.

The check is read-only. It does not rewrite source rows, manifests, PDFs or sidecars. It does not parse the PDF again to independently derive its page count, re-extract first-page text, inspect rendered pages, or establish complete source assimilation. Those remain responsibilities of the capture workflow and the independent source-fidelity review.

Explanatory \`notes\` are not a machine interface. A change to editorial wording must not invalidate source-integrity tests when the structured identity, archive bytes, manifest and registry relationships remain unchanged. Conversely, a changed binary, digest, size, marker state, source identity or archive relationship must fail the preflight.

The Quality workflow runs this check before compilation/tests and runs the focused Bigster source-archive regression on Python 3.14 before the full quality gate. The same focused regression is also included in the standard unit-test discovery on Python 3.10 and 3.13. A successful preflight is not a substitute for the full quality matrix, repository-state/documentation checks or source-fidelity review.


## 21. Unified fail-closed package consistency gate

Every Pull Request must pass one observable, fail-closed repository-consistency gate in addition to the supported Python and Windows quality matrix. The existing required status context `Repository state / project-state --check` now executes these checks in sequence on the same checked-out candidate commit:

1. `python tools/dkb.py package-preflight` — validate every repository data CSV/JSON file and the registered source-capture manifest integrity covered by the canonical preflight;
2. `python tools/dkb.py project-state --check` — compare live repository counts and canonical state, validate state references, and verify the generated state summary;
3. `python tools/dkb.py documentation-baseline --check` — verify all managed documentation baseline blocks against live repository data.

The separately required `Generated documentation / documentation-baseline --check` status remains in place as an independent, clearly named check. The additional invocation inside the repository-state job ensures that the repository-state required context cannot pass when any of the three package-consistency layers fails.

The gate is read-only. It must never silently repair a candidate branch in CI. If a check fails, the maintainer diagnoses the first causal discrepancy, applies the canonical generator locally or through an explicitly validated candidate workflow, inspects the complete resulting diff, and reruns all three checks on the same resulting tree. Manual counter copying, hand-edited generated blocks and weakened validators are prohibited.

The gate complements rather than replaces:
- the full Python and Windows quality matrix;
- importer-specific focused tests and idempotency checks;
- independent source-to-master fidelity review;
- the complete PR diff, exact-head, freshness, conflict and technical-review requirements.

For each package, the PR validation record must state the result of all three subchecks separately. A single green umbrella status does not justify describing an unobserved subcheck or source-fidelity review as passed.

The gate is intentionally wired into an existing required status context. It does not add or rename branch-protection contexts and therefore preserves the repository's six-check single-maintainer merge policy.

## 7.3 Isolated package-publishing tests

Package-publishing tests must run against disposable temporary repositories and
local bare remotes. They must not share the checked-out repository's Git index,
push to the real GitHub repository, or inherit ambient GitHub Actions repository
and Pull Request context. Each test must clean up its temporary directory.

The test environment must remove all variables listed in
`package_workflow.GIT_CONTEXT_VARIABLES`, disable system Git configuration,
use a temporary global Git configuration, and disable terminal prompts.
Contract tests must verify that `git_environment()` strips ambient GitHub
context even when such variables are present in the parent process.

Negative-path tests must prove remote safety, not merely inspect the returned
error code:
- rejection of an extra untracked path leaves the bare remote branch absent;
- rejection of an extra staged path leaves the bare remote branch absent;
- an injected local bare-remote `pre-receive` hook rejects the push, leaves
  the remote branch absent, and records a single local package commit with a
  failed-push handoff.

The deliberately injected hook produces an expected error log. Diagnose the
test assertions and final CI conclusion rather than treating that expected log
alone as a production push failure. Never replace these isolated tests with a
push against the live project remote.

## 8. CI failure diagnosis protocol

For every failed job:

1. Capture the exact workflow run ID, job name/ID, commit SHA and failing step.
2. Read the complete relevant log and identify the first causal error; later failures may be cascading symptoms.
3. Classify the failure using the six causes in section 5, or as environment/workflow infrastructure failure.
4. Inspect the exact source, changed paths, test, importer and relevant history.
5. State the root cause and evidence before editing.
6. Make the smallest in-scope correction.
7. Run the focused reproducer first.
8. Run the full required matrix on the final head.
9. Confirm the current PR head SHA still equals the SHA tested.

Do not claim CI passed based on a previous head, a partial workflow, a successful subset, or an unverified run.

## 9. Pull Request and merge gate

Before opening/updating a PR, verify:
- one logical package per PR;
- exact base and head SHA;
- only manifest/in-scope paths changed;
- source reconciliation artifact and acceptance criteria are present;
- focused checks passed;
- no unresolved evidence/model blocker is hidden.

Before merge, verify:
- PR is open and mergeable;
- current head SHA is the one with successful required CI;
- both technical-integrity and source-fidelity gates passed;
- no unresolved review, conflict or policy block exists;
- state/documentation can be advanced consistently.

A green badge alone is not a merge decision.

## 10. Session-start enforcement and reporting

At the start of every new chat/session and every continuation after a handoff:

- follow project/START_HERE.md from the beginning;
- read this protocol, not a remembered summary of it;
- verify canonical state and current GitHub state dynamically;
- identify the active user priority and package scope from repository state;
- apply both quality gates to every relevant data package.

If repository access is unavailable, do not pretend the bootstrap or validation happened. Continue only with safe analysis and clearly label it unverified.

Every package handoff/report must distinguish:
- implemented;
- focused-tested;
- source-reconciled;
- full-quality-tested (exact SHA);
- committed;
- pushed/published;
- PR-open;
- merged;
- deferred/blocked.

Never collapse these into a single word such as "done" when their states differ.

## 11. End-of-package review

At each package boundary, ask:

- Did we introduce a test tied to a mutable total that should instead test a scoped invariant?
- Did any test expectation change without independent source evidence?
- Did we verify the final data against the original source rather than only the importer?
- Did we preserve history, dates and exact applicability?
- Did we accidentally expand scope or duplicate existing facts?
- Are canonical state and generated documentation consistent?
- Can the next session resume from repository state without asking the user to repeat context?

Record material lessons and update this protocol only when a durable process change is justified.


## 12. Failure classification and test-suite health

A failing check is a diagnostic signal, not by itself proof that the feature under development is defective. Every failure must be classified before any corrective edit.

Use these distinct classes in reports and CI triage:

- **functional/regression failure** — production behavior or a durable business/data invariant is wrong;
- **test discovery/import failure** — the intended tests were not collected or could not be imported; this is a test-suite execution defect and must not be reported as a feature assertion failure;
- **test expectation defect** — the assertion encodes an obsolete or incorrectly scoped expectation, established only after reviewing the intended invariant and authoritative evidence;
- **canonical baseline drift** — a derived repository counter (including test count) is stale relative to the candidate tree;
- **generated-documentation drift** — a managed generated block is stale and must be regenerated by its canonical tool;
- **environment/workflow failure** — runner, dependency, permissions or workflow infrastructure prevented a valid check;
- **source-fidelity failure** — imported facts, mappings or provenance do not match the authoritative source.

Reports must identify the first causal error, not merely list downstream failures. State separately whether functional tests passed, whether all tests were discovered/imported, whether baseline checks passed, whether documentation checks passed, and whether source fidelity was accepted.

A changed discovered-test count is not a functional failure. Confirm the added/removed tests are intentional and discoverable, then update the canonical baseline through the supported generator. Never remove a valid test or weaken an assertion solely to restore a count.

## 13. Generator and test-independence requirements

For every data importer, report generator, baseline updater or documentation generator, add or retain checks for the following properties where applicable:

1. **Determinism:** identical inputs and tool versions produce byte-identical outputs; verify with repeated generation or an explicit check mode.
2. **Idempotency:** applying the same import/update twice does not create duplicate facts, duplicate events, repeated migrations or further file changes.
3. **No-op stability:** when inputs are unchanged, check mode succeeds and the working tree remains unchanged.
4. **Input/output boundary:** tests identify the exact source IDs, fixtures, dates and configuration scope; they do not silently use mutable global totals as local contracts.
5. **Independent oracle:** at least critical mappings and representative values are checked against source evidence or independently curated fixtures, not only against output produced by the same transformation logic.
6. **Negative-space safety:** omission, blank cells, explicit dashes and unknown states remain distinct; tests prevent unsupported inference.
7. **Regression safety:** existing correct records are preserved, and the importer does not overwrite unrelated scopes.

Do not claim that a generator is correct merely because its output matches a snapshot it generated itself. Snapshot tests are useful for deterministic formatting, but source fidelity requires an independent evidence check.

## 14. Candidate-tree and exact-SHA validation discipline

The final validation target is an immutable candidate tree identified by its exact head SHA. The required sequence is:

1. Finish code, tests, data and documentation edits.
2. Reconcile canonical state and generated documentation using the prescribed check/apply/check sequence.
3. Inspect the complete diff, including generated blocks and source manifests.
4. Run focused checks, then the complete required CI matrix on the candidate SHA.
5. Confirm every required job reports success for that exact SHA; record skipped jobs separately with their workflow-defined reason.
6. Re-fetch the PR and branch immediately before merge; confirm the current head SHA is unchanged and the target branch is up to date.
7. If any commit, rebase, generated-file update or other edit changes the candidate tree, invalidate the previous final validation and repeat all affected checks plus the required final matrix.

A successful run on a parent commit, another branch, an earlier PR head or only a subset of jobs does not validate the current candidate. Never infer that a PR is merge-safe from a green badge without checking run SHA, required jobs, source-fidelity result and branch freshness.

## 15. Branch protection and merge enforcement

CI reporting and merge enforcement are separate controls. A workflow that reports failed checks does not block merging unless repository rules require the relevant checks.

### Recorded `main` protection baseline — Project Owner confirmed 2026-11-20

The Project Owner explicitly confirmed that the `main` branch protection rule requires all six checks below and has **Require branches to be up to date before merging** enabled:

1. `Package workflow / Windows`
2. `Repository state / project-state --check`
3. `Generated documentation / documentation-baseline --check`
4. `Python 3.10`
5. `Python 3.13`
6. `Python 3.14`

This is a durable owner-confirmed repository fact. Future maintainers must use it as the default baseline and must not ask the Project Owner to repeat the confirmation merely because the GitHub API/connector cannot read branch-protection settings. A 403/permission limitation is an inspection limitation, not evidence that the rule is absent or unknown. If an authorized API inspection later becomes available, verify the rule without interrupting the Project Owner. Request reconfirmation only when concrete repository evidence suggests that the protection rule has changed or been removed.

The recorded configuration does not replace per-PR verification: immediately before merge, confirm that all six required checks succeeded on the exact current PR head and that the branch is up to date with `main`. If a PR is behind, update/rebase it and rerun the complete required matrix on the resulting exact head. Never bypass or silently weaken repository policy.

If future direct evidence shows that any required check or the up-to-date requirement is missing, treat that as a governance regression and apply the procedural no-merge rule until an authorized administrator restores the recorded baseline.

## 16. Recommended failure-repair sequence

For a failed CI run, use this order and stop at the first causal defect:

1. Verify run ID, workflow, job, runner, branch and exact tested SHA.
2. Read the failing step and preceding log context; distinguish the first cause from cascades.
3. Reproduce with the narrowest available check where execution is available.
4. Classify the failure using section 12.
5. Inspect the relevant source, test, canonical baseline or generated block.
6. Correct only the confirmed root cause using the canonical tool where one exists.
7. Re-run the focused reproducer and all checks invalidated by the edit.
8. Run final validation on the exact resulting head SHA.
9. Report the classification, evidence, repair, remaining uncertainty and exact SHA.

A test must not compare a newly generated result to a previous mutable result unless the test is explicitly verifying historical compatibility. Prefer fixed, independently curated fixtures and invariants. Historical comparison is valid only when the historical artifact is an intentional, versioned contract and its role is documented.


## End of protocol

## 17. Cross-file change transaction and regression-prevention controls

This section is mandatory for every package that changes source registries, import specifications, master data, tests, repository metadata, generated artifacts or documentation. Its purpose is to prevent a valid change in one file from leaving dependent contracts stale elsewhere.

### A. Build the dependency impact list before editing

Before the first edit, identify the complete dependency set for the changed object. At minimum consider:

- source files and their registry rows;
- source IDs, archive paths, external references and SHA-256 values;
- import specifications, importer contracts and source-specific tests;
- master CSVs, manifests, reconciliation reports and derived indexes;
- canonical counters and project/state.json;
- generated state summaries and managed documentation blocks;
- workflow definitions, validation scripts and release artifacts.

Record affected and deliberately unaffected paths in the package manifest. Do not assume a change is local merely because only one source file was initially edited.

### B. Treat related updates as one logical transaction

A source or schema change and its dependent contracts must be updated in the same package/PR unless a documented dependency requires a separate ordered package. Do not leave a known inconsistent intermediate state marked complete.

For every registered archived file:
- verify that a non-empty repository path resolves to an existing tracked file;
- compute SHA-256 from the exact original bytes when those bytes are available;
- never infer or fabricate a digest;
- distinguish an external source URL, an owner-supplied original, and a repository-archived binary;
- if binary transfer is unavailable, record the exact limitation and keep the archive state explicitly pending.

For every source-registry/importer/test change, inspect all contracts that assert the affected source ID, path, digest, date, scope or expected status. Update expectations only after verifying the authoritative source and the intended invariant.

### C. Canonical generators own derived state

Never manually synchronize counters or generated baseline blocks by copying numbers between files.

Use the repository's canonical generators/checks for project-state counters and summaries, documentation baseline blocks, generated manifests, snapshots and other deterministic outputs.

Run check mode first, inspect the proposed changes, apply only through the supported generator, then rerun check mode. All relevant checks must pass on the same candidate tree. If the generator cannot run in the active environment, use a CI job that demonstrably runs it on the exact candidate SHA; otherwise mark the package blocked rather than hand-editing generated output and claiming validation.

### D. Diagnose before changing expectations

For every failure, preserve the first causal error and classify it before editing. Determine whether the source, implementation, importer, test expectation, canonical baseline, generated documentation, branch state or CI environment is wrong.

Never change an assertion only to make CI green; compare current generated output with a previous mutable output unless historical compatibility is the explicit contract; weaken a correct invariant to accommodate a defect; treat fixture/setup log messages as failures without checking the test result; or treat a stale count as proof of a functional regression.

When an expectation legitimately changes, cite the source-backed reason in the test or adjacent fixture/report. Prefer stable invariants and independently curated expected values over mutable global totals.

### E. Mandatory pre-PR consistency matrix

Before publishing or updating any PR, record an explicit pass/fail/not-applicable result for each applicable item:

1. Changed-file syntax, import and test discovery.
2. Focused tests for every changed contract/importer.
3. Full required test suite on the candidate tree or observable CI equivalent.
4. Source registry ↔ import specification ↔ importer ↔ tests consistency.
5. Archive path existence and independently computed hashes where binary bytes are available.
6. Master data, manifest and reconciliation consistency.
7. python tools/dkb.py project-state --check.
8. python tools/dkb.py documentation-baseline --check.
9. Complete diff and changed-path scope review.
10. Independent source-fidelity review where source/domain data changed.
11. Exact candidate HEAD SHA and target-branch freshness.
12. All required CI jobs on that exact HEAD SHA.

A result is not a pass if it is unknown, assumed, inherited from a different SHA, or represented only by an unverified statement. Use BLOCKED for checks that cannot be run; do not silently mark them not applicable.

### F. Change invalidation rules

Any new commit, edit, generated-file update, source registry change, test addition/removal, rebase or merge invalidates the checks affected by that change. A changed candidate HEAD requires the full required final quality matrix to run against the new SHA. Immediately before merge, fetch the PR again and confirm the tested SHA is still its current head.

### G. Completion and session handoff

A package may be described as complete only when all applicable matrix items have observable passing evidence; source fidelity is accepted or an explicitly approved non-blocking deferral is recorded; the exact tested SHA and PR/commit are recorded; canonical state and generated documentation reflect the durable repository result; and unresolved limitations and the next package are recorded.

Every new chat/session must load this protocol through project/START_HERE.md. A short user instruction such as kontynuuj does not waive any control. If the protocol cannot be read or a mandatory check cannot be verified, enter recovery/diagnostic mode and report the exact blocker.

## 7.3 PDF extraction toolchain reproducibility

Repository-generated PDF text artifacts are byte-sensitive to the Poppler tools used for extraction. A moving runner image or an opportunistic system package upgrade must not silently change canonical extraction output.

For the committed official PDF candidate ledger:

- use the `ubuntu-24.04` GitHub Actions runner for the Linux quality job;
- use Poppler `pdftotext` and `pdfinfo` version `24.02.0`, matching the committed ledger metadata;
- verify both executable versions explicitly before running the repository PDF artifact check;
- make `tools/pdf_candidate_ledger.py` fail closed when `pdftotext` is missing or has a different version;
- compare the freshly generated backend-version metadata with the committed artifact before comparing complete output bytes.

Do not regenerate and commit a PDF-derived artifact merely to accommodate a newer runner. A toolchain change requires a deliberate package: review the extraction differences against the registered source PDFs, update the toolchain contract and documentation, regenerate the artifacts, and independently validate the changed candidate inventory. A mismatch is an environment/toolchain failure until proven otherwise; it is not permission to weaken or skip the artifact test.


## 7.4 Fail-fast data package preflight

Before the full test and quality matrix, run:

```bash
python tools/dkb.py package-preflight
```

The command performs a read-only structural pass over all CSV and JSON files under `data/`:

- every CSV is parsed with the canonical strict CSV validator, including exact row-width and quoting checks;
- every JSON file is decoded as UTF-8 and parsed with the standard JSON parser;
- missing data roots, unreadable files, malformed quoting, unexpected CSV field counts and invalid JSON are fatal.

The Quality GitHub Actions workflow runs this preflight before Python compilation and tests. Run it again after any edit to a data CSV or JSON file. It is a fast structural gate, not a replacement for `python tools/dkb.py validate`, the complete quality gate, repository-state checks, generated-documentation checks or independent source-fidelity review.

All CSV-writing code must use `csv.writer`, `csv.DictWriter` or another standards-compliant CSV serializer. Do not build CSV rows by joining raw values with commas. Tests for a CSV-producing importer or report must include a field containing a comma (and, where relevant, quotes or a newline) so serialization regressions are caught.

When data changes, identify dependent reports, manifests, reconciliation receipts and historical closure summaries before editing. Refresh derived artifacts only through their canonical generator or documented deterministic procedure, then run their verification checks. A successful CSV parse does not prove dependent artifacts are current.


## 18. Semantic contracts for source-verification tests

Tests must validate source facts and machine-readable contracts, not incidental prose.

- Do not assert an entire `notes` sentence, paragraph, punctuation, word order or editorial phrase unless the exact text is itself a controlled identifier or externally mandated literal.
- For source verification, assert the structured facts that carry meaning: source identity/code, verification state where modeled, SHA-256, byte size, page count, expected source markers, archive path, provenance reference and manifest relationship. Validate only fields that actually exist in the canonical schema; do not invent parallel metadata fields solely to satisfy a test.
- When a fact is currently represented only in free text, prefer extracting a stable structured field in a separately scoped schema change. Until then, test the necessary evidence using narrowly scoped semantic predicates, and preserve human-readable notes as explanatory provenance rather than a machine interface.
- Tests must include both positive and negative cases: valid evidence with different wording passes; missing or contradictory integrity/provenance evidence fails.
- A change to explanatory prose must not require test edits when the underlying source facts are unchanged. Conversely, changing a hash, source identity, archive path or verification result must be detected.
- Before changing a failing assertion, inspect the producer, canonical data, schema, source artifact and all supported Python versions. Do not weaken a test merely to make CI green.

## 19. Failure classification and regression containment

For each failed CI job, identify the first causal assertion or command and classify it as one of: product/code defect, data/schema defect, stale test contract, generated-artifact drift, environment/dependency failure, or expected negative-test output. Correlated failures across Python versions count as one root cause when they share the same causal assertion.

The correction must be made at the authoritative layer: producer, canonical data, schema, test contract, generator or environment pin. Add a focused regression test for the root cause, then run focused tests before the full required matrix. Record the exact final HEAD SHA and require all mandatory checks to pass on that SHA before merge.


## 20. Source archive manifest integrity preflight

The read-only \`python tools/dkb.py package-preflight\` command validates CSV and JSON structure and, for every verified \`data/source_intake/*_capture.json\` manifest, checks the archive contract against the existing repository schema:

- exactly one source-registry row matches \`source_code\`;
- the registry URL and SHA-256 match the manifest;
- a populated registry \`file_path\` matches the manifest archive path (an intentionally blank path remains a separately visible registration gap until its source-registration package closes it);
- the archived binary exists inside the repository, its actual byte length matches \`file_size_bytes\`, and its SHA-256 is recomputed from the actual bytes and matches the manifest;
- the sibling \`.sha256\` sidecar matches both the manifest digest and archive path;
- the verification status is explicitly \`verified_*\`, the page count is positive, optional expected hash/size/page-count fields agree, and the recorded first-page markers are present in the captured first-page text with no missing markers.

The check is read-only. It does not rewrite source rows, manifests, PDFs or sidecars. It does not parse the PDF again to independently derive its page count, re-extract first-page text, inspect rendered pages, or establish complete source assimilation. Those remain responsibilities of the capture workflow and the independent source-fidelity review.

Explanatory \`notes\` are not a machine interface. A change to editorial wording must not invalidate source-integrity tests when the structured identity, archive bytes, manifest and registry relationships remain unchanged. Conversely, a changed binary, digest, size, marker state, source identity or archive relationship must fail the preflight.

The Quality workflow runs this check before compilation/tests and runs the focused Bigster source-archive regression on Python 3.14 before the full quality gate. The same focused regression is also included in the standard unit-test discovery on Python 3.10 and 3.13. A successful preflight is not a substitute for the full quality matrix, repository-state/documentation checks or source-fidelity review.


## 21. Unified fail-closed package consistency gate

Every Pull Request must pass one observable, fail-closed repository-consistency gate in addition to the supported Python and Windows quality matrix. The existing required status context `Repository state / project-state --check` now executes these checks in sequence on the same checked-out candidate commit:

1. `python tools/dkb.py package-preflight` — validate every repository data CSV/JSON file and the registered source-capture manifest integrity covered by the canonical preflight;
2. `python tools/dkb.py project-state --check` — compare live repository counts and canonical state, validate state references, and verify the generated state summary;
3. `python tools/dkb.py documentation-baseline --check` — verify all managed documentation baseline blocks against live repository data.

The separately required `Generated documentation / documentation-baseline --check` status remains in place as an independent, clearly named check. The additional invocation inside the repository-state job ensures that the repository-state required context cannot pass when any of the three package-consistency layers fails.

The gate is read-only. It must never silently repair a candidate branch in CI. If a check fails, the maintainer diagnoses the first causal discrepancy, applies the canonical generator locally or through an explicitly validated candidate workflow, inspects the complete resulting diff, and reruns all three checks on the same resulting tree. Manual counter copying, hand-edited generated blocks and weakened validators are prohibited.

The gate complements rather than replaces:
- the full Python and Windows quality matrix;
- importer-specific focused tests and idempotency checks;
- independent source-to-master fidelity review;
- the complete PR diff, exact-head, freshness, conflict and technical-review requirements.

For each package, the PR validation record must state the result of all three subchecks separately. A single green umbrella status does not justify describing an unobserved subcheck or source-fidelity review as passed.

The gate is intentionally wired into an existing required status context. It does not add or rename branch-protection contexts and therefore preserves the repository's six-check single-maintainer merge policy.

## 7.5 Canonical package lifecycle invariants

The existing `project-state --check` gate validates the canonical package
selector in `project/state.json`. Both `current_package` and
`next_package` must contain non-empty stable `package_id` and `kind`
fields, in addition to their name, status and goal. The IDs must be different,
and `next_package.status` must not be `complete`.

These invariants apply to every candidate tree. They do not require every
maintenance PR to claim that it completed the current domain package. A
documentation, tooling, CI or governance PR that does not complete/redefine
the selected package may leave the package selector unchanged. When a package
implementation changes the selected package, update `state.json` and its
generated `STATE_SUMMARY.md` within that logical package PR.

Do not add a global PR-number-to-current-package equality check. If a future
workflow needs explicit package ownership binding, it must be opt-in and
activated only for PRs declaring a package manifest/identity. See D-029.


## 22. Analytical report provenance and freshness

Every new or materially refreshed analytical report under `data/reporting/` must follow `project/REPORT_FRESHNESS_STANDARD.md`. Its JSON record must bind the analysis to the exact repository commit and exact input-file identities; its Markdown companion must expose the same report identity, date, commit, status and scope. Missing provenance is a blocker, not an invitation to infer a hash or timestamp.

When a canonical input, source identity or relevant decision changes, dependent reports must be identified and marked for review. Recheck all open and unresolved findings against current canonical data and exact source evidence before carrying them forward. Never copy an old limitation into a new report without revalidation. Preserve old reports as historical records; publish a versioned successor rather than silently rewriting history.

A report may be described as current only after its repository identity, input paths and hashes, scope, finding states and JSON/Markdown parity have been verified. A matching input hash alone does not prove that source interpretation or scope remains valid. Existing reports without the metadata contract are legacy and must not be represented as current until reviewed and migrated.

The report freshness validator is part of the required Quality gate. Its contract must cover positive, negative, legacy-compatibility, tampering and dependency-closure cases. Do not weaken the existing package-preflight or repository-state checks to accommodate legacy reports.


### 22.1 Automated report freshness gate

The required Quality workflow runs `python tools/dkb.py report-freshness` immediately after package preflight. The registry at `data/reporting/report_registry.json` is the explicit inventory of governed analytical reports. New entries are strict by default; legacy compatibility requires an explicit `legacy: true` marker and may never claim current status. Each strict report is checked for required provenance, safe repository-relative paths, exact Git blob SHA-1 and content SHA-256 of every input, stable finding IDs/states/evidence/date, and Markdown companion parity. Every registry entry must explicitly declare `depends_on` (registered report IDs) and `depends_on_paths` (unregistered report JSON inputs), using `[]` when a category has no dependencies. A direct input under `data/reporting/*.json` must be declared in exactly the corresponding field: registered reports use IDs, while unregistered report artifacts use safe repository-relative paths that must also appear in the report's fingerprinted `input_files`. Unknown IDs, unsafe/missing paths, undeclared report inputs, duplicates, self-references and dependency cycles fail closed. If a report or any transitive registered dependency is invalid or stale, every dependent report is also reported as stale. Contract tests cover valid reports, changed inputs, missing metadata, companion drift, legacy compatibility, missing dependencies, cycles and stale-dependency propagation. Do not add a report to the registry as legacy merely to bypass a failed check; investigate and correct its provenance or explicitly retain it as historical under the standard.

## 23. Canonical source metadata and importer preflight

The structured source identity in data/master/sources.csv is canonical. Import specifications may repeat source identity fields to make a package independently reviewable, but importers must compare structured identity fields and must not require byte-for-byte equality of the free-form notes field.

Use tools/source_registry_contract.py for source-registry identity comparisons. The helper checks source ID, code, type, title, publisher, market, document date, external reference, archive path, SHA-256 and status. It deliberately excludes notes, which is explanatory editorial provenance. A mismatch in any structured field remains a hard error. If a source row does not yet exist, the import may create it from the reviewed specification; once registered, the registry row remains authoritative.

Every importer/import-spec contract change must include positive regression tests for editorial wording changes, negative tests for changed SHA-256/archive path/date/market/other identity fields, validation of every applicable import specification, and exact source-file SHA-256 verification.

The normal Quality workflow runs the complete unit-test suite on Python 3.10 and 3.13 and the full quality gate on Python 3.14. A green result applies only to the exact commit SHA tested.

## 24. Stable, scope-based regression tests

Tests must assert facts owned by the package: exact source IDs, configuration scopes, observation keys, source-page breakdowns and expected values. Do not use a mutable whole-source or whole-repository row count as the only contract when later packages may append observations to the same source.

When a later package adds valid observations under an existing source, earlier tests must continue to verify their original bounded subset and separately verify the new package's observations. A total may be asserted only when its scope is explicit. Before changing an expected value after a failure, identify newly added or changed records and prove the difference is intended.

A failure caused by a stale global count must be fixed by narrowing the assertion to the package ownership boundary, not by deleting new data or blindly increasing a number.

### 24.1 Shared-source and cross-package regression protection

A canonical source may be extended by more than one bounded package over time. The source code identifies the document, not the package that owns every row imported from it. Tests and importers must therefore distinguish **source identity**, **package ownership**, **observation scope** and **expected records**.

Mandatory rules:

1. **Do not select legacy/package specs by filename prefix alone.** A broad glob or prefix such as `duster-page9-*` may capture later packages that use the same source page. Select the intended inventory using explicit package manifest membership and/or structured fields such as source code, observation date, attribute code and configuration set. If filenames are used as an additional selector, prove that the selector excludes future package specs by design.
2. **Do not assert that a source has no records when the intended rule is that a package adds no duplicates.** Replace whole-source absence assertions with an exact allowed-set contract: enumerate the expected records for the new package (source, date, attributes, configurations and values), assert that each exists exactly once, and reject unexpected records only within the clearly defined scope being tested.
3. **Preserve prior package contracts.** When a later package appends observations to an existing source, earlier tests must continue to validate their original records and original applicability, while a new focused test validates the appended records. Neither test should depend on the other's mutable total.
4. **Use structured observation keys.** Where available, compare a stable key composed of source ID/code, observation date, attribute, configuration, fuel/gearbox/applicability dimensions and validity scope. Do not use a bare source code as a unique fact key.
5. **Keep exact counts local.** An exact count is valid for a fixed package manifest, fixture or enumerated source/configuration subset. It is not valid as an unqualified count of all repository specs or all rows sharing a source code if later packages are allowed to extend them.
6. **Test coexistence, not only isolated success.** When adding a spec under a previously used source, run the new focused tests together with the existing source-family regression tests. The combined run must prove that old rows remain unchanged, new rows are present exactly once, and unrelated rows are untouched.
7. **Review all shared-source consumers before changing expectations.** Search tests, importers, reports and workflows for the affected source code, file prefix, attribute code and count assertion. Record the affected tests and their ownership boundary in the package validation notes.

### Required pre-commit shared-source regression checklist

For any package that adds or changes an import spec, master row, observation or report under a source code already used by another package:

- [ ] Enumerate all existing specs and master observations for that source before editing.
- [ ] Identify which tests assert totals, absence, or filename-prefix membership for that source.
- [ ] Verify each such test is scoped to its own package/source-date/configuration contract.
- [ ] Add or update an exact positive test for the new package records and an exact negative test for duplicates/unexpected scope.
- [ ] Run the new test and every affected pre-existing source-family test in the same command.
- [ ] Compare the candidate branch diff against its base and confirm prior records were not removed or rewritten.
- [ ] Run the full repository test discovery and required quality matrix after the final edit.

If a shared-source regression is found, do not merely add the new package's count to an old expected total. Correct the ownership boundary, retain the old package's invariant, and assert the new package's exact records independently. A broad assertion may remain only if the entire source inventory is intentionally frozen and versioned as a fixture.


### 24.2 Semantic assertions and editorial wording stability

Tests for reports, findings, documentation and other human-readable content must verify the intended invariant or meaning, not an incidental sentence chosen by an author. Editorial wording may be clarified or paraphrased without changing the underlying decision; a test that requires one exact phrase can therefore fail even when the report remains correct.

Mandatory rules:

1. **Prefer structured contracts.** Where available, assert stable identifiers, finding/status codes, scope, source references, applicability, explicit outcome fields and permitted/prohibited data changes. These are stronger contracts than a sentence in a free-form `detail` or `notes` field.
2. **Treat prose as explanatory unless declared otherwise.** Do not use exact whole-sentence or phrase matching for editorial descriptions, rationale, notes or report summaries merely to prove a domain decision. A wording change alone must not break a test when the structured meaning and required behavior remain unchanged.
3. **Use exact text assertions only for real text contracts.** Exact matching is appropriate for stable machine-facing values and intentionally fixed external contracts, such as identifiers, enum literals, schema keys, command names, protocol tokens, or user-visible text whose exact wording is itself a requirement. State that reason in the test.
4. **When prose is the only available evidence, test the semantic boundary.** Check stable finding identity and status, required source/evidence references, and the presence/absence of the consequential behavior or classification. If a textual check is still needed, normalize harmless case/whitespace differences and assert the smallest meaningful condition; do not pin the test to one complete sentence or a single editorial formulation.
5. **Do not make a failing test pass by deleting or weakening its invariant.** First inspect the source evidence and the full report/finding. Decide whether the implementation's meaning changed or only its wording. If the meaning changed, correct the report/data and its tests together. If only wording changed, update the brittle assertion to the stable semantic contract and retain positive and negative checks for the intended behavior.
6. **Review the resulting test, not just the replacement line.** Confirm that the revised assertion would still fail for the prohibited or incorrect outcome. Include a regression case for the negative boundary where practical.

For example, a report finding that defers an unsupported classification should be tested through its stable `finding_id`, `needs_review` status, source scope and unchanged/no-migration outcome. A test should not require one exact editorial phrase such as “Do not convert” if the report expresses the same prohibition as “do not migrate”. Conversely, if an exact phrase is part of a published interface or legal/contractual wording, exact matching remains appropriate.

This rule applies to tests of JSON/Markdown reports, source-review findings, generated documentation and explanatory metadata. It supplements sections 5, 7.1 and 8; it does not permit a weaker evidence standard or a test that accepts an incorrect domain outcome.

## 25. Remote-main authority, package closure and post-merge state transaction

This section is mandatory for every session and package, including documentation-only work. It prevents local-checkout drift, stale package queues and false completion after a successful merge.

### A. Verify the remote before using any local state

1. Resolve the repository's actual default branch and fetch its current commit SHA from GitHub.
2. Record the exact remote main SHA used for the session and the exact SHA of every PR head under review.
3. Treat files read from GitHub's current default branch as authoritative. A local checkout, stash, generated output, previous tool result or conversation summary is only a snapshot until its commit SHA is proven to match the intended remote revision.
4. Never use project-state --apply on an unverified or stale local checkout and then describe its output as the current GitHub state. The command changes only the working tree; it does not update GitHub.
5. If local execution is used, first prove the local branch, HEAD SHA, upstream and working-tree status. If local HEAD differs from remote main, either synchronize safely or explicitly label all local results as belonging to that older candidate. Do not mix results from different trees.
6. If the current session has GitHub read/write but no local execution, use GitHub as the repository surface and rely only on observable CI for executable validation. State the exact capability boundary; do not imply that a missing manual workflow-dispatch operation means GitHub Actions or automatic PR CI is unavailable.

### B. Close every package as one canonical state transaction

A package is not durably complete merely because its PR is merged. After each merge:

1. Re-fetch the PR and verify merged=true, the merge commit SHA, the final PR head SHA and the changed-file list.
2. Re-fetch the default branch and verify that it contains the merge commit.
3. Reconcile the merged package against project/state.json. Update current_package to the completed package with its exact PR/merge reference where the schema supports it; select the next package from the merged result and current repository evidence, not from an old handoff or PR description alone.
4. Update project/state.json through the canonical project workflow. Then run project-state --check and documentation-baseline --check on the same candidate tree. The generated project/STATE_SUMMARY.md must be produced by python tools/dkb.py project-state --apply; never hand-edit or independently reconstruct it.
5. Verify the full generated diff. Confirm that counters are derived from the candidate repository, not copied from a previous run or conversation.
6. Include the canonical state, generated summary and any managed documentation changes in the same logical state-reconciliation PR when they belong to one closure transaction. Do not leave a merged package permanently represented as the next planned package.
7. If the canonical generator cannot be executed and no CI workflow can apply it to a candidate branch, do not fabricate generated files or claim the state transaction is complete. Record the exact blocker and continue only with work that does not depend on the unresolved state.

### C. Candidate and merge SHA discipline

- Every validation result must be associated with an exact commit SHA.
- A green check on an earlier head does not validate a later head, even if the later change is documentation-only.
- Before merge, re-fetch the PR and compare current head SHA, base SHA, mergeability, changed paths and all required checks.
- After merge, verify the actual merge commit on remote main; do not infer successful publication from a create/update response alone.
- If main advances while a candidate is being prepared, reconcile the branch with the new base and rerun every invalidated gate.

### D. Report state and capability truthfully

Every continuation report must distinguish:
- remote main SHA and local HEAD SHA (if local execution was used);
- canonical package state before and after the work;
- PR head SHA, merge commit and current merge status;
- observed CI checks on the exact head;
- checks not run, unavailable or blocked, with the reason;
- whether state and generated documentation were actually committed and verified.

Do not use phrases such as state synchronized, package closed or CI unavailable unless the corresponding remote evidence supports that exact claim.



### 24.3 Portfolio-wide and cross-model regression protection

Adding a model, version, configuration, source or reporting scope is a portfolio change. It may legitimately change aggregate outputs, but it must not silently rewrite the contracts of earlier packages.

Mandatory rules:

1. **No unexplained live portfolio literals.** Tests must not pin mutable repository-wide totals (model count, configuration count, version count, scope count, card count, pair count or generated-row count) to a bare integer. A fixed value is permitted only when it belongs to a named immutable fixture, a versioned release baseline, or an explicitly frozen contract. The test must identify that owner and scope in its name or comments.
2. **Use two complementary contracts.** For a portfolio-wide view, derive the current expected inventory from canonical registries and assert internal consistency (every eligible entity appears once, no ineligible entity appears, references resolve, and aggregates reconcile). Separately use a small immutable fixture to assert stable ordering, rendering and representative values. Do not use a current whole-repository count as a substitute for either contract.
3. **Preserve package-level history.** Historical package tests must use package-owned manifests or frozen fixtures. They must not silently inherit new models or rows from the current live registry. Conversely, current portfolio tests must include all active models and configurations discovered from canonical registries.
4. **Model onboarding contract.** Every new model package must test the full propagation path: model registry -> model/version/configuration registries -> source mappings -> comparison/reporting scopes -> HTML/JSON/workbook/export outputs. The test must assert the new model is present exactly once in each applicable output and absent only where an explicit applicability rule excludes it.
5. **Aggregate reconciliation.** For each generated view, assert that summary counts equal the number of emitted records/cards/groups and that pair/scope totals reconcile with their underlying memberships. Prefer deriving both sides independently from canonical data rather than copying the same literal into the test and generator.
6. **No blind expected-value refresh.** When a test fails after a portfolio change, inspect the diff from the target branch and classify each changed record as added, removed, modified or unchanged. Update a fixed expectation only after proving its ownership and intended change. Never mass-replace old counts with new counts.
7. **Historical snapshots are immutable.** Release-preparation and historical baseline tests must read a named, versioned snapshot. Updating the current registry must not regenerate or mutate historical fixture data to make old tests pass.

8. **Historical scope dates fail closed.** An as-of report excludes a scope whose explicit `effective_from` is later than the cutoff. If `effective_from` is absent but any configuration in that scope is linked to a source whose `document_date` is later than the cutoff, generation must fail with the scope and source codes; it must never silently include that future evidence. New source scopes must record `effective_from` whenever their effective period is known.

### 24.4 Report dependency and freshness closure

A data or registry change must trigger a bounded dependency review before publication.

1. Each analytical report must declare its actual input paths and scope. Prefer narrow, explicit dependencies over hashing a broad registry file when the report only consumes a subset. If a broad file is genuinely consumed, any change to it must mark the report needs_review until re-evaluated.
2. The package change-impact inventory must enumerate affected reports, tests, generated outputs and release artifacts. The inventory must distinguish directly changed inputs from transitive consumers.
3. A report marked needs_review remains visibly stale. It must not be silently returned to current, have its original fingerprints rewritten, or be excluded from a check merely to obtain a green build.
4. A refreshed report must be regenerated from its canonical structured input where a generator exists; JSON/Markdown parity, input fingerprints, scope and findings must be checked together.
5. The pre-PR gate must fail with a list of unresolved affected reports and consumers. It must not merely report a generic stale-baseline error.

### 24.5 Test-tooling isolation and failure classification

Tests of package/release tools must be hermetic and must not depend on a developer's or runner's real GitHub remote, credentials, current branch or ambient working tree.

1. Run package lifecycle tests in a fresh temporary repository and staging directory. Create a local bare Git remote when push behavior must be tested; never push to the real project remote from a unit test.
2. Assert staging-directory emptiness and exact path manifests before and after each lifecycle step. Clean up in finally/fixture teardown, and prove that an injected unexpected file is rejected without contaminating later tests.
3. Stub or inject external commands at the process boundary. A test that expects a failure must assert the exact error category and cleanup result, not only a non-zero exit code.
4. Keep negative-path tests isolated from the success-path fixture. An intentional extra file, version mismatch or simulated push failure must not leak into another test's workspace.
5. CI summaries must separate product-code failures, stale generated artifacts/reports, test-fixture defects, external-service failures and environment/toolchain failures. A green platform packaging job does not cancel a failing package-tool unit test.
6. Before changing package tooling, run its focused tests in isolation, then the full quality suite on the exact candidate tree. Re-run all required checks after every new commit.

### 24.6 Required change-impact matrix for model and portfolio changes

For any change that adds or materially changes a model, version, configuration or source registry entry, the package validation record must contain a matrix with at least these rows:

| Area | Required evidence |
|---|---|
| Canonical registries | Exact added/changed IDs and referential integrity |
| Configuration inventory | Active/inactive classification and source-backed applicability |
| Portfolio summaries | Derived counts reconcile with emitted model/configuration records |
| Comparison scopes | New model included only in supported comparable scopes; pair totals reconcile |
| Reports | Direct and transitive consumers reviewed; stale reports re-evaluated or explicitly needs_review |
| Exports and release assets | Model/version/configuration coverage and deterministic output checks |
| Historical tests | Prior package fixtures remain unchanged and pass |
| Tooling | Isolated package/release lifecycle tests pass without real remote access |
| CI | All required checks pass on the exact final head SHA |

Use the copy-ready template at project/packages/CHANGE_IMPACT_MATRIX_TEMPLATE.md. The matrix is not complete when it merely lists commands. It must record the observed result, exact command or artifact, and any unresolved item. Use the explicit evidence syntax `command: <exact command>` or `artifact: <repository-relative file path>`; artifact paths must exist in the candidate repository tree. The validator checks artifact existence and rejects paths outside the repository. Command entries record the exact command used; the row must still state the observed outcome in its result and notes. The Quality workflow also compares all ten Test-contract review checklist entries against the exact template wording, order and checked state; ten arbitrary checked boxes do not satisfy the contract. The Quality workflow enforces the matrix whenever a PR changes files under `data/master/`, `data/source_intake/`, `PDF/`, or a reporting completeness scope under `data/reporting/`. The matrix must be added or updated in that same PR, every required row must have a result of `PASS` or justified `N/A`, and every row must cite its evidence. A `FAIL`, missing row, missing evidence, incorrect checklist, or missing matrix blocks the PR. The final tested head SHA must be recorded in the PR description or review record after the last commit; do not attempt to embed a commit's own SHA inside that commit's file. An unresolved required row blocks PR readiness and merge.
