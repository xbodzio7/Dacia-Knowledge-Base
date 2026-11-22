# Striker MY26 2026-11-02 catalogue price import

**Package ID:** `striker_my26_catalogue_price_import_20261122_001`  
**Source:** `src_pl_striker_price_my26_20261102`  
**PDF:** `PDF/Cenniki/striker-price.pdf`  
**SHA-256:** `d9e1e874ceaf2b65faf37650ad7be4b9a7c9710ee1d09cbdee5856c286e62d35`

## Scope

Import the 11 non-empty page-1 catalogue price cells from the official Polish Striker MY26 price list effective 2026-11-02. The exact page-1 matrix was read from the owner-supplied original PDF. Transmission classification was cross-checked against the technical table on page 5.

## Imported price matrix

| Powertrain | Grade | Catalogue price |
|---|---|---:|
| mild hybrid-G 140 4x2 manual | Essential | 92,900 PLN |
| mild hybrid-G 140 4x2 manual | Expression | 99,900 PLN |
| mild hybrid-G 140 auto 4x2 | Expression | 106,900 PLN |
| mild hybrid-G 140 auto 4x2 | Extreme | 115,500 PLN |
| mild hybrid-G 140 auto 4x2 | Journey | 115,500 PLN |
| hybrid 155 4x2 | Expression | 113,000 PLN |
| hybrid 155 4x2 | Extreme | 121,500 PLN |
| hybrid 155 4x2 | Journey | 121,500 PLN |
| hybrid 150 4x4 | Expression | 120,900 PLN |
| hybrid 150 4x4 | Extreme | 129,500 PLN |
| hybrid 150 4x4 | Journey | 129,500 PLN |

## Transmission evidence

Page 5 confirms:
- mild hybrid-G 140 4x2 — 6-speed manual;
- mild hybrid-G 140 auto 4x2 — 6-speed dual-clutch automatic;
- hybrid 155 4x2 — Multi-mode automatic;
- hybrid 150 4x4 — 6-speed dual-clutch automatic.

The 11 configuration rows are the exact non-empty grade/powertrain cells from page 1. No empty cells or unlisted combinations were converted into configurations.

## Changes

- Added four Striker grade/version rows.
- Added 11 exact active Striker configurations.
- Added one source-to-model relationship, four source-to-grade relationships and 11 source-to-configuration relationships.
- Added 11 dated `catalog_gross` price observations.
- Added the source-specific import CSV and a regression test covering all 11 amounts, dates, grades, powertrains and source links.

## Explicit exclusions

No dealer promotions, financing/lease values, option prices, package prices, equipment availability or further technical observations are included. These remain separate source-backed packages.


## Comparison scope compatibility

Added an explicit price-only comparison scope for all 11 active Striker configurations. It declares no technical slots or equipment attributes yet, so the repository can include Striker in comparison/export tooling without implying that technical or equipment data have been assimilated. Future Striker source-backed packages can extend the scope when their evidence is reviewed.
