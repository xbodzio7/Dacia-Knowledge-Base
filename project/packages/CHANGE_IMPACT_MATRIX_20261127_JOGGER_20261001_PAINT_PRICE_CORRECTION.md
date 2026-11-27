# Change impact matrix — Jogger MY26 2026-10-01 special paint price correction

## Package scope
Correct the dated special non-metallic paint surcharge from 2,800 PLN to 2,700 PLN for the 12 Jogger configurations linked to source `src_pl_jogger_price_my26_20261001`.

## Source and evidence
- Archived source: `owner_supplied/2026-10-01/f5cdbd7878.pdf`
- SHA-256: `12e536c1e60e9e7f91228b27a9d962cecacb5a5287d585f419a14af3003e8b46`
- Printed page: 3
- Visual render and source-identity verification: workflow run [46047957727](https://github.com/xbodzio7/Dacia-Knowledge-Base/actions/runs/46047957727)
- Printed special non-metallic row: `0 / 2,700 PLN`
- Printed metallic paint pair: `2,700 / 2,900 PLN`; no colour/grade mapping is inferred.

## Directly changed data and contracts
- `data/imports/jogger_commercial_items_20261001.csv`
- `data/imports/jogger_commercial_item_configurations_20261001.csv`
- `data/master/commercial_items.csv`
- `data/master/commercial_item_configurations.csv`
- `data/master/sources.csv`
- `tools/import_jogger_price_list_commercial_matrix_20261001.py`
- `tests/test_jogger_price_list_commercial_matrix_20261001.py`
- `data/reporting/jogger_price_list_20261001_reconciliation_001.json`

## Downstream impact review
- The 12 dated commercial-item mappings are corrected to 2,700 PLN.
- The importer contract and regression test must assert the same source-backed item note and amount.
- The reconciliation report and source registry note are aligned with the verified page.
- Existing catalogue prices, historical July mappings, source PDF bytes, identifiers and unrelated commercial items are unchanged.
- Metallic paint remains deferred because the source does not provide an exact colour/grade crosswalk.
- No analytical configuration-price, equipment, availability or configuration-value tables are changed; no downstream report inputs depend on this commercial-item-only correction.

## Validation required
- Python 3.10, 3.13 and 3.14 unit suites.
- Windows package workflow.
- Generated documentation baseline check.
- Repository project-state check.
- Confirm all six required checks pass on the exact final PR head SHA before merge.
