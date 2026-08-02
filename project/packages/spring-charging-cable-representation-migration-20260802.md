# Spring Charging-Cable Representation Migration

Package ID: `spring_charging_cable_representation_migration_001`

Status: in progress until generated migration output and full Quality are verified

## Goal

Implement the accepted independent representation of the Type 2 cable supplied with the vehicle and the domestic-socket charging cable.

## Bounded changes

- add `type2_charging_cable_supplied` as a boolean Electric System attribute;
- add `domestic_socket_charging_cable` as a separate boolean Electric System attribute;
- add Type 2 `standard` availability for Spring Essential 70, Expression 70 and Extreme 100;
- add domestic-socket cable `optional` availability for Essential 70 and Extreme 100;
- create no domestic-socket row for Expression 70 while its option state remains unresolved;
- preserve every historical commercial item and mapping unchanged.

## Evidence

- Essential exact-current official configurator observation dated 2026-07-31;
- Expression exact saved-configuration PDF `7OO7LQ` dated 2026-08-02;
- Extreme exact saved-configuration PDF `WKAWYV` dated 2026-08-02;
- accepted decision `spring_independent_charging_cable_concepts`.

## Validation

The migration is declarative, idempotent and guarded against semantic collisions. Full repository Quality is required on the final PR head before merge.
