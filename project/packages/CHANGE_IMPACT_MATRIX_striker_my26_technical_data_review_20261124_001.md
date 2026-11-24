# Change-impact matrix — Striker MY26 technical data and dimensions

## Package identity

- Package: `striker_my26_technical_data_review_20261124_001`
- PR: #898
- Base SHA: `db0aa2b006faa8fb7abe7a64bdc915fd6ea96107`
- Validated data/code head SHA: `c01969f814e3670c41d3f86ce06b672ff810a953`; this closure update changes only the matrix document
- Source: `src_pl_striker_price_my26_20261102`; archived `PDF/Cenniki/striker-price.pdf`
- Source SHA-256: `d9e1e874ceaf2b65faf37650ad7be4b9a7c9710ee1d09cbdee5856c286e62d35`
- Scope: 11 exact source-linked configurations; pages 6–7

## Change inventory

| Entity type | Exact IDs | Added | Changed | Removed | Evidence / reason |
|---|---|---:|---:|---:|---|
| Scalar configuration observations | 42 source-backed attributes | 423 | 0 | 0 | 42 declarative specifications; existing attributes reused |
| Bounded configuration ranges | CO2, combined consumption, maximum-power RPM | 21 | 0 | 0 | 3 range specifications; printed intervals remain ranges |
| Configurations / versions / sources | Existing 11 Striker configurations and registered cennik | 0 | 0 | 0 | Exact source links reused |
| Commercial items / packages / availability | Existing page-5 commercial matrix | 0 | 0 | 0 | No commercial or availability records changed |
| Reports / completeness scopes | `striker_my26_technical_data_review_20261124_001` | 1 | 0 | 0 | Report, metadata, findings and 11-configuration scope added |

## Change-impact matrix

| Area | Required evidence | Result (PASS / FAIL / N/A) | Evidence (command: ... / artifact: ...) | Notes / unresolved items |
|---|---|---|---|---|
| Canonical registries | Source and configuration references remain exact | PASS | artifact: data/master/source_configurations.csv | Observed: the source is linked to exactly the 11 existing Striker configurations; no model, version, configuration or source registry rows were changed |
| Configuration inventory | Configuration scope and applicability are explicit | PASS | artifact: data/reporting/striker_my26_technical_completeness_20261124.json | Observed: the technical scope contains exactly 11 source-linked configuration codes and no new configuration identities |
| Portfolio summaries | Derived totals and scopes reconcile | N/A | artifact: data/reporting/striker_my26_technical_completeness_20261124.json | No portfolio-wide summary or cross-model aggregate is changed; only the Striker package-specific technical scope is recorded |
| Comparison scopes | Comparison inputs and pairings remain valid | N/A | artifact: project/state.json | No comparison scope, pairing registry or comparison output is changed |
| Reports | Provenance, findings and direct dependencies are registered | PASS | artifact: data/reporting/striker_my26_technical_data_review_20261124_001.json | Observed: the report has matching JSON/Markdown metadata, a registered PDF Git blob SHA and SHA-256, timezone-aware generation/finding timestamps, six explicit findings, a page-6 text-audit artifact reference and declared report dependencies |
| Exports and release assets | Export schemas and release artifacts remain compatible | N/A | artifact: project/state.json | No export schema, release asset or published data product is changed |
| Historical tests | Historical fixtures and frozen baselines remain isolated | N/A | artifact: tests/test_striker_my26_technical_data_review_20261124.py | No historical snapshot or release-baseline fixture is modified; 12 new regression tests are scoped to this source and its 11 configurations |
| Tooling | Importer and package tooling contracts are preserved | N/A | artifact: tools/import_configuration_values.py | No importer implementation or shared tooling is changed; existing declarative importers are reused |
| Generated documentation | Canonical state and managed documentation are synchronized | PASS | command: python tools/dkb.py project-state --check | Observed: Repository Baselines run 45508316155 passed both project-state and documentation-baseline checks on data/code head `c01969f814e3670c41d3f86ce06b672ff810a953`; this closure update changes only the matrix document and final-head CI will rerun the checks |
| CI | Workflow definitions and exact-head required checks are reviewed | N/A | command: python tools/change_impact_matrix.py --base-ref origin/main --head-ref HEAD | No workflow definition is changed by this package; exact-head Quality and Repository Baselines checks remain mandatory merge gates and closure stays open until they pass |

## Test-contract review

- [x] Mutable portfolio-wide counts are derived from canonical registries, not copied into tests as unexplained literals.
- [x] Exact counts are limited to immutable fixtures or explicitly frozen, versioned contracts.
- [x] Existing package tests remain bounded to their own manifests and source/configuration scopes.
- [x] New package records are asserted exactly once, with explicit negative checks for duplicates/out-of-scope records.
- [x] Aggregate counts are reconciled independently against emitted records.
- [x] Historical snapshots and release baselines were not regenerated from current live data.
- [x] Changed report dependencies are reviewed; stale reports remain needs_review until re-evaluated.
- [x] Package lifecycle tests use fresh temporary repositories/staging areas and a local bare remote if push behavior is tested.
- [x] Negative-path fixtures cannot contaminate success-path tests.
- [x] The final diff was reviewed against the exact base SHA.

## Failure classification

| Initial failure | Category | Evidence inspected | Corrective action | Re-run result |
|---|---|---|---|---|
| New report lacked required report_metadata | stale report / provenance contract | Quality run 45507091941, jobs 138844983534 and 138844983870 | Add report ID, timestamp, repository, base SHA, PDF Git/SHA-256 fingerprints, scope, status and finding provenance; align Markdown parity and dependencies | Passed on data/code head `c01969f814e3670c41d3f86ce06b672ff810a953`; final-head checks rerun after this matrix-only update |
| New regression test attempted PDF text extraction without the pinned backend in the general Quality runner | test-environment / source-extraction contract | Quality run 45507548488, Python 3.10 job 138846548229 and Python 3.13 job 138846548278 | Verify PDF binary identity in the general test suite and reference the independently successful pinned source-audit artifact for page-6 extracted text | Pending exact-head rerun |
| Change-impact matrix omitted mandatory sections and area rows | tooling / CI contract | Quality run 45507091941, Python 3.14 job 138844983842 | Replace package matrix with the enforced template, all ten areas and exact checked test-contract items | Passed on data/code head `c01969f814e3670c41d3f86ce06b672ff810a953` |

## Closure

- Validated data/code head SHA: `c01969f814e3670c41d3f86ce06b672ff810a953`.
- Quality run #45508315790: all four jobs passed, including 2054 tests on Python 3.10 and 3.13, the full Python 3.14 quality gate and the Windows package workflow.
- Repository Baselines run #45508316155: project-state and documentation-baseline checks both passed.
- All 17 source-triggered reporting, comparison, export and release workflows passed.
- This closure commit changes only this matrix document; exact-head Quality and Repository Baselines checks must pass again before merge.
- Unresolved source findings: hybrid 155 CO2 `95/96`, minimum running-order mass semantics, maximum folded-seat luggage-volume basis, trim-level tyre fitment, 1000 m standing-start time and unexplained interior dimensions remain explicitly recorded.
- Merge decision: do not merge until the complete exact-head CI matrix is green and no blocking review threads remain.
