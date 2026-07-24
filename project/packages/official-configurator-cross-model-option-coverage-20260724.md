# Official Configurator Cross-Model Option Coverage — 2026-07-24

Status: complete

## Goal

Close the misleading partial-coverage gap for the factory shark-fin antenna and power-folding mirrors without turning absent or ambiguous web content into a negative availability claim.

## Imported evidence

The package registers one dated normalized snapshot of nine official Dacia Polska grade-specific equipment pages and expands each factory-equipment statement only to active configurations belonging to that exact version.

It adds:

- 31 exact `shark_fin_antenna` observations across Sandero, Sandero Stepway and Jogger;
- 28 `standard` shark-fin observations;
- three explicit `not_available` observations where the same official page names `antena biczowa` as the factory antenna;
- six newer `standard` observations for `side_mirrors_folding` in Jogger Journey;
- source relationships to three models, nine versions and 31 exact configurations.

The six Jogger Journey records dated 2026-04-01 are retained as historical observations. Reporting selects the newer 2026-07-24 state and therefore shows power-folding mirrors as standard for every active Journey configuration.

## Commercial package boundary

This package does not broaden existing commercial mappings:

- the Sandero and Stepway EASY package remains mapped only to exact configurations proven by the dated price list;
- the Jogger DRIVE package remains mapped to its eight exact Extreme configurations;
- no price or package applicability is inferred from a broad grade page.

## Factory equipment versus accessories

The target attribute describes factory configuration equipment. A separately priced retrofit accessory, installation charge or dealer-stock addition is not converted into `optional` factory availability. Explicit alternate factory equipment can support `not_available`; mere omission cannot.

## Model boundaries

- **Bigster:** current master data already covers both target attributes for all 14 active configurations, so no duplicate observations are added.
- **Duster:** current dynamic grade-page payload does not provide sufficiently stable, exact evidence for both target attributes. No Duster record is added, removed or reclassified; missing states remain unknown.

## Consumer validation focus

In the generated shortlist, selecting the factory shark-fin antenna should retain Sandero Expression/Journey, Stepway Expression/Extreme, Jogger Expression/Extreme/Journey and the already-covered Bigster configurations. Stepway Essential and Jogger Essential should be excluded because their exact official grade pages identify a whip antenna instead. Duster must not be rejected on an invented negative state; its missing factory-option evidence remains unknown and therefore outside the source-complete equipment facet.

Jogger Journey should show power-folding mirrors as standard from the newer 2026-07-24 observation. The older 2026-04-01 negative records remain in history but must not drive the current browser state.

## Determinism

`tools/import_official_cross_model_option_coverage_20260724.py` verifies the exact snapshot SHA-256, active model/version/configuration relationships, boolean attributes, allowed statuses and exact row counts. `--apply` replaces only rows owned by this source code; `--check` reproduces the normalized contract without mutation.

## Verification

- exact snapshot hash and source registration;
- 31 exact factory-antenna observations;
- historical and current Jogger Journey folding-mirror states;
- latest-state selection in the browser catalogue;
- unchanged Bigster coverage;
- explicit Duster non-import;
- unchanged EASY and DRIVE package mappings;
- full repository quality gate and canonical project-state check.
