# Duster MY26 — 2026-11-02 official price-list commercial reconciliation

## Objective

Close the importable commercial-data deltas in the official Polish Duster MY26 price list effective 2026-11-02. This package is deliberately restricted to the cennik; brochures and configurator evidence are excluded.

## Source

- Source code: `src_pl_duster_price_my26_20261102`
- Official PDF: https://cdn.group.renault.com/dac/pl/pdf/cenniki/duster-price.pdf.asset.pdf/f07ca0a87f.pdf
- Document date: 2026-11-02
- Ten printed pages, archived at `PDF/Cenniki/DACIA DUSTER cennik MY26 20261102.pdf`.
- Verified SHA-256: `dd6c65d048d7531251967ba39bb8ab6767256882325254e9b3eaafac11d89118`.

## Changes

- Register the source and link it to 16 existing configurations and four existing grades.
- Add two named non-metallic colour items and memberships:
  - Biel Alpejska: 0 PLN.
  - Khaki Lichen: 2,800 PLN.
- Add 16 dated spare-wheel states: six optional at 900 PLN; ten explicitly unavailable with LPG.
- Add 16 dated TECHNO 1 states: three automatic Extreme configurations optional at 2,900 PLN; the other 13 explicitly unavailable.
- Update the existing spare-wheel and TECHNO 1 item notes to reflect the current cennik.

## No-duplicate boundary

- Page-1 catalogue prices: 16 existing observations reused; no new price rows.
- Equipment matrix: 1,152 existing availability observations reused; no new availability rows.
- Page-6 technical data: 391 existing scalar observations and 16 ranges reused; no new technical rows. The table states 230 V for Hybrid 155, matching the 2026-09-01 table.
- The `hybridg150` canonical configuration codes remain unchanged although the current cennik prints “tribrid 150 4X4”.

## Deferred evidence

- Metallic paint 2,800 / 3,000 PLN: no named colour-to-price mapping in the cennik.
- Page-8 winter-wheel accessory list: separate accessory catalogue.
- Page-9 paired dimensions: no exact configuration crosswalk.
- Page-2 narrative voltage (260 V) vs page-6 technical-table voltage (230 V): preserve both source contexts. The table agrees with the previous 2026-09-01 value; no new voltage observation is warranted.
- Page-10 legal and commercial disclosures: reviewed; not configuration-level prices.

## Source review correction

The initial text extraction misread the page-6 table's `230 V` as `280 V`. Visual inspection of the archived PDF confirms `230 V full hybrid`. The earlier report's claimed 280 V delta and missing-source-hash blocker were incorrect; both have been corrected. The PDF has ten pages, including a separate page 10 for legal terms.

## Reproducibility and validation

- Import specs: `data/imports/duster_price_list_20261102_*.csv`
- Deterministic importer: `tools/import_duster_price_list_20261102.py`
- Validation: `python tools/import_duster_price_list_20261102.py`
- Regression test: `tests/test_duster_price_list_20261102.py`
