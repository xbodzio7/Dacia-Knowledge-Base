# Official Configurator Sandero Stepway Configuration Import

Date: 2026-07-23

## Purpose

Convert the first model-specific official Dacia web observation into exact, dated master-data records without transferring equipment, package applicability or prices between unproven powertrain and gearbox states.

Sandero Stepway is the first configuration-level import because the user supplied its official configurator link and the official version pages expose five active Eco-G 120 states with explicit gearbox and catalogue-price combinations.

## Imported source

- normalized snapshot: `project/sources/dacia-pl-sandero-stepway-configurations-20260723.json`;
- source code: `src_pl_sandero_stepway_official_web_configurations_20260723`;
- publisher and market: Dacia Polska, PL;
- observation date: 2026-07-23;
- source volatility: dynamic official web pages.

The snapshot retains the exact version-page, equipment-page and configurator addresses plus the grade codes used for Essential, Expression and Extreme.

## Imported configuration prices

Five exact active Eco-G 120 configurations receive current catalogue-price observations:

- Essential manual: 71,700 PLN;
- Expression manual: 76,400 PLN;
- Expression automatic: 83,300 PLN;
- Extreme manual: 82,500 PLN;
- Extreme automatic: 89,400 PLN.

Financing examples, temporary promotions, dealer-stock prices, accessories and installation charges are excluded.

## Imported equipment evidence

Only the source-visible version highlights are expanded, and only to exact Eco-G powertrain/gearbox configurations printed on the same official version page.

The package creates 24 dated `standard` observations. Six configuration/attribute pairs were not previously covered:

- longitudinal roof rails and My Safety for Essential manual;
- front fog lights and modular roof rails for Expression manual;
- front fog lights and modular roof rails for Expression automatic.

The remaining observations are dated official-web confirmations of already represented equipment.

## Explicit non-import

The default configurator state shows `pakiet MEDIA DISPLAY` for TCe 110 manual at 1,900 PLN. It is preserved in the normalized snapshot but is not mapped to any Eco-G configuration because the observed page state does not prove that applicability.

No package, option, dependency or exclusion is inferred from another trim, engine or gearbox.

## Deterministic importer

`tools/import_sandero_stepway_official_web_20260723.py` supports `--apply` and `--check`. It verifies the snapshot SHA-256, catalogue relationships, exact powertrain and gearbox labels, boolean equipment attributes, five prices and 24 availability rows before comparing the generated semantic contract with master data.

## Verification

- 709 Python tests;
- 41 master CSV files and 7,669 rows;
- 4,496 equipment-availability observations;
- importer `--check`: PASS;
- CSV, reference, source-hash and SQLite validation: PASS;
- generated shortlist uses the 2026-07-23 Stepway prices as the latest dated catalogue observations.

## Publication

`data-products-v1.4.0` was published from exact merged main commit `85fff3f69cae97de900bf9422f2418de9f8335ee`. The exact release HTML shows all five imported Stepway Eco-G configurations with the dated official prices and source identity. The three public assets were downloaded again and accepted by the independent release verifier.
