# Change-impact matrix template

Copy this file into the package directory and complete it before requesting review for any change to a model, version, configuration, source registry, shared source or reporting scope.

## Package identity

- Package:
- PR:
- Base SHA:
- Candidate head SHA:
- Change owner:
- Source/evidence IDs:

## Change inventory

| Entity type | Exact IDs | Added | Changed | Removed | Evidence / reason |
|---|---|---:|---:|---:|---|
| Models | | | | | |
| Versions | | | | | |
| Configurations | | | | | |
| Sources | | | | | |
| Source mappings | | | | | |
| Reporting scopes | | | | | |

## Change-impact matrix

| Area | Required evidence | Result (PASS / FAIL / N/A) | Exact command or artifact | Notes / unresolved items |
|---|---|---|---|---|
| Canonical registries | Exact IDs and referential integrity | | | |
| Configuration inventory | Active/inactive classification and source-backed applicability | | | |
| Portfolio summaries | Derived counts reconcile with emitted records | | | |
| Comparison scopes | Supported inclusion and reconciled pair/scope totals | | | |
| Reports | Direct/transitive consumers reviewed; findings re-evaluated | | | |
| Exports and release assets | Model/version/configuration coverage and deterministic outputs | | | |
| Historical tests | Package-owned fixtures unchanged and passing | | | |
| Tooling | Isolated package/release tests; no real remote access | | | |
| Generated documentation | Canonical generators and baseline checks pass | | | |
| CI | Required checks pass on exact final head SHA | | | |

## Test-contract review

- [ ] Mutable portfolio-wide counts are derived from canonical registries, not copied into tests as unexplained literals.
- [ ] Exact counts are limited to immutable fixtures or explicitly frozen, versioned contracts.
- [ ] Existing package tests remain bounded to their own manifests and source/configuration scopes.
- [ ] New package records are asserted exactly once, with explicit negative checks for duplicates/out-of-scope records.
- [ ] Aggregate counts are reconciled independently against emitted records.
- [ ] Historical snapshots and release baselines were not regenerated from current live data.
- [ ] Changed report dependencies are reviewed; stale reports remain needs_review until re-evaluated.
- [ ] Package lifecycle tests use fresh temporary repositories/staging areas and a local bare remote if push behavior is tested.
- [ ] Negative-path fixtures cannot contaminate success-path tests.
- [ ] The final diff was reviewed against the exact base SHA.

## Failure classification

For every failed check, classify it before editing:

| Failure | Category (product / stale report / brittle test / fixture leak / environment / external service) | Evidence inspected | Corrective action | Re-run result |
|---|---|---|---|---|
| | | | | |

Do not mass-update expected counts or refresh report fingerprints until the changed records and their ownership have been inspected.

## Closure

- Final tested head SHA:
- Required checks:
- Unresolved findings:
- Merge decision and evidence:
