# Bigster MY26 price-list import — 2026-11-02

## Source
- Official Dacia Poland PDF: https://cdn.group.renault.com/dac/pl/pdf/cenniki/bigster-price.pdf.asset.pdf/2fe688def9.pdf
- Effective date: 2026-11-02
- Printed document: 8 pages
- Imported scope: printed page 1 catalogue gross price matrix
- SHA-256: not asserted; the Library PDF was not materialized as raw bytes in this session.

## Result
- 1 source registry record added.
- 0 technical/equipment source-to-configuration links added; the 13 price rows carry direct source/configuration keys.
- 13 dated catalogue gross price records added.
- 0 existing records overwritten.
- 0 duplicate new records.

## Imported prices

| Configuration | Catalogue gross price |
|---|---:|
| `bigster_essential_mildhybridg140_4x2_manual` | 101,400 PLN |
| `bigster_expression_mildhybridg140_4x2_manual` | 110,400 PLN |
| `bigster_extreme_mildhybridg140_4x2_manual` | 118,900 PLN |
| `bigster_journey_mildhybridg140_4x2_manual` | 118,500 PLN |
| `bigster_expression_mildhybridg140_4x2_automatic` | 115,600 PLN |
| `bigster_extreme_mildhybridg140_4x2_automatic` | 124,100 PLN |
| `bigster_journey_mildhybridg140_4x2_automatic` | 123,700 PLN |
| `bigster_expression_hybrid155_4x2_automatic` | 124,900 PLN |
| `bigster_extreme_hybrid155_4x2_automatic` | 133,400 PLN |
| `bigster_journey_hybrid155_4x2_automatic` | 133,000 PLN |
| `bigster_expression_tribrid150_4x4_automatic` | 128,900 PLN |
| `bigster_extreme_tribrid150_4x4_automatic` | 137,600 PLN |
| `bigster_journey_tribrid150_4x4_automatic` | 137,200 PLN |

## Reconciliation
All 13 target configurations already existed in the canonical configuration inventory. The 2026-11-02 list repeats the same catalogue amounts as the 2026-10-01 list for these combinations. This import therefore preserves both dated observations and does not supersede or rewrite the October rows.

## Explicit exclusions
- Promotional Rabat 7 000 zł and MFS financing benefits.
- Monthly rental examples.
- Optional equipment/package prices on printed pages 4–5.
- Technical specifications on printed page 6; these require a separate exact source-to-master gap reconciliation.

## Validation contract
The regression test verifies one active source record, 13 exact price records and no technical/equipment provenance links, and 13 exact price rows with the source/date/market/type tuple.
