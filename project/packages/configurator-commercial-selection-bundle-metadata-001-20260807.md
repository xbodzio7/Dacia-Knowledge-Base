# Configurator Commercial Selection Bundle Metadata 001

Date: 2026-08-07  
Baseline main: `c6655cea65f9fbff60b2338bf1b64c98b7980f79`

## Purpose

Preserve explicit step-7 commercial-selection metadata when an `interactive_configuration_selection` JSON file is consumed by the existing configuration comparison bundle.

## Boundary

Configuration selection semantics do not change. `collect_selection()` still deduplicates only canonical configuration codes. Commercial choices are retained per shortlist source report and are not merged across files or used to create, remove or rank configurations.

## Validation

When `commercial_selection` is present on a shortlist result, the parser requires:

- a non-empty unique `selected_item_codes` string list;
- an `items` object list whose item codes exactly match `selected_item_codes` in order;
- a `price_preview` object;
- `compatibility_inference_performed: false`.

Invalid commercial metadata raises `BundleError` instead of being silently trusted.

## Source metadata

Each shortlist source record now preserves:

- `commercial_configuration_count`;
- `commercial_selected_item_count`;
- `commercial_selections`, retaining the exact `commercial_selection` object next to its canonical `configuration_code`.

This keeps source-specific commercial choices reproducible for later reporting without inventing a cross-export merged state.

## Tests

The existing `test_collect_selection_accepts_codes_and_shortlist` method is extended. It verifies preservation of one commercial selection and rejection of a payload claiming compatibility inference. No new discovered unittest method is added; the canonical baseline remains 1885.

## Repository impact

Reporting metadata only:

- no master-data mutation;
- no schema migration;
- no change to selected configuration codes;
- no cross-source commercial merge;
- no compatibility inference;
- no change to the deferred Spring retry package.

## Files

- `tools/reporting/configuration_comparison_bundle.py`
- `tests/test_configuration_comparison_bundle.py`
- `project/packages/configurator-commercial-selection-bundle-metadata-001-20260807.md`
- `project/state.json`
- `project/STATE_SUMMARY.md`
