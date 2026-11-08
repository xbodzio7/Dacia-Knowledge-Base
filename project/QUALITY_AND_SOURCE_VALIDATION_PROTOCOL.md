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
8. Run all remaining package-specific deterministic checks and independent source-fidelity review.
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

These workflow definitions provide automatic PR feedback, but a workflow job is not necessarily a merge-blocking required check. Repository administrators must configure the two job checks (and the other required quality jobs) in branch protection/rulesets where permissions allow. Until that repository setting is inspected and verified, do not claim that GitHub technically blocks merges on these checks.

Documentation alone does not enforce branch protection. Report separately whether (a) the workflow exists and ran, and (b) the corresponding check is configured as a required status check.

### F. No local execution capability

If the active profile cannot execute the canonical generators or tests, do not fabricate their output, manually guess generated counters, or publish the candidate as validated. Use a verified CI workflow capable of running the checks on the candidate branch. If no such workflow is available, leave the PR blocked/unpublished and record the exact capability blocker.

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

At the start of a merge decision, inspect the current branch protection/ruleset state. If the target branch does not require the designated baseline and quality checks, record that as a governance risk; do not describe CI as merge-blocking. Request an authorized repository administrator to configure required status checks for the repository's actual workflow/job names. Do not attempt to bypass or silently weaken repository policy.

Until required checks are enforced by GitHub, the maintainer must apply a procedural no-merge rule: do not merge unless the current exact PR head has passed the full required quality matrix and both technical-integrity and source-fidelity gates. If the maintainer lacks permission to configure branch protection, continue safe work and report the exact administrative action needed.

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
