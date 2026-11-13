# Cross-Model Residual Coverage Review — Official Polish Dacia Price Lists

**Reviewed:** 2026-11-14  
**Scope:** Registered official Polish Dacia cenniks only. Brochures, configurator captures, dealer campaigns and separately distributed accessory catalogues remain out of scope.

## Executive result

Six registered source/date entries were reconciled against current master data. One actionable master-data gap remains: the Jogger 2026-10-01 commercial matrix has 54 missing option/package mappings (38 optional, 16 explicitly unavailable) and one missing commercial-item definition for special non-metallic paint.

The other reviewed price and commercial records are already represented. No duplicate catalogue-price rows are proposed.

## Cross-model coverage

| Model / source date | Catalogue price cells | Source-specific price rows | Commercial mappings present | Residual |
|---|---:|---:|---:|---|
| Duster 2026-11-02 | 16 | 0 new (16 reused) | 64 | No price gap; preserve 230 V table / 260 V narrative |
| Bigster 2026-10-01 | 13 | 13 | 86 | No master-data gap |
| Bigster 2026-11-02 | 13 | 13 | 86 | PDF binary archive pending; no data gap |
| Sandero / Stepway 2026-11-02 | 15 | 15 | 209 | No current price/mapping gap in reviewed matrix |
| Jogger 2026-10-01 | 11 | 11 | 0 | 54 commercial mappings missing |
| Spring MY25 stock 2026-07-08 | 2 | 2 | 10 | MY26 source not registered; do not generalize MY25 stock |

Totals: **70 catalogue price cells**, **54 source-specific price rows**, **16 already represented/reused price cells**, and **455 existing commercial mappings**. The 54 missing Jogger mappings are excluded from the existing-mapping total.

## Jogger — exact next import scope

The 2026-10-01 official Jogger cennik pages 3–4 supports this matrix across the 12 source-linked configurations:

| Item | Optional | Not available | Total |
|---|---:|---:|---:|
| Special non-metallic paint — 2,800 PLN | 12 | 0 | 12 |
| Media Nav — 1,600 PLN | 10 | 2 | 12 |
| Heated front seats — 700 PLN | 4 | 2 | 6 |
| ZIMOWY package — 1,200 PLN | 6 | 6 | 12 |
| DRIVE package — 1,400 PLN | 6 | 6 | 12 |
| **Total** | **38** | **16** | **54** |

One new commercial item is needed: `jogger_special_nonmetallic_paint_option`. Existing Media Nav, heated seats, ZIMOWY and DRIVE items are reused.

Evidence boundaries:
- Page 3 distinguishes non-metallic (0 PLN) from special non-metallic (2,800 PLN); only the paid special non-metallic choice is added.
- The metallic paint pair 2,800 / 3,000 PLN is not mapped to named colours or grades because the source does not establish that relationship.
- Extreme heated front seats are marked `P` (part of a package), so no standalone Extreme mapping is created; the priced ZIMOWY package is represented instead.
- No removed KOMFORT package or separate accessory list is inferred into the current matrix.

The source-linked master price rows already contain 11 exact catalogue prices. Correct 7-seat Eco-G 120 manual alignment: Essential has no price (`-`), Expression is 86,550 PLN, Extreme is 94,400 PLN. The earlier report incorrectly shifted the first two grade cells; master price records are already aligned correctly.

## Other residual boundaries

- **Duster:** all 16 November catalogue price cells are represented by existing price history. The technical table's 230 V and narrative 260 V remain separate contexts; do not add 280 V. The winter-wheel list is a separate accessory scope.
- **Bigster:** both October and November lists have 13 catalogue prices and 86 commercial mappings. The November PDF has a verified source hash but its binary is not archived in the repository. Its technical page is already covered by the October source's 22 import specifications and 150 observations.
- **Sandero / Stepway:** 15 catalogue prices and 209 commercial mappings are represented. Four Hybrid 155 prices are unchanged and are not duplicated under the November source.
- **Spring:** two prices and ten commercial mappings are specific to MY25 dealer stock. No MY26 Spring cennik is registered; MY25 stock data and promotions must not be generalized.

## Validation and exclusions

- Source identities, dates, registered hashes, source-linked configuration counts and master mapping counts were checked against current repository files.
- No brochure or configurator evidence was used.
- No source omission was interpreted as unavailability.
- Existing history and correct master observations are retained; no duplicate price observations are proposed.

## Next package

Implement the Jogger commercial matrix completion as one bounded package: add one special non-metallic paint item and 54 dated mappings, correct the existing reconciliation report, independently verify every mapping against printed pages 3–4, and run full Quality on the final commit.
