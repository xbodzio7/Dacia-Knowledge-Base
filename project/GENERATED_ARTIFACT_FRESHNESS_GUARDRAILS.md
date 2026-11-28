# Generated Artifact Freshness and Regeneration Guardrails

**Status:** Mandatory policy for generated repository artifacts  
**Applies to:** Reports, evidence bundles, comparison outputs, completeness analyses, resolution plans, exports and generated documentation.

## 1. Failure classes this policy prevents

A successful master-data import can make previously correct derived artifacts stale. Typical symptoms include:

- a report still classifies newly imported values as missing;
- a resolution plan still proposes work that is already complete;
- a dependent comparison or completeness report retains an old denominator;
- a historical report is accidentally rewritten as though it described current state;
- a generator updates canonical package state or package metadata as an unintended side effect;
- tests compare a local package against mutable global catalogue totals.

These are dependency and scope failures, not automatically data defects. Never fix them by changing expected numbers until the artifact's scope and inputs are understood.

## 2. Classify every artifact before changing it

Every affected artifact must be assigned exactly one lifecycle class:

1. **Live derived artifact** — intended to describe current repository data. It must be reproducible and freshness-checkable.
2. **Historical snapshot** — intentionally preserves what was known at a stated date/commit. It must not be silently regenerated from current data.
3. **Reviewed decision/evidence record** — records a human/source interpretation or an explicit unresolved conflict. It must not be overwritten by a generic generator.
4. **Source/master data** — authoritative source-backed input. A report refresh must never modify it.

When a failure involves an artifact, first establish its class, declared scope, source date, generator, and owning package. If this cannot be established, stop and preserve the artifact.

## 3. Dependency and provenance contract

For every live derived artifact, the owning package must declare or document:

- stable artifact/report ID and repository path;
- generator module/command and relevant generator version;
- exact input paths and the semantic scope of each input;
- source IDs, source revisions/effective dates and configuration/model scope where relevant;
- whether the artifact is current-state or date-bounded/historical;
- upstream artifacts it consumes;
- expected downstream artifacts that become stale when an input changes.

Where practical, record SHA-256 fingerprints of file inputs and a deterministic semantic fingerprint for scoped data inputs. A timestamp alone is not proof of freshness. Do not fingerprint the entire repository when only a defined subset is relevant.

The dependency graph must be explicit enough to answer: **which outputs need review or regeneration when this exact input changes?** Do not regenerate unrelated models or historical snapshots.

## 4. Generator safety contract

Every generator that can write repository files must provide a read-only check/diff mode and an explicit write mode.

- --check must not write, delete, rename or update any file.
- A reports-only mode must write only its named report outputs and must return before touching project/state.json, package manifests, package completion receipts or next-package selection.
- Default state-changing behavior must remain explicit and documented; never silently change the meaning of an existing command.
- Before write mode, resolve and print the exact output allowlist. Reject paths outside it.
- Write atomically; preserve files outside the allowlist byte-for-byte.
- A no-op regeneration is valid and must be tested.
- A failed generator must not leave partial output or a partially advanced project state.
- Generators must not consume untrusted PR artifacts in a job with write credentials.

Use the existing **Baseline Repair** workflow for the six canonical counter/documentation files. It is intentionally limited to those outputs; it is not permission to refresh arbitrary reports.

## 5. Required repair sequence after a data or code change

1. Identify changed source/master/specification/script paths on the exact PR head.
2. Resolve their declared downstream dependency set.
3. Classify each affected output using Section 2.
4. Run each relevant generator in read-only/check mode first; capture the stale-output diagnosis.
5. Regenerate only live derived artifacts with their canonical generator and explicit output allowlist.
6. Review the diff for scope, provenance, denominators, configuration IDs, dates and unresolved evidence. Confirm historical snapshots and reviewed decisions were not changed.
7. Run focused tests for each changed artifact and its downstream consumers.
8. Run the full required Quality matrix and all six repository protection checks on the final exact PR head SHA.
9. Record the regenerated artifact IDs/paths, unchanged historical artifacts, tests and exact head SHA in the package report and continuity checkpoint.

Do not hand-edit generated JSON/Markdown to make a check pass. If a generator is missing or unsafe, first add a bounded generator mode and regression tests; do not bypass the freshness check.

## 6. Test and denominator safeguards

Tests should assert scoped invariants, not mutable global totals.

- Scope count assertions to an exact fixture, source ID/revision, report ID, configuration set or historical snapshot.
- If a historical test intentionally excludes later records, encode the cutoff in the fixture/query and explain why.
- A current-state report must derive its denominator from its declared current scope; do not copy a previous run's global row count into a local test.
- Test both positive and negative boundaries: newly present facts leave the missing set; unresolved/ambiguous facts remain unresolved; unrelated models and historical snapshots remain unchanged.
- Test idempotency, deterministic output, reports-only state preservation, no-op regeneration and rejection of unexpected output paths.
- Do not weaken assertions or replace exact values with broad ranges merely to accommodate data growth.

The canonical test count is discovered from the current test suite by the documentation baseline generator. Never update the count manually. Use the existing Baseline Repair workflow from trusted main when remote-only regeneration is required, then verify its six-file diff and all six normal checks on the new exact head.

## 7. PR acceptance checklist

A PR changing source/master data, import specifications, report generators or generated reports is not ready until its description or package evidence answers:

- [ ] Which inputs changed, and what is the exact source/configuration scope?
- [ ] Which generated outputs depend on those inputs?
- [ ] Which outputs are live, historical, reviewed decisions or source/master data?
- [ ] Were only stale live outputs regenerated by canonical generators?
- [ ] Were state/package metadata and historical snapshots preserved unless explicitly in scope?
- [ ] Are report IDs, source provenance, dates and denominators correct?
- [ ] Do tests cover the changed scope and protect unrelated scopes?
- [ ] Did read-only checks and focused tests pass?
- [ ] Did all six required checks pass on the final exact PR head SHA?

A blank or unknown dependency answer is a blocker, not an implicit approval.

## 8. Automation boundary and rollout

The repository already has a machine-readable analytical report registry at data/reporting/report_registry.json and CI enforcement in the Quality workflow:

- tools/report_impact.py identifies direct and transitive analytical reports affected by changed inputs.
- tools/report_freshness.py validates registered report provenance, input fingerprints, dependency declarations, JSON/Markdown companion parity and freshness propagation.
- tests/test_report_freshness.py covers changed inputs, direct/transitive consumers, dependency declarations, stale-input handling and scope boundaries.
- .github/workflows/quality.yml runs report-impact for pull requests and report-freshness as part of the Quality gate.

These controls are real automation for the reports declared in the registry. Do not describe them as covering every generated artifact in the repository: unregistered reports, one-off exports and other generator outputs may remain outside this contract.

The next protection work is coverage expansion and gap closure, not duplicating the existing checker:

1. Inventory report-producing generators and compare their outputs with report_registry.json; explicitly classify historical snapshots and reviewed decisions.
2. Add missing live analytical reports to the registry with exact direct input paths, upstream report IDs, fingerprints and status.
3. Add regression cases for each newly covered report family, including input changes, transitive invalidation, historical immutability and unrelated-scope isolation.
4. Confirm report-impact and report-freshness fail closed for missing or inconsistent declarations, and remain read-only.
5. Keep these checks in Quality; do not make a separate weaker freshness workflow or silently regenerate reports in CI.
6. Extend coverage incrementally. Unknown dependencies must be visible and block only affected closeout, not trigger broad automatic rewrites.

Never change branch protection or reduce the existing six required checks as part of this rollout.
