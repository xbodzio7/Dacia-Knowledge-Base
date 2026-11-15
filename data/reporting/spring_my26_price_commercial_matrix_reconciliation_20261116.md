# Spring MY26 2026-02-06 price and commercial matrix reconciliation

**Status:** import contract prepared  
**Source:** `src_pl_spring_price_my26_20260206`  
**Source revision:** 2026-02-06 · Poland · MY26 · 7 pages  
**Binary SHA-256:** `ab36fba1106ca4929c42330df7896cea8fe56e8774353f6cbb5a7a94cfc18055`

## Accepted import contract

- 3 exact catalogue-matrix price cells on printed page 1: Essential Electric 70 — 73,500 PLN; Expression Electric 70 — 81,500 PLN; Extreme Electric 100 — 85,900 PLN.
- 3 Lichen Khaki mappings at 2,300 PLN on page 3.
- 3 FlexiCharger mappings at 1,500 PLN on page 4.
- 1 DC 40 kW option mapping: Expression, 2,750 PLN.
- 3 package mappings: TECHNO / Expression / 3,500 PLN; CITY / Extreme / 1,800 PLN; POWER / Extreme / 3,000 PLN.
- 3 source-to-configuration links and 3 source-to-grade links.

## Critical semantic boundary

The page-1 header/footer identify the matrix as catalogue prices, while each price row is labelled **“Cena promocyjna”**. The import uses the existing `catalog_gross` category but records this exact wording conflict in every price observation. It must not be paraphrased as a confirmed discount, transaction price or unambiguous catalogue price.

## Explicitly deferred / excluded

- The DC 40 kW cell for Extreme is marked **P**. No meaning is assigned; no mapping is created.
- Other page-3 `P` marks for parking sensors/reversing camera are outside this commercial-price package and are not interpreted.
- Page 2 narrative (48 kW / 65 KM / 26.8 kWh) conflicts with page 5 technical data (Electric 70: 52 kW / 70 hp / 24.3 kWh). Neither side is imported.
- Page 6 dimensions are deferred because exact attribute and measurement-basis semantics are not established.
- Page 7 promotion/financing terms are excluded.
- No configurator-derived substitutions or inferences are permitted.

## History and duplicate prevention

All observations are dated 2026-02-06 and source-specific. Existing MY25 stock records, July 2026 configurator prices, August 2026 Essential Khaki price and existing FlexiCharger observations remain unchanged. The three exact active configurations are reused; no new configuration or commercial item definition is created.

## Expected master-data delta

| Table | New rows |
|---|---:|
| `configuration_prices.csv` | 3 |
| `commercial_item_configurations.csv` | 10 |
| `source_configurations.csv` | 3 |
| `source_versions.csv` | 3 |

Detailed candidate dispositions are recorded in the companion JSON. The source's earlier full seven-page review remains authoritative for source identity and page inventory.
