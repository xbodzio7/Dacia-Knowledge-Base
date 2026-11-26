# Configurator Summary Step 001

Date: 2026-08-07  
Baseline main: `4b4814b329526777bc3f7ada66204952f62412de`

## Purpose

Turn step 8, `Podsumowanie`, from a navigation destination into a real source-bounded configuration summary while preserving the existing shortlist, filtering, exact-observation and commercial-selector contracts.

## Selection boundary

The shortlist can legitimately contain zero, one or many matching configurations. The summary therefore has three explicit states:

- zero visible configurations: report that no configuration matches and do not substitute another variant;
- more than one visible configuration: require further narrowing and do not choose a vehicle arbitrarily;
- exactly one visible configuration: render the summary for that exact canonical configuration.

This keeps the summary deterministic and prevents a visually convenient result from being mistaken for a user selection.

## Summary content

For one exact visible configuration the summary shows:

- model, version, powertrain and transmission;
- canonical configuration code;
- confirmed catalogue base price when recorded;
- commercial packages/options explicitly selected in step 7;
- an arithmetic price preview using only confirmed selected-item prices;
- explicit unknown-price warnings when a selected commercial item has no confirmed price;
- an explicit compatibility warning when more than one commercial item is selected;
- colour, wheels and upholstery only when an exact saved configurator observation exists for that configuration.

## Evidence boundary

Appearance values remain `exact_observation` evidence. They describe the exact saved manufacturer configuration and are not promoted to a catalogue of other available colours, wheels or upholstery choices.

Commercial selections remain configuration-scoped offers. The summary performs no dependency, conflict or simultaneous-orderability inference.

Equipment filters remain shortlist criteria. They are not automatically treated as ordered commercial options in the final price summary.

## Behaviour

The summary is additive and lives inside the already embedded `configuration_shortlist_v12_pricing.js` module:

- it captures the exact configurator observation snapshot before the later equipment-group layer removes observation pseudo-components from the browser catalogue;
- it reacts to `dkb:results-rendered` and refreshes after the current filtering layers settle;
- it reacts to step-7 commercial checkbox changes;
- it inserts the summary directly above the rendered result cards, so the existing step-8 navigation target remains valid;
- it uses existing offline styles and introduces no external dependency or parallel application.

## Tests

The existing `test_unfiltered_shortlist_is_price_sorted_and_reports_unknowns` test is extended rather than adding another discovered test method.

It verifies the summary contract markers on every run and, when Node.js is available, directly executes `configuratorSummaryMarkup` with:

- a canonical configuration with a confirmed base price;
- two selected commercial options;
- an exact colour/wheel/upholstery observation.

The rendered markup must contain the selected options, the exact appearance value and the multi-option compatibility warning. The canonical discovered unittest baseline therefore remains 1885.

Full repository `Quality` and the existing shortlist/HTML/selection workflows remain the merge gate.

## Repository impact

Interface/reporting only:

- no master-data mutation;
- no schema change;
- no new source inference;
- no automatic vehicle selection;
- no generic commercial compatibility logic;
- no promotion of exact appearance observations to catalogues;
- no change to the deferred Spring retry package.

## Files

- `tools/reporting/configuration_shortlist_v12_pricing.js`
- `tests/test_configuration_shortlist.py`
- `project/packages/configurator-summary-step-001-20260807.md`
- `project/state.json`
- `project/STATE_SUMMARY.md`
