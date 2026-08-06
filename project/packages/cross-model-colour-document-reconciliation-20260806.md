# Cross-model colour document reconciliation

Date: 2026-08-06  
Gap: `CAT-GAP-002`  
Source commit: `7160f7c7b4707da33c2e6ec065104b0b4f97e010`

## Goal

Reconcile every colour fact already present in official Polish brochures, registered current model price lists, exact saved-state commercial observations and the bounded Spring current-context review before using the configurator.

## Result

- 40 named brochure colour rows across six active model families;
- 81 active configuration surfaces retained as the exact closure boundary;
- 19 normalized exact selected-colour observations retained only as selected-state corroboration;
- zero complete exact colour choice-list surfaces;
- five current MY2026 range price lists present in the repository;
- one explicit current MY2026 price-list absence record for Spring;
- `CAT-GAP-002` remains open.

A selected colour in a saved configuration is not treated as a palette. No unavailable state is inferred from absence.

## Model findings

| Model | Named colours | Active configurations | Document result |
|---|---:|---:|---|
| Spring | 6 | 3 | Essential confirms Biel alpejska at 0 PLN and Khaki lichen at 2300 PLN. Expression and Extreme current palettes remain unresolved; the linked price list is MY2025 stock only. |
| Sandero | 7 | 7 | The exact combined July MY2026 PDF is registered. Its named colour table still requires normalization; four Essential exclusions are retained from the brochure. |
| Sandero Stepway | 7 | 8 | The exact combined July MY2026 PDF is registered. Its named colour table still requires normalization; four Essential exclusions are retained from the brochure. |
| Jogger | 7 | 22 | The current July price list proves the printed 0/2700 and 2700/2900 PLN classes for all grades, but not their alignment to colour names. Brochure finish footnotes remain an explicit conflict. |
| Duster | 7 | 27 | The February extract retains Biel Alpejska at 0 PLN, Khaki Lichen at 2700 PLN and the metallic 2700/2900 PLN pair. The current July PDF must be re-extracted before bounded configurator use. |
| Bigster | 6 | 14 | The current July price list supplies the 3000 PLN metallic class and the 1400 PLN two-tone surcharge for Extreme/Journey; black is excluded from two-tone. Named compatibility by powertrain remains unresolved. |

## Identity boundaries

Similar wording is not silently normalized across models or sources. This applies in particular to:

- `Schist`, `Schiste` and `Shiste`;
- `Cedar` and `Cèdre`;
- `Pearl` and `Perła`;
- `Lichen Khaki` and `Khaki lichen`;
- `Biały Glacier` and `Biel Alpejska`.

Each source label remains available for later explicit reconciliation.

## Files

- `data/reporting/cross_model_colour_document_reconciliation_20260806.json`
- `data/reporting/cross_model_colour_document_reconciliation_20260806.csv`
- `data/reporting/cross_model_colour_configurator_fallback_queue_20260806.json`

## Boundaries

- no master-data mutation;
- no configurator use in this package;
- no cross-model, cross-grade, cross-powertrain, cross-transmission, cross-drive, cross-seat or cross-date transfer;
- no selected saved-state colour promoted to a complete choice list;
- no absence interpreted as unavailability;
- no older Spring MY2025 stock price promoted to current MY2026.

## Next step

Complete exact July PDF colour normalization for Sandero, Sandero Stepway and Duster. Then capture bounded current configurator choice lists only for the surfaces that remain unresolved. `CAT-GAP-002` closes only when every active surface satisfies its explicit acceptance criterion.
