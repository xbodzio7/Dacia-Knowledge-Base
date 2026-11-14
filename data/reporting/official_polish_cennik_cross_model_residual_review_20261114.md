# Cross-Model Residual Coverage Review — Official Polish Dacia Price Lists

**Reviewed:** 2026-11-14  
**Scope:** Registered official Polish Dacia cenniks only. Brochures, configurator captures, dealer campaigns and separately distributed accessory catalogues remain out of scope.

## Executive result

Six registered source/date entries were reconciled against current master data. The Jogger 2026-10-01 commercial matrix gap has since been closed: one special non-metallic paint item and 54 option/package mappings (38 optional, 16 explicitly unavailable) were imported on 2026-11-14.

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

Totals: **70 catalogue price cells**, **54 source-specific price rows**, **16 already represented/reused price cells**, and **509 commercial mappings now present after the Jogger import**. The 54 missing Jogger mappings are excluded from the existing-mapping total.

## Jogger — exact next import scope

The 2026-10-01 official Jogger cennik pages 3–4 supported this matrix across the 12 source-linked configurations; all 54 mappings and the item definition were imported on 2026-11-14:

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
- **Spring:** two prices and ten commercial mappings are specific to MY25 dealer stock. The owner-supplied Library PDF is MY25/effective 2026-03-03. The live official CDN content at the same URL is MY26/effective 2026-02-06, with three candidate price cells. Treat these as distinct binary versions; do not overwrite the MY25 source or import MY26 prices before acquiring and hashing the current PDF.

## Validation and exclusions

- Source identities, dates, registered hashes, source-linked configuration counts and master mapping counts were checked against current repository files.
- No brochure or configurator evidence was used.
- No source omission was interpreted as unavailability.
- Existing history and correct master observations are retained; no duplicate price observations are proposed.

## Next package

Completed in package `jogger_price_list_20261001_commercial_matrix_import_20261114_001`: one special non-metallic paint item and 54 dated mappings were added. Next cennik-only package: capture and hash the live Spring MY26 PDF as a distinct source version, preserve the MY25 Library source, and reconcile the three candidate price cells. The Bigster 2026-11-02 PDF binary archive gap remains after that.


## Spring — mutable CDN URL and source-version identity

The owner-supplied Library PDF `2e0588c888.pdf` (1,419,041 bytes) is the MY25 stock document: its first page says `ROCZNIK 2025` and `Cennik obowiązuje od 03.03.2026`. The registered source record `src_pl_spring_price_my25_stock_20260303` and its recorded SHA-256 remain MY25-bounded.

The same official CDN URL (https://cdn.group.renault.com/dac/pl/pdf/cenniki/spring-price.pdf.asset.pdf/2e0588c888.pdf) currently returns a different PDF titled `S2E_PY26_06.02.2026`: its first page says `ROCZNIK 2026` and `Cennik obowiązuje od 06.02.2026`. It presents three candidate price cells: Essential Electric 70 — 73,500 PLN; Expression Electric 70 — 81,500 PLN; Extreme Electric 100 — 85,900 PLN. The table heading/footer call these catalogue prices, while the row labels read `Cena promocyjna`; retain both source contexts.

The current MY26 PDF binary has not yet been captured into the repository and its SHA-256 is therefore unknown. Do not overwrite the MY25 source record, invent a hash, or import MY26 prices until the exact current bytes are acquired and archived as a separate source.
