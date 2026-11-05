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
2. Thirteen unique source-to-configuration relationships.
3. Thirteen exact catalogue gross prices from printed page 1.
4. No historical price row overwritten and no duplicate new record.
5. Regression test and repository Quality pass on the final PR head.

## Evidence boundary
The PDF is 8 pages and was text-extracted from the owner-supplied Library item. This package imports only page-1 catalogue gross prices. Promotional/financing claims, option/package prices, and page-6 technical specifications are excluded from this package. No SHA-256 is asserted because raw PDF bytes were not available for hashing in the repository runtime.

## Next
Continue the canonical `official_bigster_brochure_full_assimilation_20261014_001` package with the page-4/5 equipment and package matrix and page-6 technical table, reusing prior page-20–22 reviews and importing only exact unsuperseded gaps.
