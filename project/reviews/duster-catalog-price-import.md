# Duster Catalog Price Import

## Scope

This package imports the 24 explicit catalogue gross prices shown in the page-1 Duster MY26/PY25 price matrix.

Each record is linked to:

- an existing source-backed Duster III configuration,
- market `PL`,
- price type `catalog_gross`,
- currency `PLN`,
- date `2026-02-06`,
- source `src_pl_duster_price_my26_py25_20260206`.

## Evidence boundary

The first page separately advertises a discount of up to 10,000 PLN and a financing benefit of up to 18,000 PLN. Neither value is a catalogue price, so neither is imported into `configuration_prices.csv`.

A dash in the matrix is treated as absence of that version and powertrain combination from the source. No zero-price or unavailable-price record is created.

The heading `ROCZNIK 2025` is preserved in record notes. The observation date remains the conservative price-list effective date printed in the document: 6 February 2026.

## Price matrix

| Powertrain | essential | expression | extreme | journey | journey+ |
| --- | ---: | ---: | ---: | ---: | ---: |
| Eco-G 100 4x2 | 82,000 | 90,000 | 96,000 | 96,000 | — |
| mild hybrid 130 4x2 | — | 97,600 | 103,600 | 103,800 | — |
| hybrid 140 4x2 | — | 112,100 | 118,100 | 118,300 | 123,600 |
| mild hybrid 130 4x4 | — | 111,900 | 117,900 | 117,900 | — |
| Eco-G 120 4x2 | 82,000 | 90,000 | 96,000 | 96,200 | — |
| mild hybrid 140 4x2 | — | 97,600 | 103,600 | 103,800 | — |
| hybrid 155 4x2 | — | 112,100 | 118,100 | 118,300 | — |

All amounts are gross catalogue prices in PLN.

## Compatibility

The seven existing Sandero prices remain unchanged. Ten Sandero-specific regression guards now count only configurations present in their own expected manifests instead of freezing the repository-wide price-table size.

## Validation

Acceptance requires:

- exactly 24 Duster price rows and exact matrix parity,
- no promotional values imported as prices,
- exact date, market, type, currency and source provenance,
- 31 total price records,
- SQLite parity at 34 tables and 1,464 rows,
- unchanged explicit Sandero reporting subset,
- full Quality and Windows checks.

The final Quality run must use the clean branch head after README and changelog synchronization; no transport workflow or synchronization script is part of the package diff.
