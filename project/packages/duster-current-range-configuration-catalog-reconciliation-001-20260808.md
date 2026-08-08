# Duster Current Range Configuration Catalog Reconciliation

Date: 2026-08-08  
Package: `duster_current_range_configuration_catalog_reconciliation_001`

## Goal

Align the canonical Duster configuration catalogue with the current official Polish MY26 range before any downstream exact-configurator completeness product treats the registry as current.

## Source-backed current range

The official Polish Duster price list effective 2026-07-03 defines 16 current grade/powertrain surfaces across Essential, Expression, Extreme and Journey. The previously registered catalogue contained 27 active Duster surfaces: 13 matched the current range, three current `hybrid-G 150 4x4` surfaces were absent, and fourteen prior-phase surfaces remained active.

## Master-data changes

- add `duster_iii_expression_hybridg150_4x4_automatic`;
- add `duster_iii_extreme_hybridg150_4x4_automatic`;
- add `duster_iii_journey_hybridg150_4x4_automatic`;
- mark configuration IDs 8–21 `deprecated` rather than deleting them;
- mark `duster_iii_journey_plus` `deprecated` because it has no current configuration in the 2026-07-03 range;
- preserve every historical configuration and price observation.

After reconciliation the canonical registry contains 84 configuration rows, 70 active rows overall and exactly 16 active Duster surfaces. All 16 current Duster identities are represented and no prior-phase Duster identity remains active.

## Evidence boundary

This package changes configuration identity/status only. It does not infer technical values, standard equipment, packages/options or appearance for `hybrid-G 150 4x4`. It also does not rewrite historical prices. The three current catalogue prices are imported separately so catalogue identity reconciliation and price provenance remain independently testable.

## Next package

`duster_hybridg150_current_price_import_001` will add the official 2026-07-03 catalogue gross prices for the three newly canonical identities:

- Expression — 119,900 PLN;
- Extreme — 125,900 PLN;
- Journey — 126,100 PLN.

No historical stock-card or earlier catalogue price will be removed.
