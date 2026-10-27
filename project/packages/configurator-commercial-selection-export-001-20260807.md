# Configurator Commercial Selection Export 001

Date: 2026-08-07  
Baseline main: `0e13365869641b832c86ec36ab64f73b75cbae18`

## Purpose

Make explicit step-7 package/option choices reproducible in the existing JSON selection export without changing the meaning of selected configuration codes, the TXT export or the comparison-bundle consumer contract.

## Export contract

The existing `interactive_configuration_selection` payload remains version 1. The package adds an optional `commercial_selection` object to an exported configuration only when the user explicitly selected at least one mapped commercial item for that exact configuration.

When no commercial choice is selected, the configuration result remains structurally unchanged with respect to all existing fields and no empty commercial object is emitted.

## Commercial selection payload

For an explicit selection the export records:

- deterministic `selected_item_codes`, normalized against commercial offers actually mapped to the exact configuration;
- the selected item name, kind, confirmed amount/currency/date/source, mapped equipment codes and exact selected-state provenance when available;
- review metadata for source-bounded unknown-price states;
- a `price_preview` containing base amount, known surcharge, arithmetic total, completeness, unknown item codes and the multi-choice compatibility warning state;
- `compatibility_inference_performed: false` explicitly.

Unknown or duplicated submitted commercial codes are ignored by normalization and cannot create synthetic export items.

## Browser state

The selection-export layer keeps its own configuration-scoped commercial-selection map by observing `[data-commercial-choice]` changes in capture phase. Capture occurs before the commercial selector rerenders its panel, so the state survives result rerenders and can be exported even after the visible controls are rebuilt.

Only configurations actually selected for JSON export contribute commercial-selection data. Commercial choices do not change the selected configuration list.

## Compatibility

- TXT code export remains unchanged.
- JSON with no commercial choices remains semantically identical to the previous contract.
- the existing comparison-bundle parser continues to consume configuration codes and ignores the additive commercial metadata;
- no import or automatic restoration contract is introduced by this package;
- no dependency, conflict or simultaneous-orderability inference is introduced.

## Tests

Existing methods in `tests/test_configuration_selection_export.py` are extended; no new discovered test method is added.

Coverage verifies:

- exports without commercial choices omit `commercial_selection`;
- an explicit `nav_package` selection is normalized despite duplicate/unknown submitted codes;
- selected-state provenance and the 1200 PLN surcharge are preserved;
- the arithmetic preview is 70000 + 1200 = 71200 PLN;
- `compatibility_inference_performed` remains false;
- the existing comparison-bundle parser consumes an extended JSON payload successfully;
- the embedded offline HTML contains the new export contract.

The canonical discovered unittest baseline remains 1885.

## Repository impact

Interface/export only:

- no master-data mutation;
- no schema migration;
- no change to TXT configuration-code export;
- no generic commercial compatibility inference;
- no change to exact appearance semantics;
- no change to the deferred Spring retry package.

## Files

- `tools/reporting/configuration_shortlist_selection.js`
- `tests/test_configuration_selection_export.py`
- `project/packages/configurator-commercial-selection-export-001-20260807.md`
- `project/state.json`
- `project/STATE_SUMMARY.md`
