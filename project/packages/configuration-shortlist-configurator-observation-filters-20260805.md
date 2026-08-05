# Configuration Shortlist Configurator Observation Filters

## Package

- Package ID: `configuration_shortlist_configurator_observation_filters_001`
- Date: 2026-08-05
- Kind: `user_interface_data_integration`
- Status: complete

## Goal

Expose the exact producer-export observations from the 2026-08-04 configurator bundle in the interactive configuration shortlist without promoting saved selections into an availability catalogue.

## Delivered

- validates and joins all 18 commercial, standard-equipment and canonical identity records;
- keeps direct-current and phase-qualified mappings explicit;
- transports the joined observation only inside the interactive catalogue and strips it before commercial price rendering;
- adds a separate, collapsed `Dane potwierdzone konfiguracją producenta` filter section;
- filters by exact configurator confirmation, selected colour, selected wheels, selected upholstery and preserved standard-equipment source lines;
- shows the saved configuration code, observation date, source phase, selected values and exact standard-equipment evidence on matching cards;
- preserves offline operation and session filter state;
- excludes the technical observation transport record from commercial offer exports;
- updates selection and release interface contracts from the equipment-group marker `v1_7` to `v1_8`.

## Evidence boundary

The controls describe only the 18 saved configurations observed on 2026-08-04. They do not state that another colour, wheel, upholstery or equipment item is available or unavailable for a configuration. Wrapped PDF source lines remain unjoined exact evidence.

## Verification

Focused contract coverage checks:

- 18 canonical observation joins;
- 1355 preserved standard-equipment source lines;
- no cross-phase promotion;
- no observation leakage into commercial exports;
- exact browser matching semantics and required user-facing boundary text;
- selection-export and release contracts recognize the new `v1_8` enhancement marker.

Full repository quality is required on the final Pull Request head before merge.

## Manifest

- `CHANGELOG.md`
- `README.md`
- `project/ROADMAP.md`
- `project/SESSION_STATE.md`
- `project/STATE_SUMMARY.md`
- `project/packages/configuration-shortlist-configurator-observation-filters-20260805.md`
- `project/state.json`
- `tests/test_configuration_selection_export.py`
- `tests/test_configuration_shortlist_configurator_observation_filters.py`
- `tests/test_data_product_release.py`
- `tools/reporting/commercial_offers.py`
- `tools/reporting/configuration_shortlist_equipment_groups.css`
- `tools/reporting/configuration_shortlist_equipment_groups.js`
