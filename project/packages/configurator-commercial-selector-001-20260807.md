# Configurator Commercial Selector 001

Date: 2026-08-07  
Baseline main: `a109cfab7fc73c7484d79c34c3d6ae1fce43b98f`

## Purpose

Turn the existing source-bounded commercial readiness layer into a real per-configuration `Pakiety i opcje` selector without inventing compatibility rules or replacing the current shortlist/filtering engine.

## Source boundary

The package uses only commercial items already mapped to exact canonical configurations in master data.

It preserves two distinct facts when both exist for the same item and configuration:

- `optional` means the item is a selectable commercial offer with the exact mapped standalone price when known;
- a later `standard` row from an exact saved configuration is selected-state evidence and must not hide the earlier selector offer or its price.

These meanings are merged into one logical UI component. The selected-state observation is shown as evidence, not as a second duplicate choice.

## Behaviour

The selector:

- exposes only package/option rows with exact configuration applicability;
- shows the individual exact mapped price or an explicit unconfirmed-price state;
- preserves exact saved-configuration selected-state evidence separately;
- keeps selections local to each result card;
- shows an arithmetic price preview based on known selected prices;
- never treats an unknown price as zero;
- warns that a multi-choice sum is provisional because dependency, conflict and simultaneous-orderability rules are not represented in the repository;
- performs no compatibility inference;
- remains fully self-contained and offline through the existing embedded pricing module.

## Compatibility boundary

Selecting more than one commercial item does not assert that the items can be ordered together. The UI deliberately does not disable, auto-select, remove or reorder choices based on inferred relationships.

## Tests

Existing unittest coverage is extended without introducing a new `test_*` method. The regression fixture contains an `optional` offer followed by a later `standard` selected-state observation for the same item and verifies that:

- one logical commercial component remains;
- the component is still selectable as `optional`;
- its exact price is preserved;
- selected-state evidence is retained separately.

The canonical discovery baseline remains 1885 tests. Full repository `Quality` remains the merge gate, while the existing selection/export workflows exercise the embedded JavaScript syntax and offline HTML chain.

## Repository impact

Interface/reporting only:

- no master-data mutation;
- no schema change;
- no new source inference;
- no generic dependency/conflict model;
- no change to filtering semantics;
- no change to the deferred Spring retry package.

## Files

- `tools/reporting/commercial_offers.py`
- `tools/reporting/configuration_shortlist_v12_pricing.js`
- `tests/test_configuration_shortlist.py`
- `project/packages/configurator-commercial-selector-001-20260807.md`
- `project/state.json`
- `project/STATE_SUMMARY.md`
