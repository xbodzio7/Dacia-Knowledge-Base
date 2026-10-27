# Sandero and Stepway exact default colour captures

Date: 2026-08-06  
Gap: `CAT-GAP-002`  
Source commit: `1881e0db0eeb796c00a1616d93df8efc40e7701b`

## Goal

Begin the bounded configurator phase only after exhausting the current brochures, model price list and version pages. Capture a surface only when the exact version, engine and transmission are visible together with the complete colour list and prices.

## Exact results

### Sandero Essential TCe 100 manual

- biel alpejska — 0 PLN;
- niebieski iron — 2500 PLN;
- szary schiste — 2500 PLN.

The visible configurator identifies the state as `NOWE SANDERO essential TCe 100 F.2` and reports three colours.

### Sandero Stepway Essential TCe 110 manual

- biel alpejska — 0 PLN;
- szary schiste — 2500 PLN;
- czarna perła — 2500 PLN.

The visible configurator identifies the state as `NOWE SANDERO STEPWAY essential stepway TCe 110 f.2` and reports three colours.

## Version-page review

All six current grade pages were reviewed before using the configurator.

- Sandero Essential exposes TCe 100 and a complete three-colour grade list.
- Sandero Expression exposes TCe 100, Eco-G 120 manual and Eco-G 120 automatic, but its dynamic Design colour panel was not exposed by the accessible page text.
- Sandero Journey exposes the same three powertrain/transmission states and a seven-colour grade list, but not exact engine-specific colour prices.
- Stepway Essential exposes TCe 110 and Eco-G 120 manual.
- Stepway Expression and Extreme expose TCe 110, Eco-G 120 manual and Eco-G 120 automatic.
- The three Stepway grade pages did not expose their dynamic Design colour lists in the accessible page text.

## Access boundary

The version-page configuration actions did not expose a deterministic public target-state URL for the thirteen remaining configurations. The accessible configuration shell returned the generic default state. No URL was synthesized and no default palette was relabelled as another grade, engine or transmission.

This is an evidence limitation, not evidence that the remaining configurations share or do not share a palette.

## Result

- focused active Sandero and Stepway surfaces: 15;
- complete exact colour choice-list surfaces before the package: 0;
- complete exact surfaces after the package: 2;
- exact colour rows: 6;
- remaining focused surfaces: 13;
- `CAT-GAP-002` remains open.

## Files

- `data/reporting/sandero_stepway_exact_default_colour_choice_capture_20260806.json`
- `data/reporting/sandero_stepway_exact_default_colour_choice_capture_20260806.csv`
- `data/reporting/sandero_stepway_colour_capture_access_review_20260806.json`
- `data/reporting/cross_model_colour_exact_choice_progress_overlay_20260806.json`

## Boundaries

- no master-data mutation;
- no palette projection between engines or transmissions;
- no unavailable state inferred from absence;
- no grade-level colour list promoted to an exact engine price list;
- no saved selected colour promoted to a full palette;
- no synthetic deep link or hidden-state assumption.

## Next step

Obtain official saved-configuration PDFs, public `conf` URLs or another repeatable official browser capture for the thirteen exact states. Each capture must show the target version, engine, transmission, full visible colour list and price state.
