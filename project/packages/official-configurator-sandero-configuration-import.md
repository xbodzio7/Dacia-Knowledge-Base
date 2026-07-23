# Official Configurator Sandero Configuration Import

Date: 2026-07-23

## Purpose

Convert the official Dacia Poland Sandero version-page observations into exact, dated configuration-level records without transferring package applicability, option prices or equipment states between unproven engines and gearboxes.

The package extends the active catalogue because the official Expression and Journey pages explicitly list Eco-G 120 with both manual and automatic transmissions and provide a catalogue price for every state.

## Imported source

- normalized snapshot: `project/sources/dacia-pl-sandero-configurations-20260723.json`;
- source code: `src_pl_sandero_official_web_configurations_20260723`;
- publisher and market: Dacia, PL;
- observation date: 2026-07-23;
- source volatility: dynamic official web pages.

The snapshot retains the exact version, equipment and configurator addresses, grade codes and explicit non-import decisions.

## Active catalogue extension

Two configurations are added to the active catalogue:

- Expression Eco-G 120 automatic;
- Journey Eco-G 120 automatic.

Together with the two existing manual configurations, Sandero now has four exact official Eco-G 120 states and a new independent automatic comparison scope.

## Imported configuration prices

Four dated catalogue-price observations are imported:

- Expression manual: 68,000 PLN;
- Expression automatic: 74,900 PLN;
- Journey manual: 73,600 PLN;
- Journey automatic: 80,500 PLN.

Financing examples, promotions, accessories, installation charges and dealer-stock prices are excluded.

## Imported equipment evidence

Only the source-visible version highlights are expanded, and only to the exact Eco-G powertrain and gearbox states printed on the same official version page.

The package creates 16 dated `standard` observations: four highlights for each of the four configurations. Absence from the highlight list is not interpreted as `not_available`.

## Explicit non-import

The broad Expression and Journey equipment pages list named packages and other items, but do not prove exact Eco-G manual/automatic applicability and price. The snapshot therefore retains MEDIA NAV, THERMO, MEDIA NAV LIVE, ZIMOWY, EASY and the full-size spare-wheel observations without creating new package mappings for the automatic configurations.

The default visible configurator state is Essential TCe 100 manual. Its zero-price driver-seat-height adjustment and split rear-seat items are retained as observations but are not transferred to Eco-G.

## Reporting scope

`sandero_ecog120_automatic` is added as an independent reporting scope with two configurations and one comparison pair. The release catalogue therefore contains 69 active configurations in 18 independent scopes.

## Deterministic importer

`tools/import_sandero_official_web_20260723.py` supports `--apply` and `--check`. It verifies the snapshot SHA-256, exact trim/powertrain/gearbox states, two newly created configurations, four prices, 16 availability observations and all source relationships before comparing the generated semantic contract with master data.

## Verification

- 716 Python tests;
- 41 master CSV files and 7,699 rows;
- 69 active configurations;
- 18 independent comparison scopes;
- 4,512 equipment-availability observations;
- importer `--check`: PASS;
- CSV, reference, source-hash, project-state and SQLite validation: PASS.

## Publication

`data-products-v1.5.0` was published from exact merged `main` commit `7f325d254b68eb495204c01c075727ee34893e1f`. The release contains 69 active configurations and 18 independent scopes, including the four exact Sandero Eco-G 120 states and the automatic comparison scope. The three public assets were downloaded again and accepted by the independent release verifier.
