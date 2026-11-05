# Bigster MY26 price-list catalogue-price import — 2026-11-02

## Scope
Register the owner-supplied official Dacia Poland Bigster MY26 price list effective 2026-11-02 and add its 13 exact catalogue gross price observations for configurations already present in the canonical configuration inventory.

## Manifest
- `data/master/sources.csv`
- `data/master/source_configurations.csv`
- `data/master/configuration_prices.csv`
- `data/reporting/bigster_price_list_20261102_price_import.json`
- `data/reporting/bigster_price_list_20261102_price_import.md`
- `tests/test_bigster_price_list_20261102.py`

## Acceptance
1. One active source registry row with effective/document date 2026-11-02.
2. No technical/equipment source relationships; each price row references the source and configuration directly.
3. Thirteen exact catalogue gross prices from printed page 1.
4. No historical price row overwritten and no duplicate new record.
5. Regression test and repository Quality pass on the final PR head.

## Evidence boundary
The PDF is 8 pages and was text-extracted from the owner-supplied Library item. This package imports only page-1 catalogue gross prices. Promotional/financing claims, option/package prices, and page-6 technical specifications are excluded from this package. No SHA-256 is asserted because raw PDF bytes were not available for hashing in the repository runtime.

## Follow-up reconciliation
The page-4/5 commercial option and package price matrix was imported separately for the 2026-10-01 and 2026-11-02 price lists under `bigster_price_list_20261001_20261102_commercial_matrix_import_20261105_001`. This preserves dated prices without overwriting the July history. The 2026-11-02 page-6 technical table remains a separate source-to-master reconciliation.
