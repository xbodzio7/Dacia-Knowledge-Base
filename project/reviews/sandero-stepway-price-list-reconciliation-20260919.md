# Sandero / Sandero Stepway — cennik 11.08.2026 reconciliation review

Date: 2026-09-19

## Source

The owner-supplied official 7-page Polish price list is effective from 11.08.2026. Original PDF SHA-256:

`c220ab0ff1df848b72121c6ebe0f05fb245bb9b70052a10dbd48068709b2034a`

The complete normalized extract is stored in `project/sources/sandero_stepway_price_my26_20260811_full_extract.json`.

## Coverage

All seven pages were reviewed. Pages 3 and 6 were additionally checked as rendered pages because the equipment matrix and dimension drawing contain visual/table information that text extraction can distort.

No master data is changed by this review.

## Key result

The 11.08.2026 price matrix contains **19 explicit Sandero/Sandero Stepway catalogue combinations**. The current `data/master/configurations.csv` contains 15 Sandero/Sandero Stepway combinations from the earlier catalogue slice. The current price list therefore exposes **four explicit configuration candidates not yet represented in the master configuration catalogue**:

- `sandero_iii_expression_hybrid155_automatic` — 84,600 PLN
- `sandero_iii_journey_hybrid155_automatic` — 90,200 PLN
- `sandero_stepway_iii_expression_hybrid155_automatic` — 90,700 PLN
- `sandero_stepway_iii_extreme_hybrid155_automatic` — 96,800 PLN

This is a source-backed catalogue gap, not an inference. Current official Dacia pages also expose Hybrid 155 for Sandero and Sandero Stepway. 

## Commercial-price boundary

The price list is now the primary current source for catalogue and option/package prices. In particular, the 11.08.2026 document states:

- COMFORT (Eco-G 120 auto): 2,000 PLN
- THERMO: 1,900 PLN
- ZIMOWY: 1,200 PLN
- MEDIA NAV LIVE: 1,600 PLN
- EASY: 1,600 PLN

An older exact configurator snapshot dated 09.08.2026 contains a 1,400 PLN value for EASY on Sandero Journey Eco-G 120 automatic. This package does **not** replace the current 11.08 price-list value. The historical configurator observation must remain historical evidence.

## Colour boundary

The current price list provides paint surcharge classes but does not name individual colours in the equipment matrix. Therefore:

- paint surcharge amounts should come from the price list;
- exact colour names and exact colour/configuration compatibility still require exact-state configurator or other direct colour evidence;
- no colour-name-to-price mapping is inferred merely from the generic 2,500/2,700 PLN cells.

## Technical data

The document also supplies the Hybrid 155 technical row, dimensions for both body variants, WLTP values, fuel-tank data, equipment matrix and package contents. These are preserved in the full extract without converting source wording into unsupported broader semantics.

## Next package

`sandero_stepway_price_list_20260811_master_reconciliation_001` should:

1. add the four explicit Hybrid 155 configuration records;
2. reconcile current catalogue/package prices against dated commercial mappings;
3. preserve 03.07.2026 history;
4. avoid overwriting historical configurator observations;
5. only then reassess which exact colour surfaces still require interactive configurator evidence.

No CAT-GAP-002 surface is closed by this review merely because a colour surcharge appears in the price list.
