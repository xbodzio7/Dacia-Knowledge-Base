# Configurator UI Appearance Data 001

Date: 2026-08-07

## Goal

Prepare a source-bounded appearance layer for the planned Dacia-configurator-like interface without weakening repository evidence rules.

The package combines:

- the existing 18 exact saved-configuration commercial appearance observations;
- existing exact current Sandero, Sandero Stepway and Spring colour-choice captures;
- fresh official Dacia Polska default-configurator observations for Duster, Jogger and Bigster;
- current grade-page design lists where the complete visible list is exposed;
- the existing official model-packshot layer.

## New exact current default surfaces

Six model-family defaults now have a complete current UI choice capture for colour, wheel and upholstery:

1. Sandero Essential TCe 100 manual;
2. Sandero Stepway Essential TCe 110 manual;
3. Duster Essential Eco-G 120 manual;
4. Jogger Essential Eco-G 120 5-seat manual;
5. Bigster Essential mild hybrid-G 140 manual;
6. Spring Essential electric 70 automatic.

The first two and Spring preserve earlier exact colour evidence and now expose the appearance data in one UI-facing structure. Duster, Jogger and Bigster add newly normalized exact current default choice lists.

## Additional grade-level design evidence

The current static grade pages expose complete visible design lists for:

- Sandero Journey: seven colours, one TAMIA wheel design and one denim upholstery;
- Bigster Expression: five colours, two TERGAN wheel variants and one Denim upholstery.

These rows are explicitly grade-scoped. Prices are not invented where the grade page does not expose them.

## UI semantics

The new catalogue separates evidence scopes so the future interface cannot confuse:

- an exact selectable choice list;
- a grade-level design list;
- one selected appearance from a saved configuration;
- a brochure/model palette;
- a model-level packshot.

Only exact current choice lists may be rendered with exact option prices. Selected-only observations do not become complete palettes.

## Readiness result

The interface can now safely implement:

- model, grade and powertrain selection from canonical master data;
- standard equipment, option and package presentation from existing master data;
- official model-level packshots;
- exact appearance selectors for the six default model surfaces;
- source-bounded grade design selectors where the complete grade list is visible;
- selected/default appearance cards for the 18 saved configurator states.

It must still fall back to selected/default appearance or catalogue context when an exact alternative list is not proven.

## Remaining evidence boundary

`CAT-GAP-002` is intentionally not closed. The strict portfolio target contains 81 active configuration surfaces. Three exact colour-choice surfaces existed before this package and six are represented after the fresh default captures, leaving 75 surfaces without a complete exact current colour list.

The available static retrieval interface does not reproducibly select many non-default target states. The package therefore does not project a default palette across grade, powertrain, transmission, drive or seat count.

This is an evidence-completeness limitation, not an interface-architecture blocker: the UI data contract now carries the completeness/scope state explicitly.

## Master-data delta

None. The package changes reporting/integration artifacts and project state only.

## Files

- `data/reporting/configurator_ui_appearance_catalog_20260807.json`
- `data/reporting/configurator_ui_current_exact_choices_20260807.csv`
- `project/packages/configurator-ui-appearance-data-001-20260807.md`
- `project/state.json`
- `project/STATE_SUMMARY.md`
