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

## End of protocol
