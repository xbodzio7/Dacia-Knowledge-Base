# Duster MY26 price-list reconciliation — 2026-11-02

**Source:** [Official Dacia Duster price list, effective 2 November 2026](https://cdn.group.renault.com/dac/pl/pdf/cenniki/duster-price.pdf.asset.pdf/f07ca0a87f.pdf)  
**Source code:** `src_pl_duster_price_my26_20261102`  
**Repository PDF:** `owner_supplied/2026-11-02/f07ca0a87f.pdf`  
**Document length:** 9 pages (the current official URL serves a 9-page PDF)  
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

The catalogue prices, equipment matrix and most technical values match the 2026-09-01 observations. The current page-6 technical table contains one important exception described below.

## Newly identified technical delta — not yet imported

For all three Hybrid 155 configurations:

- Printed page 2 narrative: traction battery 1.4 kWh, **260 V**.
- Printed page 6 technical table: **280 V**.
- Previous 2026-09-01 page-6 technical table: **230 V**.

These are distinct literal source statements and must remain separate. The three current-dated `hybrid_system_voltage=280` observations are identified but not yet materialized. The November source record has no verified SHA-256; the declarative import workflow requires a hash-verified registered source. No historical value has been overwritten.

## Complete page review

| Printed page | Content | Result |
|---:|---|---|
| 1 | Catalogue price matrix and commercial headlines | All 16 prices match existing observations |
| 2 | Technology and comfort narrative | Reviewed; 260 V statement retained as narrative evidence |
| 3 | Grade equipment summaries | Reviewed; detailed matrix is on pages 4–5 |
| 4–5 | Equipment, options and package matrix | Reconciled; no duplicate availability/package rows |
| 6 | Technical data | Existing values reused except the three 280 V table observations pending import |
| 7 | Accessory presentation and QR links | No prices or exact configuration applicability |
| 8 | Complete winter-wheel accessory list and promotion | Four priced products (1,700 / 1,555 / 1,220 / 1,075 PLN); separate accessory list effective 2026-09-01, not vehicle configuration options |
| 9 | Dimensions diagram and legal terms | Paired dimensions remain deferred without an exact grade/powertrain crosswalk |

## Deferred, without inference

- Metallic paint is printed as 2,800 / 3,000 PLN without identifying the corresponding named paint variants.
- The 280 V Hybrid 155 technical-table value requires three dated observations after the registered source has a verified SHA-256.
- Winter-wheel products are a separate accessory list, not configuration-option mappings.
- Paired dimensions on page 9 are not mapped to configurations without a reliable crosswalk.
- Promotions, financing and lease terms remain separate from catalogue prices.

No brochure or configurator evidence was used. No master data was changed in this residual review.
