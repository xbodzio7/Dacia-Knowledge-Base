# Configurator Step Navigation 001

Date: 2026-08-07  
Baseline main: `107be5b74e83f10eb309e5257bfd1db3fe129c98`

## Purpose

Start the real UI transition from the existing offline shortlist into a Dacia-configurator-like flow without replacing the current application, filters, comparison or evidence contracts.

This first UI package is intentionally structural. It adds a visible eight-step navigation skeleton while preserving the existing shortlist as the implementation surface underneath it.

## Flow

The navigation exposes the intended order:

1. Model
2. Wersja
3. Silnik i skrzynia
4. Kolor
5. Koła
6. Tapicerka
7. Pakiety i opcje
8. Podsumowanie

The first three steps navigate to the existing catalogue-backed controls. The final summary navigates to the existing result set. The commercial step navigates to the existing source-mapped commercial information on matching configuration cards.

## Appearance evidence boundary

Colour, wheel and upholstery navigation is deliberately evidence-aware.

The current browser already exposes exact configurator observations for selected configurations. These controls are not promoted to a full choice catalogue. The three appearance steps therefore use the explicit `exact_observation` scope:

- when exact observation controls exist, the navigation labels them as exact observations;
- when such controls do not exist, the step is unavailable and says `brak potwierdzonego wyboru`;
- the package does not infer `exact_current_choice_list` coverage;
- no brochure palette, representative grade state or isolated export observation is converted into a guaranteed configuration choice list.

## Behaviour

The step layer is additive:

- it reads current native shortlist controls but does not replace the filtering engine;
- it scrolls/focuses existing UI surfaces rather than creating parallel selectors;
- it keeps the current model cards, filters, comparison and equipment UI intact;
- it updates navigation status from existing selections and rendered results;
- it remains self-contained and offline because the JavaScript and CSS continue to be embedded by the existing HTML generator chain;
- it adds no commercial dependency/conflict inference and no new source data.

## Tests

The existing selection HTML contract test covers:

- self-contained HTML embedding of the navigation assets;
- exactly eight ordered steps;
- catalogue-choice scope for model/version/powertrain;
- `exact_observation` scope for colour/wheels/upholstery;
- contextual commercial and summary steps;
- source-safe fallback wording;
- responsive CSS contract;
- Node export of the navigation contract when Node.js is available.

This keeps the canonical repository baseline at 1885 discovered tests while preserving the configurator-step assertions inside an already-counted final-wrapper test.

Full repository `Quality` remains the merge gate.

## Repository impact

Interface/reporting only:

- no master-data mutation;
- no schema change;
- no new framework or parallel application;
- no change to the 2026-08-08 date gate on New Spring Shop Retry Cycle 002;
- no generic option compatibility logic.

## Files

- `tools/reporting/configuration_shortlist_equipment_groups.js`
- `tools/reporting/configuration_shortlist_equipment_groups.css`
- `tests/test_configuration_selection_export.py`
- `project/packages/configurator-step-navigation-001-20260807.md`
- `project/state.json`
- `project/STATE_SUMMARY.md`
