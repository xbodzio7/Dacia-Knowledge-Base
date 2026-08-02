# Spring Charging-Cable Commercial Semantics Review

Package ID: `spring_charging_cable_commercial_semantics_review_001`

Status: in progress until generated migration output and full Quality are verified

## Goal

Preserve the historical brochure option for the physical Type 2 cable, correct its canonical attribute membership, and add a separate exact-current commercial option for the domestic-socket cable.

## Evidence boundary

- the 2026-02-19 brochure explicitly lists the physical Type 2 cable as an option for Essential, Expression and Extreme;
- current exact MY26 evidence lists the Type 2 cable as standard;
- current exact Essential 70 and Extreme 100 evidence lists the domestic-socket cable as optional at 1500 PLN;
- current Expression domestic-socket option applicability remains unresolved.

## Bounded changes

- preserve `spring_type2_charging_cable_option` and all three brochure-backed mappings unchanged;
- replace only its incorrect `charging_connector_type` membership with `type2_charging_cable_supplied`;
- add `spring_domestic_socket_charging_cable_option`;
- link it to `domestic_socket_charging_cable`;
- add 1500 PLN mappings for Essential 70 and Extreme 100;
- create no Expression mapping.

## Expected data impact

- commercial items: +1;
- commercial-item memberships: +1 net;
- commercial-item configuration mappings: +2;
- total master rows: +3;
- historical Type 2 mappings changed: 0.

## Validation

The migration is declarative and must be idempotent. Full repository Quality is required on the final PR head before merge.
