# Sandero and Sandero Stepway Configurator Data Completion

Date: 2026-08-08  
Package: `sandero_stepway_configurator_data_completion_001`  
Gap: `CAT-GAP-002`

## Goal

Complete the source-backed current configurator scope for Sandero and Sandero Stepway before changing the configurator-choice interface. The package must distinguish genuinely complete exact choices from source-blocked states instead of filling missing Design data by analogy.

## Current inventory result

All 15 active exact grade/powertrain/transmission surfaces are reconfirmed from the current Polish Dacia grade pages together with catalogue prices:

- Sandero Essential: 1 surface;
- Sandero Expression: 3 surfaces;
- Sandero Journey: 3 surfaces;
- Sandero Stepway Essential: 2 surfaces;
- Sandero Stepway Expression: 3 surfaces;
- Sandero Stepway Extreme: 3 surfaces.

Inventory and current catalogue-price coverage is therefore 15/15 for this focused scope.

## Design result

Two exact surfaces have reproducible complete current Design choice capture:

- `sandero_iii_essential_tce100_manual`;
- `sandero_stepway_iii_essential_tce110_manual`.

The remaining 13 exact Design surfaces are explicitly source-blocked. Current accessible official pages do not expose deterministic target-state Design panels for them. Sandero Journey exposes a complete visible grade-level Design list, but that list is not promoted to exact TCe/Eco-G manual/automatic price catalogues.

This is a deliberate completeness boundary: 15/15 current configurations are known and priced, while exact Design catalogue coverage remains 2/15.

## Historical user-supplied context

`Archiwum/conversations/Dacia.htm` confirms that the project originally received five Eco-G 120 configuration PDFs covering Sandero Expression, Sandero Journey, Stepway Essential, Stepway Expression automatic and Stepway Extreme automatic. Their standalone PDF bytes are not preserved in the repository, so filenames are treated only as historical provenance context. No Design choice, price or configuration code is reconstructed from a filename.

Already assimilated canonical observations from earlier work remain unchanged.

## Files

- `project/sources/dacia-pl-sandero-stepway-current-configurator-scope-20260808.json`
- `data/reporting/sandero_stepway_configurator_data_completion_20260808.json`
- `project/packages/sandero-stepway-configurator-data-completion-001-20260808.md`
- `project/state.json`
- `project/STATE_SUMMARY.md`

## Boundaries

- no `data/master` mutation;
- no cross-grade, cross-powertrain or cross-transmission projection;
- no selected appearance promoted to a catalogue;
- no grade-level Design list promoted to exact configuration choices;
- no synthetic configurator deep links;
- no source fact reconstructed from an archive filename;
- `CAT-GAP-002` remains open for the 13 exact source-blocked Design surfaces.

## Closure

The package is complete because all reproducible source channels for the focused Sandero/Stepway current scope have been exhausted and the remaining evidence limits are explicit. Source-blocked does not mean unknown data should be fabricated.

The next package changes the interface so it can present this distinction correctly: real selectable choices where exact choice evidence exists, grade-level information where only grade scope exists, selected-only observations where appropriate, and an explicit source-limited state otherwise.
