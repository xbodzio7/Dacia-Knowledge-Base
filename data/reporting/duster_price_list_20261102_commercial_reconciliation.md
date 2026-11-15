# Duster MY26 price-list reconciliation — 2026-11-02

**Source:** [Official Dacia Duster price list, effective 2 November 2026](https://cdn.group.renault.com/dac/pl/pdf/cenniki/duster-price.pdf.asset.pdf/f07ca0a87f.pdf)  
**Source code:** `src_pl_duster_price_my26_20261102`  
**Repository PDF:** `owner_supplied/2026-11-02/f07ca0a87f.pdf`  
**Document length:** 10 pages (verified archived official PDF; SHA-256 `dd6c65d048d7531251967ba39bb8ab6767256882325254e9b3eaafac11d89118`)  
**Scope:** 16 existing configurations, four grades; no brochure data.

## Imported

- Registered the official price list and linked it to all 16 existing configurations and four grades.
- Added two named non-metallic paint options:
  - Biel Alpejska — 0 PLN, 16 configuration mappings.
  - Khaki Lichen — 2,800 PLN, 16 configuration mappings.
- Added the current spare-wheel state for all 16 configurations:
  - 900 PLN for six non-LPG configurations (Expression/Extreme/Journey with mild hybrid 140 or hybrid 155).
  - Explicitly `not_available` for the ten LPG configurations.
- Reconciled Pakiet TECHNO 1:
  - 2,900 PLN for the three automatic Extreme configurations only.
  - Explicitly `not_available` for the other 13 configurations.

**Total:** 2 new commercial items, 2 colour memberships and 64 dated commercial mappings.

## Reused without duplication

| Data group | Existing observations reused | New rows |
|---|---:|---:|
| Catalogue prices (page 1) | 16 | 0 |
| Equipment availability (pages 4–5) | 1,152 | 0 |
| Previously represented technical scalars (page 6) | 391 | 0 |
| Technical value ranges (page 6) | 16 | 0 |

The catalogue prices, equipment matrix and most technical values match the 2026-09-01 observations. The page-6 technical table was visually rechecked against the archived PDF; the earlier text-extraction discrepancy is corrected below.

## Hybrid 155 voltage evidence — corrected visual review

For all three Hybrid 155 configurations:

- Printed page 2 narrative: traction battery 1.4 kWh, **260 V**.
- Printed page 6 technical table: **230 V**.
- Previous 2026-09-01 page-6 technical table: **230 V**.

The page-6 table was visually checked against the exact archived ten-page PDF. The earlier **280 V** reading came from a text-extraction error, not the printed technical table. The registered November source SHA-256 is `dd6c65d048d7531251967ba39bb8ab6767256882325254e9b3eaafac11d89118`. The 260 V narrative and 230 V technical-table statements are retained as separate source contexts. No new voltage observations are warranted; do not import 280 V or overwrite the existing 230 V observations.

## Complete page review

| Printed page | Content | Result |
|---:|---|---|
| 1 | Catalogue price matrix and commercial headlines | All 16 prices match existing observations |
| 2 | Technology and comfort narrative | Reviewed; 260 V statement retained as narrative evidence |
| 3 | Grade equipment summaries | Reviewed; detailed matrix is on pages 4–5 |
| 4–5 | Equipment, options and package matrix | Reconciled; no duplicate availability/package rows |
| 6 | Technical data | Existing values reused; page-6 table states 230 V for all three Hybrid 155 configurations |
| 7 | Accessory presentation and QR links | No prices or exact configuration applicability |
| 8 | Complete winter-wheel accessory list and promotion | Four priced products (1,700 / 1,555 / 1,220 / 1,075 PLN); separate accessory list effective 2026-09-01, not vehicle configuration options |
| 9 | Dimensions diagram | Paired dimensions remain deferred without an exact grade/powertrain crosswalk |
| 10 | Legal and commercial terms | Reviewed; promotions, financing and legal disclosures remain separate from catalogue prices |

## Deferred, without inference

- Metallic paint is printed as 2,800 / 3,000 PLN without identifying the corresponding named paint variants.
- The Hybrid 155 narrative/table voltage distinction (260 V on page 2; 230 V on page 6) is retained as source-context evidence; no configuration-level 260 V or 280 V observation is inferred.
- Winter-wheel products are a separate accessory list, not configuration-option mappings.
- Paired dimensions on page 9 are not mapped to configurations without a reliable crosswalk.
- Promotions, financing and lease terms remain separate from catalogue prices.

No brochure or configurator evidence was used. No master data was changed in this residual review. The 230 V master observations remain unchanged.
