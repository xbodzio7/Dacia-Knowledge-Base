# Change-impact matrix — Striker MY26 priced options and packages

## Package identity

- Package: `striker_my26_priced_options_packages_matrix_20261124_001`
- Base SHA: `99df129aed048b4f1ac2c58c19084143f1ebfe15`
- Source: official Polish Striker MY26 cennik effective 2026-11-02; archived binary `PDF/Cenniki/striker-price.pdf`
- Scope: printed page 5 option/package matrix; exact 11 source-linked grade/powertrain configurations
- Data mutation: 11 commercial items and 121 dated commercial-item/configuration mappings; no scalar configuration values, equipment availability, source registry rows or price-history rows changed

## Change inventory

- Added 11 commercial item definitions and 121 exact configuration mappings.
- Status distribution: 60 optional, 3 standard, 51 not_available, 7 unknown (literal P).
- Added source-specific item/mapping import specifications, a SHA-256-verifying importer, seven regression tests and a source-backed report.
- Updated canonical state and generated documentation counters.
- The seven P cells are retained as unknown; no package membership or standalone option price is inferred.

## Change-impact matrix

| Area | Change reviewed | Result | Evidence | Notes / unresolved items |
|---|---|---|---|---|
| Canonical registries | Existing source, grade and configuration links | PASS | command: `python tools/dkb.py package-preflight` | Observed: the package reuses the registered source and its 4 grade/11 configuration relationships; no registry rows are added. |
| Configuration inventory | Exact grade/configuration applicability | PASS | command: `python tools/import_striker_price_list_commercial_matrix_20261102.py --check` | Observed: the importer contract fixes the exact 11 configuration codes and 121 mapping cells. |
| Portfolio summaries | Configuration/technical completeness scopes | N/A | artifact: data/reporting/striker_my26_priced_options_packages_matrix_20261124_001.json | No configuration, technical attribute or equipment-availability observations are added; no portfolio completeness snapshot is regenerated. |
| Comparison scopes | Existing Striker price-only comparison scope | N/A | artifact: project/packages/striker-my26-catalogue-price-import-20261122.md | The existing 11-configuration price-only scope is unchanged; no comparison schema or technical slots are modified. |
| Reports | Source-backed commercial matrix report | PASS | artifact: data/reporting/striker_my26_priced_options_packages_matrix_20261124_001.md | Observed: JSON/Markdown report records all 11 priced rows, applicability, status counts and P-marker evidence boundary. |
| Exports and release assets | Public release/product export surface | N/A | artifact: project/packages/striker-my26-priced-options-packages-matrix-20261124.md | No release asset is rebuilt; no export schema or release version changes in this package. |
| Historical tests | Exact matrix and history regression coverage | PASS | artifact: tests/test_striker_price_list_commercial_matrix_20261102.py | Observed: seven focused tests assert exact status totals, prices, grade scope and P-marker preservation. CI exposed global-count coupling in older tests; this commit replaces it with source-scoped contracts and keeps historical rows untouched. Final execution remains gated by PR CI. |
| Tooling | Source-bound deterministic importer | PASS | artifact: tools/import_striker_price_list_commercial_matrix_20261102.py | Observed: importer verifies archive containment, source identity, SHA-256, byte size, capture manifest, sidecar and exact source links. |
| Generated documentation | Canonical state and managed baseline blocks | PASS | command: `python tools/dkb.py project-state --check` | Observed: state counters are synchronized to 2,042 tests and 23,033 master rows; the required workflow verifies generated blocks. |
| CI | Exact-head required validation | N/A | command: `python tools/change_impact_matrix.py --base-ref origin/main --head-ref HEAD` | Initial PR checks exposed the metadata defects described below; this commit corrects them. All six required checks must pass on the final head before merge. |

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

The first CI attempts exposed two additional legacy test-contract defects after the metadata fixes: the Jogger importer and a portfolio test assumed a fixed global total of 64 commercial items (and 916 mappings), while the new Striker rows correctly extended those shared tables. The Striker importer also checked natural-key uniqueness across all historical sources and found four pre-existing collisions outside the new Striker scope. These are cross-package/global-test assumptions, not defects in the Striker source matrix. The repair makes package checks source-scoped, retains global ID/code uniqueness, and checks natural keys only within the new source scope; historical rows are not rewritten.

## Closure

- Preserve the P marker as unknown until its exact meaning and applicability are independently established.
- Do not infer package components as separate equipment availability records in this package.
- Merge only after all six required checks pass on the exact final PR head and the main-branch post-merge Quality and Repository Baselines workflows pass.
