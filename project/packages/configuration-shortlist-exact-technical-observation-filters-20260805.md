# Configuration Shortlist Exact Technical Observation Filters

## Package

- Package ID: `configuration_shortlist_exact_technical_observation_filters_001`
- Date: 2026-08-05
- Kind: `user_interface_data_integration`
- Status: complete

## Goal

Expose the completed exact technical-data observations from the 2026-08-04 configurator bundle in the interactive configuration shortlist without parsing source lines into canonical attributes or promoting one saved state into another configuration.

## Delivered

- makes `cross_model_configurator_technical_data.json` the fourth required member of the exact saved-configurator observation bundle;
- fails closed when commercial, standard-equipment, technical-data and identity-closure reports differ by source code, observation date or exact configuration-code set;
- joins 18 exact technical observations containing 162 category blocks and 349 preserved source lines;
- carries grouped technical categories, a flat exact technical source-line list and source-page provenance inside the transport-only observation object;
- adds a searchable multi-select filter for exact technical source lines;
- shows grouped exact technical evidence on each matching result card;
- preserves existing confirmation, colour, wheel, upholstery and standard-equipment filter semantics;
- keeps the transport-only observation out of commercial exports;
- adds a release-integration layer that verifies exact technical counts, HTML markers, deterministic archive rewriting and manifest boundaries.

## Evidence boundary

Technical lines remain literal saved-state evidence. They are not parsed into semantic key-value pairs, promoted to master data, transferred between model families, source phases, grades, powertrains, transmissions or seat counts, or interpreted as a catalogue of other available parameters.

The options, packages and accessories boundary remains unchanged: the 18 saved PDFs contain zero exact entries and no availability, compatibility or price is inferred.

## Verification

Focused contract coverage checks:

- 18 joined exact saved states;
- 162 preserved technical category blocks;
- 349 preserved technical source lines;
- mandatory four-report bundle completeness;
- exact browser matching for technical source lines;
- unchanged matching behavior when the technical criterion is absent;
- no semantic technical-line coercion;
- release manifest and shortlist HTML integration markers;
- no observation leakage into commercial exports.

The complete required CI matrix must pass on the final Pull Request head before merge.

## Manifest

- `data/reporting/cross_model_configurator_technical_data.json`
- `project/STATE_SUMMARY.md`
- `project/packages/configuration-shortlist-exact-technical-observation-filters-20260805.md`
- `project/state.json`
- `tests/test_configuration_selection_export.py`
- `tests/test_configuration_shortlist_exact_technical_observation_filters.py`
- `tests/test_data_product_release.py`
- `tools/data_product_release.py`
- `tools/reporting/commercial_offers.py`
- `tools/reporting/configuration_shortlist_equipment_groups.js`
- `tools/reporting/configuration_shortlist_technical_observation_release_integration.py`

## Next package

`data_products_v1_18_0_release_preparation_001` will build and verify a reproducible v1.18.0 release candidate from the completed exact technical-observation integration, stopping before public tag or release creation.
