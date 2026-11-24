# Striker MY26 2026-11-02 Priced Options and Packages Matrix

**Package:** `striker_my26_priced_options_packages_matrix_20261124_001`  
**Source:** `src_pl_striker_price_my26_20261102`  
**Archived PDF:** `PDF/Cenniki/striker-price.pdf`  
**SHA-256:** `d9e1e874ceaf2b65faf37650ad7be4b9a7c9710ee1d09cbdee5856c286e62d35`  
**Evidence:** printed page 5; panoramic-roof standard state cross-checked on page 4.

## Result

Added **11 commercial items and 121 dated mappings** across all 11 exact source-linked configurations.

| Status | Count |
|---|---:|
| `optional` | 60 |
| `standard` | 3 |
| `not_available` | 51 |
| `unknown` (literal P) | 7 |
| **Total** | **121** |

## Exact price matrix

| Item | Essential | Expression | Extreme | Journey |
|---|---:|---:|---:|---:|
| Lakier metalizowany | 3,100 PLN | 3,100 PLN | 3,100 PLN | 3,100 PLN |
| Opony całoroczne 18″ | — | — | 1,000 PLN | 1,000 PLN |
| Aluminiowe obręcze kół 19″ | — | — | 1,200 PLN | 1,200 PLN |
| Nieotwierany panoramiczny szklany dach | — | — | standard | 4,300 PLN |
| Podgrzewane dysze spryskiwaczy i szyba przednia | — | P | P | 1,000 PLN |
| Pakiet Zimowy | — | 1,200 PLN | 1,200 PLN | — |
| Pakiet Zimowy Plus | — | 2,300 PLN | 2,300 PLN | — |
| Pakiet Techno | — | 1,300 PLN | — | — |
| Pakiet Techno 2 | — | — | 1,300 PLN | — |
| Pakiet City | — | 2,200 PLN | — | — |
| Pakiet City 2 | — | — | 2,200 PLN | 2,200 PLN |

Dashes are `not_available`. The roof is `standard` in Extreme because both the equipment matrix and price table mark it ●.

## P-marker boundary

The heated washer nozzles/windscreen row has literal `P` markers in Expression and Extreme. Seven configuration mappings are stored as `unknown`; the marker is preserved in notes. No inference is made about package membership or standalone availability. Journey has an explicit 1,000 PLN price; Essential has a dash.

## Controls

- Verify source registry identity, archive path, SHA-256, size, capture manifest, sidecar, eight-page count, four grade links, 11 configuration links and 11 catalogue-price rows.
- Map only the 11 exact source-linked configurations; do not synthesize configurations from blank price cells.
- Preserve previous commercial rows and append new IDs.
- No package-component attributes, equipment, technical data, promotions or finance offers are imported.

## Reproducible artifacts

- `data/imports/striker_commercial_items_20261102.csv`
- `data/imports/striker_commercial_item_configurations_20261102.csv`
- `tools/import_striker_price_list_commercial_matrix_20261102.py`
- `tests/test_striker_price_list_commercial_matrix_20261102.py`
- `data/reporting/striker_my26_priced_options_packages_matrix_20261124_001.json`

Superseded by: striker_my26_matrix_marker_semantics_correction_20261124_001

Report ID: striker_my26_priced_options_packages_matrix_20261124_001
Generated: 2026-11-24T19:37:00+01:00
Analysed commit: 99df129aed048b4f1ac2c58c19084143f1ebfe15
Status: historical
Scope: Official Polish Striker MY26 cennik effective 2026-11-02; printed option/package matrix on page 5; 11 exact source-linked configurations.
