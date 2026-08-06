# Cross-model Non-configurator Catalogue Coverage Matrix

Date: 2026-08-06

## Goal

Create one auditable coverage layer for the six active Polish Dacia model families and seven catalogue domains:

- exterior colours;
- wheels and wheel covers;
- upholstery and interior trim;
- standard equipment;
- standalone options;
- option packages;
- dealer accessories.

The package separates verified source coverage from global live-configurator completeness. It does not promote selected saved-state observations into complete model catalogues.

## Result

- 6 model families;
- 7 catalogue domains;
- 42 matrix cells;
- 20 explicit residual gaps;
- 13 gaps may use a bounded exact-state configurator fallback after document review;
- 7 gaps, mainly accessory-reference and document-conflict work, explicitly forbid configurator-based resolution.

Coverage status counts:

- `partial_verified`: 18;
- `complete_for_captured_states`: 5;
- `partial_exact_current_state`: 3;
- `source_registered_not_reconciled`: 10;
- `partial_reconciled`: 6.

`complete_for_captured_states` means complete only for the exact saved states named by the source. It is not a claim that every current live configuration has been captured.

## Evidence layers

The matrix uses the following order:

1. current official model brochure;
2. current official model price list;
3. current official accessory catalogue;
4. current official accessory price list;
5. official model page;
6. official Dacia Shop;
7. bounded exact-state configurator capture only for remaining dynamic compatibility dependencies.

The 18 saved configurator PDFs preserve selected commercial values and exact standard-equipment source lines, but contain zero separate option, package or accessory catalogue entries. The Spring work remains a separate partial exact-current layer.

## Important findings

- Colours, wheels and upholstery are verified only as brochure catalogues plus selected exact-state observations; current grade/powertrain compatibility and prices remain incomplete.
- Standard equipment is complete only for five models' captured saved states. Spring has two partial current grade snapshots and no complete exact-current snapshot set.
- Separate standalone-option and package catalogues are absent from the 18 saved-state PDFs. Spring exposes selected current options and packages, but not complete all-grade coverage.
- Bigster and Duster accessory sources are deeply reconciled, but official source conflicts and a non-exhaustive current shop subset remain.
- Jogger, Sandero and Sandero Stepway still depend partly on official 2022 accessory price lists; those prices are historical evidence, not current 2026 prices.
- New Spring has a complete 56-row 2024 price-list extract and current page/shop corroboration, but three promoted concepts lack verified references and rubber-mat references conflict across sources.

## Boundaries

- No master-data mutation.
- No inferred value, recommendation, ranking or source-quality score.
- No cross-model, cross-grade, cross-powertrain, cross-phase or cross-date transfer.
- Absence from one document or shop search is not interpreted as withdrawal or unavailability.
- The configurator is not used to invent accessory part numbers, merge package and component references or settle contradictions between accessory documents.
- No global statement that every colour, wheel, upholstery, option, package or accessory in the current live configurator is complete.

## Files

- `data/reporting/cross_model_nonconfigurator_catalog_coverage_matrix_20260806.json`
- `data/reporting/cross_model_nonconfigurator_catalog_coverage_matrix_20260806.csv`
- `data/reporting/cross_model_nonconfigurator_catalog_gap_backlog_20260806.json`

## Next step

Resolve `CAT-GAP-001` first by registering and validating current Polish model price lists. Then close document-resolvable colour, wheel, upholstery, option and package gaps before opening bounded exact-state configurator captures. Accessory gaps remain in catalogue, shop or dealer evidence channels.
