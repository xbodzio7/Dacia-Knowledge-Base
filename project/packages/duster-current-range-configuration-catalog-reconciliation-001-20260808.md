# Duster Current Range Configuration Catalog Reconciliation

Date: 2026-08-08  
Package: `duster_current_range_configuration_catalog_reconciliation_001`

## Goal

Align the canonical Duster configuration catalogue with the current official Polish MY26 range before downstream exact-configurator completeness products treat the current Duster scope as complete.

## Source-backed current range

The official Polish Duster price list effective 2026-07-03 defines 16 current grade/powertrain surfaces across Essential, Expression, Extreme and Journey. Before this package, 13 of those current surfaces already had canonical exact configuration identities and three current `hybrid-G 150 4x4` surfaces were missing.

The repository also preserves fourteen Duster rows from earlier source phases. They remain valid historical/source-bounded observations and are not deleted or assigned a new status value in this package.

## Master-data changes

- add `duster_iii_expression_hybridg150_4x4_automatic`;
- add `duster_iii_extreme_hybridg150_4x4_automatic`;
- add `duster_iii_journey_hybridg150_4x4_automatic`;
- link each new identity to `src_pl_duster_price_my26_20260703` in `source_configurations.csv`;
- add an explicit three-configuration reporting scope with no projected technical or equipment slots;
- preserve all existing Duster configuration rows, versions and historical price evidence unchanged.

After reconciliation the canonical registry contains 84 configuration rows and all 16 current Duster identities are represented. Current-range membership remains source/date scoped; it is not encoded by retroactively changing historical configuration status.

## Evidence boundary

This package adds configuration identity only. It does not infer technical values, standard equipment, packages/options or appearance for `hybrid-G 150 4x4`. It also does not rewrite historical prices. The current repository status vocabulary is preserved; no new `deprecated` state is introduced.

The source-coverage report therefore records all three identity links as present, treats technical and equipment areas as intentionally not applicable to this identity-only scope, and leaves exactly three commercial price sections missing for the bounded follow-up.

Historical brochure import and review contracts recognize these later exact identities while continuing to exclude them from the earlier Duster brochure technical, cargo, chassis and dimension packages.

The three current catalogue prices are imported separately so configuration identity and price provenance remain independently testable.

## Reporting propagation

The explicit scope brings the current portfolio to 84 active configurations across 23 reporting scopes and 133 within-scope pairs. Exactly 81 configurations have recorded catalogue prices; the three deliberate price gaps are the new Duster identities. Portfolio family, version, source-coverage and powertrain/transmission outputs are regenerated from the same 254 explicit source-to-configuration relationships without creating cross-scope comparisons, rankings, recommendations or inferred values.

## Next package

`duster_hybridg150_current_price_import_001` will add the official 2026-07-03 catalogue gross prices for the three newly canonical identities:

- Expression — 119,900 PLN;
- Extreme — 125,900 PLN;
- Journey — 126,100 PLN.

No historical stock-card or earlier catalogue price will be removed.
