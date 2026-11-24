# Change-impact matrix — Striker MY26 matrix marker semantics correction

## Package identity

- Package: `striker_my26_matrix_marker_semantics_correction_20261124_001`
- PR: #897
- Base SHA: `5695c54ba971e710ac381e3a52b9f5f27d8d18c5`
- Candidate head SHA: `f9a54e249f4b0438271c8e7662bfee937426dd02`
- Change owner: Project Owner decision D-035; implementation by repository maintainer
- Source/evidence IDs: `src_pl_striker_price_my26_20261102`; `PDF/Cenniki/striker-price.pdf`; D-035

## Change inventory

| Entity type | Exact IDs | Added | Changed | Removed | Evidence / reason |
|---|---|---:|---:|---:|---|
| Models | none | 0 | 0 | 0 | No model records changed. |
| Versions | none | 0 | 0 | 0 | No version records changed. |
| Configurations | 11 existing Striker configuration codes | 0 | 0 | 0 | Existing 11 exact configuration links retained. |
| Sources | `src_pl_striker_price_my26_20261102` | 0 | 0 | 0 | Existing source registration and archived PDF unchanged. |
| Source mappings | 7 P mappings for `striker_heated_washer_nozzles_and_windscreen_option` | 0 | 7 | 0 | Reclassified from `unknown` to `package`; amounts remain empty. |
| Reporting scopes | `striker_my26_matrix_marker_semantics_correction_20261124_001` | 1 | 0 | 0 | Successor report records the owner-defined interpretation. |

## Change-impact matrix

| Area | Required evidence | Result (PASS / FAIL / N/A) | Evidence (command: ... / artifact: ...) | Notes / unresolved items |
|---|---|---|---|---|
| Canonical registries | Exact IDs and referential integrity | PASS | command: python tools/dkb.py package-preflight | Observed: PR CI package preflight passed, checking 121 CSV files, 615 JSON files and 4 source capture manifests. |
| Configuration inventory | Active/inactive classification and source-backed applicability | N/A | artifact: data/imports/striker_commercial_item_configurations_20261102.csv | No models, versions or configurations are added or removed; all 121 mappings remain on the existing 11 exact configurations. |
| Portfolio summaries | Derived counts reconcile with emitted records | N/A | artifact: data/reporting/striker_my26_matrix_marker_semantics_correction_20261124_001.json | No portfolio configuration/technical completeness scope changes; the canonical master-row baseline increases by one because the shared status dictionary gains one row. |
| Comparison scopes | Supported inclusion and reconciled pair/scope totals | N/A | artifact: project/state.json | No comparison configuration or pair scope changes. |
| Reports | Direct/transitive consumers reviewed; findings re-evaluated | PASS | artifact: data/reporting/striker_my26_matrix_marker_semantics_correction_20261124_001.json | Observed: successor report records 11 items/121 mappings, 7 package statuses, zero unknown P statuses, and explicitly leaves the named package identity unspecified. |
| Exports and release assets | Model/version/configuration coverage and deterministic outputs | N/A | artifact: project/state.json | No release version, downloadable data product or export schema is changed. |
| Historical tests | Package-owned fixtures unchanged and passing | N/A | artifact: tests/test_striker_price_list_commercial_matrix_20261102.py | Focused importer and regression checks are being executed by the required PR Quality matrix; no test result is claimed before completion. |
| Tooling | Isolated package/release tests; no real remote access | N/A | artifact: tools/import_striker_price_list_commercial_matrix_20261102.py | Importer contract updated; exact importer check remains part of CI validation. |
| Generated documentation | Canonical generators and baseline checks pass | N/A | command: python tools/dkb.py project-state --check | The first CI run detected the expected +1 master row and stale generated baseline blocks; this commit updates canonical state and managed counters. Recheck required. |
| CI | Required checks pass on exact final head SHA | N/A | command: python tools/change_impact_matrix.py --base-ref origin/main --head-ref HEAD | The first run correctly blocked because the required matrix file was absent. This file is the remediation; all six required checks must pass on the updated exact head before merge. |

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
| Missing package change-impact matrix | tooling / CI contract | Python 3.14 Quality log for PR #897 | Add this exact package matrix file | Pending next exact-head CI run |
| Canonical baseline drift after adding one controlled status row | generated documentation / repository state | Repository Baselines logs for PR #897 | Increase canonical master-row count to 23034 and regenerate managed documentation blocks | Pending next exact-head CI run |

## Closure

- Final tested head SHA: pending after corrective commit; do not merge on the initial head.
- Required checks: all six required status checks must pass on the final exact PR head.
- Unresolved findings: specific named package identity for the P-marked feature remains unspecified by the source and is not inferred.
- Merge decision and evidence: remain unmerged until the complete exact-head Quality and Repository Baselines checks pass.
