# Official Model Price-List Reconciliation

Date: 2026-08-06  
Gap: `CAT-GAP-001`  
Result: closed

## Goal

Reconcile the current official Polish model price-list layer for Spring, Sandero, Sandero Stepway, Jogger, Duster and Bigster. Each active model must have either a registered current range price list or an explicit official-source absence record.

## Result

- Sandero and Sandero Stepway use the registered combined MY2026 price list effective from 2026-07-03.
- Jogger has a registered MY2026 price list effective from 2026-07-03, covering separate five- and seven-seat surfaces.
- Duster has a registered MY2026 price list effective from 2026-07-03.
- Bigster has a registered MY2026 price list effective from 2026-07-03.
- The current Spring model page links to a price list effective from 2026-07-08 that is explicitly limited to model-year-2025 dealer stock. No separate current MY26 all-grade range price list was resolved from the current official Polish model page or registered source inventory, so Spring is closed through an explicit official-source absence record rather than by treating the stock document or configurator as a current range price list.

## Evidence boundary

Closing `CAT-GAP-001` establishes source identity, validity dates and the Spring absence classification. It does **not** establish complete current compatibility or prices for:

- exterior colours;
- wheels and wheel covers;
- upholstery and interior trim;
- standalone options;
- option packages.

Those remain open under `CAT-GAP-002` through `CAT-GAP-013`.

## Data changes

- no master-data rows changed;
- no source rows added;
- no configuration relationships changed;
- no prices or availability states imported;
- no cross-model, grade, powertrain or document-date transfer.

## Files

- `data/reporting/official_model_price_list_reconciliation_20260806.json`
- `data/reporting/official_model_price_list_reconciliation_20260806.csv`
- `data/reporting/cross_model_nonconfigurator_catalog_gap_status_20260806.json`

## Next package

`CAT-GAP-002`: reconcile the complete current colour catalogue and grade/powertrain compatibility graph from the now-registered price-list layer, using bounded configurator choice lists only where the documents do not resolve exact dependencies.
