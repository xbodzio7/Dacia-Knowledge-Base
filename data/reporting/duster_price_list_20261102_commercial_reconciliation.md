# Duster MY26 price-list reconciliation — 2026-11-02

**Source:** [Official Dacia Duster price list, effective 2 November 2026](https://cdn.group.renault.com/dac/pl/pdf/cenniki/duster-price.pdf.asset.pdf/f07ca0a87f.pdf)  
**Source code:** `src_pl_duster_price_my26_20261102`  
**Scope:** 16 existing configurations, four grades; no brochure data.

## Imported

- Registered the 10-page official price list and linked it to all 16 existing configurations and four grades.
- Added two named non-metallic paint options:
  - Biel Alpejska — 0 PLN, 16 configuration mappings.
  - Khaki Lichen — 2,800 PLN, 16 configuration mappings.
- Added the current spare-wheel state for all 16 configurations:
  - 900 PLN for six non-LPG configurations (Expression/Extreme/Journey with mild hybrid 140 or hybrid 155).
  - Explicitly `not_available` for the ten LPG configurations.
- Reconciled Pakiet TECHNO 1:
  - 2,900 PLN for the three automatic Extreme configurations only.
  - Explicitly `not_available` for the other 13 configurations because the package is listed only for Extreme and includes ACC, which is available only with automatic transmission.

**Total:** 2 new commercial items, 2 colour memberships and 64 dated commercial mappings.

## Reused without duplication

| Data group | Existing observations reused | New rows |
|---|---:|---:|
| Catalogue prices (page 1) | 16 | 0 |
| Equipment availability (pages 3–4) | 1,152 | 0 |
| Technical scalar values (page 6) | 391 | 0 |
| Technical value ranges (page 6) | 16 | 0 |

The page-1 prices and technical table match the existing 2026-09-01 observations. The equipment matrix is unchanged. The cennik renames the 4x4 powertrain to **tribrid 150 4X4**; the existing canonical `hybridg150` configuration family is retained rather than creating duplicate configurations.

## Deferred, without inference

- Metallic paint is printed as **2,800 / 3,000 PLN**, but the document does not identify which named paint variants correspond to the two prices.
- Page 8 lists winter-wheel accessories with part references; these are not configuration option mappings.
- Page 9 shows paired dimensions without a reliable grade/powertrain crosswalk.
- The page-2 narrative says 260 V for the hybrid battery, while the page-6 technical table says 230 V. The existing discrepancy is preserved.

No brochures, configurator data, promotions or financing claims were used.
