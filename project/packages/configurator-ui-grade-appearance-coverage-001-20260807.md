# Configurator UI Grade Appearance Coverage 001

Date: 2026-08-07  
Baseline main: `b913cee3b4fa7517af24860dddb7baf17f36f1c7`

## Purpose

Extend the Dacia-configurator-like UI data layer from six exact default states to all current grade surfaces without weakening evidence boundaries.

The package separates three concepts that the interface must not conflate:

1. **representative exact selected appearance** — one exact official configuration observation for a grade;
2. **grade-page appearance fact** — a current official version-page statement such as a named wheel, upholstery or body-style highlight;
3. **complete choice list** — a source that actually exposes all visible alternatives for the captured scope.

## Coverage

- 6 current model families;
- 21 current grade surfaces;
- 21/21 grades with one representative exact selected wheel and upholstery observation;
- 14/21 grade pages with at least one explicit appearance fact visible in the current official page layer;
- 6 exact current default configurations with complete visible colour choices and prices;
- 2 additional grade surfaces with complete visible grade-design lists already captured: Sandero Journey and Bigster Expression;
- 13 grade surfaces remain selected-only or partial for alternative-choice semantics.

## Evidence used

The package reuses existing repository-normalized exact observations and rechecks current official Dacia Polska pages on 2026-08-07.

Repository inputs:

- `data/reporting/configurator_ui_appearance_catalog_20260807.json`;
- `data/reporting/configurator_ui_current_exact_choices_20260807.csv`;
- `data/reporting/cross_model_configurator_commercial_data.json`;
- `project/sources/dacia-pl-spring-saved-configurations-20260802.json`.

Current official page evidence includes Sandero, Sandero Stepway, Jogger, Duster, Bigster and Spring version/configurator pages.

## UI contract

- A representative saved/exact appearance is never promoted to a grade-wide standard unless a grade-level source independently states it.
- A generic grade-page phrase such as `felgi aluminiowe` remains generic; no wheel design is invented.
- A grade-wide complete Design list may be shown for that grade, but missing prices remain missing.
- A complete exact colour selector may be enabled only for the exact captured configuration scope.
- Omitted alternatives are not interpreted as unavailable.
- Model packshots remain model-level images rather than exact paint/wheel renders.

## CAT-GAP-002

`CAT-GAP-002` remains open. This package improves UI readiness but does not lower the strict exact-colour acceptance criterion for the 81 active configuration surfaces.

## Repository impact

Reporting/integration only:

- no master-data mutation;
- no schema change;
- no new architecture decision;
- no change to the date gate on the New Spring Shop retry.

## Files

- `data/reporting/configurator_ui_grade_appearance_coverage_20260807.json`
- `project/packages/configurator-ui-grade-appearance-coverage-001-20260807.md`
- `project/state.json`
- `project/STATE_SUMMARY.md`
