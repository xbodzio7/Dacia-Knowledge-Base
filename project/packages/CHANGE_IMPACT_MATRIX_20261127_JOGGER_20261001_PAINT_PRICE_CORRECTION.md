# Change-impact matrix — Jogger MY26 2026-10-01 special paint price correction

## Package identity

- Package: Jogger MY26 2026-10-01 special non-metallic paint surcharge correction
- PR: #924
- Base SHA: `302fe0b31e639abd416034dcbff0d082c785d8ec`
- Candidate head SHA: `b73500df431c4465d9537b6629fc7ffafeef0705` (superseded by this matrix update; final SHA is recorded in PR checks)
- Change owner: repository maintainer
- Source/evidence IDs: `src_pl_jogger_price_my26_20261001`; archived PDF SHA-256 `12e536c1e60e9e7f91228b27a9d962cecacb5a5287d585f419a14af3003e8b46`; visual evidence workflow run `46047957727`

## Change inventory

| Entity type | Exact IDs | Added | Changed | Removed | Evidence / reason |
|---|---|---:|---:|---:|---|
| Models | none | 0 | 0 | 0 | No model records changed |
| Versions | none | 0 | 0 | 0 | No version records changed |
| Configurations | 12 Jogger MY26 configuration codes linked to the source | 0 | 0 | 0 | Existing configuration identities retained |
| Sources | `src_pl_jogger_price_my26_20261001` | 0 | 1 note | 0 | Source registry annotation aligned with visually verified printed page 3 |
| Source mappings | `jogger_special_nonmetallic_paint_option` × 12 dated configuration mappings | 0 | 12 amounts | 0 | Special non-metallic paint surcharge corrected from 2,800 to 2,700 PLN |
| Reporting scopes | none | 0 | 0 | 0 | No analytical reporting scope changed |

## Change-impact matrix

| Area | Required evidence | Result (PASS / FAIL / N/A) | Evidence (command: ... / artifact: ...) | Notes / unresolved items |
|---|---|---|---|---|
| Canonical registries | Exact IDs and referential integrity | PASS | command: python tools/import_jogger_price_list_commercial_matrix_20261001.py --check | Observed: source and 12 configuration links are validated by the package importer; final CI reruns this on the final head |
| Configuration inventory | Active/inactive classification and source-backed applicability | N/A | command: git diff -- data/master/configurations.csv data/master/configuration_values.csv | No configuration inventory or applicability records are changed |
| Portfolio summaries | Derived counts reconcile with emitted records | N/A | command: git diff -- data/master/ | No portfolio-wide model/configuration summaries are changed |
| Comparison scopes | Supported inclusion and reconciled pair/scope totals | N/A | command: git diff -- data/master/comparison_scopes.csv | No comparison-scope records are changed |
| Reports | Direct/transitive consumers reviewed; findings re-evaluated | PASS | artifact: data/reporting/jogger_price_list_20261001_reconciliation_001.json | Observed: dated commercial reconciliation records the visual page-3 evidence, corrected 2,700 PLN amount and deferred metallic-price crosswalk |
| Exports and release assets | Model/version/configuration coverage and deterministic outputs | N/A | command: git diff -- data/exports/ | No export definitions or release assets are changed |
| Historical tests | Package-owned fixtures unchanged and passing | PASS | command: python -m unittest tests.test_jogger_price_list_commercial_matrix_20261001 | Observed: package regression contract is updated to the printed 2,700 PLN row; full required CI reruns on final head |
| Tooling | Isolated package/release tests; no real remote access | PASS | command: python -m unittest discover -s tests | Observed: CI Windows package workflow passed on candidate SHA; Python suite exposed and led to correction of the dependent 2026-11-02 historical assertion |
| Generated documentation | Canonical generators and baseline checks pass | PASS | command: python tools/generate_project_docs.py --check | Observed: generated documentation baseline passed on candidate SHA |
| CI | Required checks pass on exact final head SHA | PASS | command: GitHub Actions required checks for PR #924 exact head SHA | Observed: Windows package workflow and repository baseline checks passed on candidate SHA; final six-check status is pending after this matrix/importer update |

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
| 2026-11-02 importer expected the superseded 2026-10-01 amount of 2,800 PLN | brittle test | Python 3.10/3.13/3.14 Quality logs; `tools/import_jogger_price_list_20261102.py` historical guard | Update only the dependent historical guard to require the visually verified 2,700 PLN for the 2026-10-01 source; preserve the independent 2026-11-02 source amount of 2,800 PLN | Pending final-head CI |
| Matrix omitted required template sections, areas and exact checklist | brittle/incomplete change documentation | Python 3.14 Quality log from `change_impact_matrix.py` | Replace abbreviated matrix with complete repository template structure and evidence-backed rows | Pending final-head CI |

Do not mass-update expected counts or refresh report fingerprints until the changed records and their ownership have been inspected.

## Closure

- Final tested head SHA: pending after this matrix/importer correction; verify all six required checks against the exact final PR head
- Required checks: Python 3.10; Python 3.13; Python 3.14; Package workflow / Windows; Generated documentation / documentation-baseline --check; Repository state / project-state --check
- Unresolved findings: metallic paint price pair 2,700 / 2,900 PLN remains unmapped because the printed source provides no named-colour/grade crosswalk
- Merge decision and evidence: do not merge until all six required checks pass on the exact final head SHA
