# Brochure Gear-Specific Performance Context Modeling

Date: 2026-07-26
Status: complete

## Goal

Define the smallest reusable representation for source-backed 80–120 km/h elasticity observations whose meaning depends on a selected forward gear.

## Accepted model

Future gear-qualified observations remain rows in `configuration_attribute_values.csv` and reuse the neutral `elasticity_80_120` attribute. The schema foundation shall add one optional `gear_number` column after `fuel_type_code` and before `value`.

`gear_number` is populated only when the source explicitly identifies one selected forward gear. It stores a canonical positive integer such as `4`, `5` or `6`. An empty field means that no selected-gear qualifier was supplied; it does not mean unknown, all gears, top gear or not applicable.

## Existing dimensions reused

- the 80–120 km/h interval remains part of the attribute meaning;
- LPG or petrol alternatives use the existing `fuel_type_code`;
- five- and seven-seat variants target exact Jogger configurations;
- powertrain and transmission remain properties of the exact target configuration.

## Evidence

- Sandero page 17 distinguishes fourth and fifth gear;
- Sandero Stepway page 17 distinguishes fourth, fifth and sixth gear where stated;
- Jogger page 19 states fourth-gear values separately for five- and seven-seat variants.

## Rejected alternatives

- separate attributes for every gear;
- a one-to-one relation for one scalar qualifier;
- a generic key-value measurement-context table;
- duplicated fuel, passenger-layout, powertrain or transmission fields.

## Scope

This package changes no master schema and imports no elasticity values. The next package implements schema, validation, SQLite, data-dictionary, import-spec and reporting support.
