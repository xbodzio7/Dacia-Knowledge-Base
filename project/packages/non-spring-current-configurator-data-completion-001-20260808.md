# Non-Spring Current Configurator Data Completion

Date: 2026-08-08  
Package: `non_spring_current_configurator_data_completion_001`  
Primary evidence gap: `CAT-GAP-002`

## Goal

Complete the source-backed current configurator evidence scope for every current Dacia model family other than Spring. Reuse the already completed Sandero/Sandero Stepway package, add current Duster, Jogger and Bigster evidence, and preserve exact scope boundaries instead of filling inaccessible dynamic states by analogy.

## Existing completed scope

PR #621 already completed the current Sandero/Sandero Stepway source scope: 15/15 current grade/powertrain/transmission identities and catalogue prices are verified. Two exact default Design surfaces are reproducibly complete; thirteen remaining exact Design states remain explicitly bounded where the official site does not expose a deterministic target state.

## Duster

The current official Dacia Poland model page exposes four real grade preset configuration links for Essential, Expression, Extreme and Journey. The current generic configurator reproducibly exposes the exact Essential Eco-G 120 state, and same-day official grade preset observations provide current Design and factory-option evidence for Expression, Extreme and Journey without synthesizing links.

The current range contains 16 grade/powertrain surfaces. The canonical configuration registry matches 13 of them. Three current `hybrid-G 150 4x4` grade surfaces are absent from the registry, while fourteen prior-phase Duster configurations remain marked active. This package records that drift but deliberately does not mutate canonical configuration status; the dedicated next package will reconcile it with historical evidence preserved.

## Jogger

The current five-seat and seven-seat official configurators are treated as separate exact scopes. Both Essential Eco-G 120 default states are reproducible with complete visible current colour choices, wheel and upholstery. The repository contains 22 exact Jogger configuration surfaces; non-default Design states are not projected from the default five- or seven-seat palette when the official site does not expose a deterministic target state.

## Bigster

The current official model page exposes real grade preset links for Essential, Expression, Extreme and Journey. The Essential current exact default is reproducibly complete for visible Design choices. Same-day official Journey preset evidence records its visible Design and factory options. Current grade pages preserve the engine inventory for all four grades without transferring Design choices between engines.

## Result

All five current non-Spring families now have an explicit current official configurator/source-completeness scope in the repository:

- Sandero — completed by the preceding focused package;
- Sandero Stepway — completed by the preceding focused package;
- Duster — current source scope captured; canonical registry reconciliation required next;
- Jogger — current source scope captured with five-/seven-seat separation and explicit exact-state boundaries;
- Bigster — current source scope captured with real grade presets and explicit exact-state boundaries.

The current non-Spring scope contains 67 exact configuration surfaces when the current Duster live range replaces the stale Duster registry boundary. Six reproducible exact default Design surfaces are complete: Sandero Essential, Stepway Essential, Duster Essential, Jogger Essential five-seat, Jogger Essential seven-seat and Bigster Essential.

## Files

- `project/sources/dacia-pl-non-spring-current-configurator-scope-20260808.json`
- `data/reporting/non_spring_current_configurator_data_completion_20260808.json`
- `project/packages/non-spring-current-configurator-data-completion-001-20260808.md`
- `project/state.json` and generated `project/STATE_SUMMARY.md` after the source/reporting head passes Quality

## Boundaries

- Spring is intentionally excluded because its current configurator work is already complete;
- no cross-grade, cross-powertrain, cross-transmission or cross-seat projection;
- no selected appearance is promoted to a complete choice catalogue;
- no synthetic configurator deep links;
- no absence is interpreted as unavailability;
- no Duster canonical status is changed in this package;
- historical exact configurator observations remain preserved.

## Closure and next package

This source-completion package is complete when its source/reporting head passes repository Quality. The next package is `duster_current_range_configuration_catalog_reconciliation_001`: reconcile the three current missing hybrid-G 150 4x4 surfaces and the fourteen prior-phase active Duster surfaces before downstream completeness products treat the Duster registry as current.
