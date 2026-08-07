# Configurator UI Commercial Choice Readiness 001

Date: 2026-08-07  
Baseline main: `a35936dab9110429005422817d302776e72ae3fd`

## Purpose

Turn the existing master commercial-option data into an explicit UI contract for the planned Dacia-configurator-like interface.

The repository already contains a substantial option/package layer. The remaining problem is semantic: the interface needs to distinguish an actual selector offer from an exact selected-state observation and must not infer compatibility between several simultaneous selections when no source proves it.

## Coverage

The package inventories the current non-appearance commercial layer:

- 40 commercial items in master;
- 6 Spring exterior-colour items excluded from this selector because appearance is handled by the dedicated appearance contract;
- 34 non-appearance options/packages;
- 189 total commercial-item/configuration rows;
- 171 non-appearance rows;
- 167 selector-offer rows (`availability_status=optional`);
- 4 exact selected-state observation rows for Duster stock configurations;
- 162 selector offers with an explicit price;
- 5 valid Spring selector offers whose source states no amount;
- 88 non-appearance commercial-item attribute memberships describing package contents or standalone-option semantics;
- all 6 current model families represented.

## Model-family coverage

| Family | Items | Selector offers | Priced | Unpriced | Selected-state observations |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sandero + Sandero Stepway | 8 | 38 | 38 | 0 | 0 |
| Duster | 7 | 29 | 29 | 0 | 4 |
| Jogger | 6 | 42 | 42 | 0 | 0 |
| Bigster | 7 | 48 | 48 | 0 | 0 |
| Spring | 6 | 10 | 5 | 5 | 0 |
| **Total** | **34** | **167** | **162** | **5** | **4** |

## UI contract

### Selector offers

The configurator may expose a commercial item as an available option/package only from an explicit `commercial_item_configurations` row whose `availability_status` is `optional`.

The selector must preserve the exact `configuration_code`. No availability may be transferred across grade, powertrain, transmission, drive, seat count, phase or model family.

### Selected-state observations

Four Duster rows with `availability_status=standard` were added from exact stock evidence to preserve that a package was selected on a specific vehicle. They are **not** separate selector offers and must not create duplicate choices.

For a `(commercial_item_code, configuration_code)` pair that has both an optional offer and an exact selected-state observation:

- keep the optional row as the offer;
- retain the standard row as selected-state evidence;
- do not render two commercial choices.

### Prices

A blank `amount` means **unknown / not stated by the source**, never zero.

The five currently unpriced non-appearance offers are:

- Type 2 charging cable — Spring Essential;
- Type 2 charging cable — Spring Expression;
- Type 2 charging cable — Spring Extreme;
- Techno package — Spring Expression;
- DC 40 kW charging option — Spring Expression.

### Package contents

`commercial_item_attributes` is the UI-facing composition source. It may be used to show package contents and the semantic feature represented by a standalone option.

Source wording and specificity must be preserved. A package membership does not automatically create an unconditional scalar configuration value.

### Combination logic

The current master layer does **not** contain a generic pairwise dependency/conflict/orderability graph.

Therefore:

- individually mapped choices are selector-ready;
- arbitrary simultaneous combinations must not be claimed as orderable unless exact evidence or an explicit rule proves the combination;
- a multi-choice final price may be calculated arithmetically only as a **provisional** total unless compatibility is source-verified;
- isolated exact combinations, such as the Duster stock observations, must not be generalized to other configurations.

The existing Duster `duster_techno_1_package` mapping remains intentionally limited to the modeled automatic configuration because the source condition ties ACC availability to an automatic gearbox.

## Appearance boundary

The six Spring exterior-colour commercial items remain in master for provenance and existing data semantics, but they are excluded from this commercial selector contract.

Exterior colours, wheels and upholstery belong to:

- `data/reporting/configurator_ui_appearance_catalog_20260807.json`;
- `data/reporting/configurator_ui_grade_appearance_coverage_20260807.json`.

The UI must not create two competing paint selectors.

## Result

After this package the planned configurator UI can safely implement the **packages/options step** for exact mapped configurations with:

- option/package name;
- individual price when known;
- source-backed contents;
- exact configuration applicability;
- selected-state evidence separated from offer availability.

The remaining commercial blocker for a fully faithful configurator is generic **multi-option compatibility/dependency/conflict logic**, not basic option/package inventory.

## Repository impact

Reporting/integration only:

- no master-data mutation;
- no schema change;
- no architecture decision;
- no change to the date gate on the New Spring Shop retry.

## Files

- `data/reporting/configurator_ui_commercial_choice_readiness_20260807.json`
- `project/packages/configurator-ui-commercial-choice-readiness-001-20260807.md`
- `project/state.json`
- `project/STATE_SUMMARY.md`
