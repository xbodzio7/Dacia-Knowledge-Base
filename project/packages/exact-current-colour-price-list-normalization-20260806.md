# Exact current colour price-list normalization

Date: 2026-08-06  
Gap: `CAT-GAP-002`  
Source commit: `d0e4d21ab3da26363494708506db0873822864f2`

## Goal

Finish the document phase for Sandero, Sandero Stepway and Duster by extracting the exact current July 2026 paint-price rows before any bounded configurator capture.

## Result

- 18 normalized grade/paint-class rows;
- six Sandero and Sandero Stepway grade rows;
- twelve Duster grade/class rows;
- eight exact named Duster non-metallic rows;
- no configurator use;
- no master-data mutation;
- `CAT-GAP-002` remains open.

## Sandero and Sandero Stepway

The current combined table uses six columns in this order:

1. Sandero essential;
2. Sandero expression;
3. Sandero journey;
4. Sandero Stepway essential;
5. Sandero Stepway expression;
6. Sandero Stepway extreme.

The printed row `Lakier metalizowany lub niemetalizowany specjalny` contains:

- 2500 PLN for Sandero essential, expression and journey;
- 2500 PLN for Stepway essential;
- 2500 or 2700 PLN for Stepway expression and extreme.

The document does not align those price alternatives to colour names and does not distinguish powertrains. The direct Sandero delivery URL and the registered combined Sandero/Stepway URL remain separate official source identities; byte identity is not inferred.

## Duster

For essential, expression, extreme and journey the current price list prints:

- metallic paint: 2700 or 2900 PLN;
- Biel Alpejska: 0 PLN;
- Khaki Lichen: 2700 PLN.

These are grade-level rows. They do not prove powertrain-specific colour compatibility or align the two metallic prices to individual metallic colour names.

## Current-range drift

The same current Duster price list contains five powertrain rows:

- Eco-G 120 4x2;
- Eco-G 120 auto 4x2;
- mild hybrid 140 4x2;
- hybrid 155 4x2;
- hybrid-G 150 4x4.

The active registry contains 27 Duster surfaces. Thirteen match the current price matrix, three hybrid-G 150 4x4 grade surfaces are absent, and fourteen prior-phase surfaces remain active although they are not printed in the current price list. This package records the difference but does not add, remove or reclassify configurations.

## Files

- `data/reporting/exact_current_colour_price_list_normalization_20260806.json`
- `data/reporting/exact_current_colour_price_list_normalization_20260806.csv`
- `data/reporting/duster_current_range_configuration_drift_review_20260806.json`
- `data/reporting/cross_model_colour_document_progress_overlay_20260806.json`

## Boundaries

- no colour-name inference from price order;
- no powertrain compatibility inferred from grade-level rows;
- no unavailable colour inferred from absence;
- no cross-model or cross-source lexical normalization;
- no current Duster configuration-catalog mutation;
- no live-market completeness claim.

## Next step

Capture exact current colour choice lists for the 15 Sandero and Sandero Stepway surfaces first. Duster exact choice capture remains behind a separate current-range configuration-catalog review because the live source and active registry no longer describe the same set of powertrains.
