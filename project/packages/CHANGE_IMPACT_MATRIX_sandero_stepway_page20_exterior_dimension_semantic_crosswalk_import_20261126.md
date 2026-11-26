# Change-impact matrix — Sandero Stepway page-20 exterior dimensions

## Package identity

- Package: `sandero_stepway_page20_exterior_dimension_semantic_crosswalk_import_20261126`
- PR: #922
- Base SHA: `c08d93156f3977cd4ba1ce0ad96cbc9e90bfcd57`
- Candidate head SHA: `829a8a53b3ec80e83572c2938457f809e234eaff` (matrix-only follow-up remains subject to exact-head CI)
- Change owner: DKB maintainer
- Source/evidence IDs: `src_pl_sandero_stepway_brochure_20260202`; page 20; five exact Eco-G 120 source-configuration relationships

## Change inventory

| Entity type | Exact IDs | Added | Changed | Removed | Evidence / reason |
|---|---|---:|---:|---:|---|
| Models | `sandero_stepway_iii` | 0 | 0 | 0 | Existing model reused |
| Versions | Essential, Expression, Extreme | 0 | 0 | 0 | Existing versions reused |
| Configurations | Five exact Eco-G 120 manual/automatic configurations | 0 | 0 | 0 | Existing source links reused |
| Sources | `src_pl_sandero_stepway_brochure_20260202` | 0 | 0 | 0 | Existing archived PDF reused |
| Scalar observations | `front_track`, `rear_track`, `ground_clearance` | 15 | 0 | 0 | Three declarative import specs, five configurations each |
| Reporting scopes | Stepway automatic completeness and shared manual gap evidence | 0 | 2 | 0 | Existing comparison contracts updated to reflect newly observed track dimensions |

## Change-impact matrix

| Area | Required evidence | Result (PASS / FAIL / N/A) | Evidence (command: ... / artifact: ...) | Notes / unresolved items |
|---|---|---|---|---|
| Canonical registries | Exact IDs and referential integrity | PASS | artifact: data/master/source_configurations.csv | Observed: the brochure remains linked to exactly five active Eco-G 120 configurations; no model, version, configuration or source registry rows were added or changed |
| Configuration inventory | Active/inactive classification and source-backed applicability | PASS | artifact: data/master/configuration_attribute_values.csv | Observed: 15 new rows cover exactly three attributes across the five source-linked configurations; no TCe 110 or Hybrid 155 applicability was inferred |
| Portfolio summaries | Derived counts reconcile with emitted records | N/A | artifact: project/state.json | No model/version/configuration portfolio identities or commercial counts changed; only 15 dated scalar observations were added |
| Comparison scopes | Supported inclusion and reconciled pair/scope totals | PASS | artifact: data/reporting/sandero_stepway_ecog120_automatic_completeness.json | Observed: front_track and rear_track are now included in the Stepway automatic technical scope; six obsolete manual Stepway missing-evidence decisions were removed from the shared manual evidence file |
| Reports | Direct/transitive consumers reviewed; findings re-evaluated | PASS | artifact: data/reporting/sandero_stepway_page20_exterior_dimension_semantic_crosswalk_import_20261126.json | Observed: page-20 report records 15 imported values, reused observations, the unresolved 1853 mm width conflict, exclusions and source PDF SHA-256; report freshness validation passed after metadata and Markdown parity repair |
| Exports and release assets | Model/version/configuration coverage and deterministic outputs | N/A | artifact: project/state.json | No export schema, release asset or published data product is changed |
| Historical tests | Package-owned fixtures unchanged and passing | N/A | artifact: tests/test_configuration_value_import_specs.py | No historical fixture or frozen release baseline is modified; full Quality remains the required exact-head gate |
| Tooling | Isolated package/release tests; no real remote access | N/A | artifact: tools/dkb.py | No shared importer or workflow implementation is changed; existing declarative import and validation tooling is reused |
| Generated documentation | Canonical generators and baseline checks pass | PASS | command: python tools/dkb.py project-state --check | Observed: Repository Baselines run #45903565769 passed Generated documentation; project-state validation was still running at the time of matrix preparation and must pass again on the final head |
| CI | Required checks pass on exact final head SHA | N/A | command: python tools/change_impact_matrix.py --base-ref origin/main --head-ref HEAD | Workflows are unchanged; six required checks remain mandatory and must pass on the exact final PR head before merge |

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
| Stepway comparison scopes still treated newly imported front/rear track as missing | stale report | Quality run #45903260853 and Stepway reporting/HTML workflow logs | Add both attributes to the Stepway automatic technical scope and remove six obsolete manual Stepway gap decisions | Stepway automatic reporting and HTML report passed on subsequent head |
| Canonical package transition rejected a replanning receipt whose from-package ID did not match main's prior next-package ID | stale state metadata | Quality run #45903451667, Python 3.14 transition log | Align `package_replanning.from_package_id` with the exact package ID on base `main` | Project-state transition passed on subsequent head |
| Change-impact matrix was missing for source/master-data changes | CI contract | Quality run #45903565689, Python 3.14 job | Add this package-scoped matrix with all ten required areas, evidence, exact checklist and failure classification | Pending exact-head rerun |

## Closure

- Imported IDs: 8970–8984 (15 rows).
- Reused rather than duplicated: overall length, wheelbase, front/rear overhang, roof/body height and width with mirrors.
- Deferred: 1853 mm width/mirror-state semantic conflict.
- Excluded: interior top-view measurements and 14° seatback angles.
- Final tested head SHA: pending exact-head CI.
- Required checks: Python 3.10, Python 3.13, Python 3.14, Package workflow / Windows, Repository state / project-state --check, Generated documentation / documentation-baseline --check.
- Unresolved findings: 1853 mm width semantics remain open; no unsupported inference was imported.
- Merge decision: do not merge until all six required checks pass on the exact final head SHA.
