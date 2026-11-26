# Change-impact matrix — Official Bigster Brochure Full Assimilation

## Package identity

- Package: official_bigster_brochure_full_assimilation_20261014_001
- PR: #904
- Base SHA: ddcbdfaeb8d3c6e913ac07a8143dfcfe1888d414
- Candidate head SHA: pending final package commit and CI
- Change owner: DKB autonomous maintainer
- Source/evidence IDs: src_pl_bigster_brochure_20251210; src_pl_bigster_price_my26_20261001

## Change inventory

| Entity type | Exact IDs | Added | Changed | Removed | Evidence / reason |
|---|---|---:|---:|---:|---|
| Models | Bigster | 0 | 0 | 0 | Existing model identity reused |
| Versions | Existing 14 source-linked configurations | 0 | 0 | 0 | No grade/version identity changes |
| Configurations | Existing 14 source-linked configurations | 0 | 0 | 0 | No new configuration or crosswalk inferred |
| Sources | src_pl_bigster_brochure_20251210 | 0 | 1 | 0 | Assimilation coverage and report reference added to existing source row |
| Source mappings | Six Bigster colour items | 6 | 0 | 0 | Six commercial items and six exterior_color attributes; no grade mapping |
| Reporting scopes | Bigster brochure 24-page inventory | 1 | 1 | 0 | Full page inventory and explicit deferral ledger |

## Change-impact matrix

| Area | Required evidence | Result (PASS / FAIL / N/A) | Evidence (command: ... / artifact: ...) | Notes / unresolved items |
|---|---|---|---|---|
| Canonical registries | Exact IDs and referential integrity | PASS | artifact: data/master/commercial_items.csv | Observed: six new Bigster colour item IDs are present once each; six matching exterior_color attributes are registered; the existing Bigster brochure source identity is retained. |
| Configuration inventory | Active/inactive classification and source-backed applicability | N/A | artifact: data/reporting/official_bigster_brochure_full_assimilation_20261125.json | No configuration, version or grade applicability mapping was added because the brochure does not establish exact colour-to-grade applicability. |
| Portfolio summaries | Derived counts reconcile with emitted records | PASS | artifact: data/reporting/official_bigster_brochure_full_assimilation_20261125.json | Observed: all 24 brochure pages are inventoried; the report reconciles 14 configurations, 458 scalar observations, 557 availability observations, 34 ranges, 68 cargo-context values, 56 grade-detail values and 126 exterior-dimension observations. |
| Comparison scopes | Supported inclusion and reconciled pair/scope totals | N/A | artifact: data/reporting/bigster_documentary_technical_reconciliation_001.json | No comparison scope or price-history observation is added; ten payload values matching the later cennik are not duplicated and four dated 2025 conflicts remain preserved. |
| Reports | Direct/transitive consumers reviewed; findings re-evaluated | PASS | artifact: reports/price_history/sandero_stepway_catalogue_price_history_2026.json | Observed: the shared sources.csv change was detected as a report dependency; the Sandero report and Markdown companion are updated together and explicitly set to needs_review, retaining original fingerprints. |
| Exports and release assets | Model/version/configuration coverage and deterministic outputs | N/A | artifact: project/packages/official-bigster-brochure-full-assimilation-2026-11-25.md | No data-product export, release asset or downloadable product package is changed by this assimilation. |
| Historical tests | Package-owned fixtures unchanged and passing | N/A | artifact: tests/test_bigster_brochure_full_assimilation_20261125.py | No historical fixtures are modified; the new package contract test is isolated to the Bigster source, six colour records, payload reconciliation and canonical counters. |
| Tooling | Isolated package/release tests; no real remote access | N/A | artifact: project/packages/official-bigster-brochure-full-assimilation-2026-11-25.md | No tooling implementation or release workflow is changed by this data package; repository tooling is exercised by the required CI suite. |
| Generated documentation | Canonical generators and baseline checks pass | PASS | artifact: README.md | Observed: generated baseline blocks now state 2055 tests and 23490 master rows; the canonical state summary is aligned with the package candidate. |
| CI | Required checks pass on exact final head SHA | N/A | command: python tools/dkb.py project-state --check | CI status is intentionally not pre-asserted in a static matrix; all six required checks must pass on the exact final PR head under branch protection. |

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

| Failure | Category (product / stale report / brittle test / fixture leak / environment / external service) | Evidence inspected | Corrective action | Re-run result |
|---|---|---|---|---|
| Sandero/Stepway price-history input fingerprint changed after the shared source registry row was updated | stale report | command: python tools/dkb.py report-freshness | Preserve original fingerprints; update JSON/Markdown pair together and set status to needs_review until re-evaluated | Pending exact-head CI |
| Required change-impact matrix absent from the first candidate | brittle test | command: python tools/change_impact_matrix.py --base-ref origin/main --head-ref HEAD | Add this package-scoped matrix with all required areas and exact template checklist | Pending exact-head CI |

## Closure

- Final tested head SHA: pending exact-head CI; record in PR description after all checks complete.
- Required checks: Python 3.10; Python 3.13; Python 3.14; Package workflow / Windows; Generated documentation / documentation-baseline --check; Repository state / project-state --check.
- Unresolved findings: Sandero/Stepway catalogue-price history remains needs_review pending report regeneration; Bigster source deferrals remain explicitly recorded in the package ledger.
- Merge decision and evidence: merge only after all six required checks pass on the exact final head SHA and mergeability is confirmed.
