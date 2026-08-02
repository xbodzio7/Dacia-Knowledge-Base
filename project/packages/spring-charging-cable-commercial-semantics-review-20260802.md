# Spring Charging-Cable Commercial Semantics Review

Package ID: `spring_charging_cable_commercial_semantics_review_001`

Status: complete

## Goal

Resolve the source meaning of the historical Type 2 commercial item and define an exact-current domestic-socket commercial representation without changing master data.

## Findings

- the 2026-02-19 brochure genuinely describes a physical Type 2 cable as an option for Essential, Expression and Extreme;
- its current membership in `charging_connector_type` is semantically incorrect;
- the accepted target membership is `type2_charging_cable_supplied`;
- current exact MY26 evidence lists Type 2 as standard;
- current Essential 70 and Extreme 100 evidence lists the separate domestic-socket cable as optional at 1500 PLN;
- current Expression domestic-socket applicability remains unresolved.

## Accepted migration plan

- preserve `spring_type2_charging_cable_option` and all three brochure-backed mappings unchanged;
- replace only its membership with `type2_charging_cable_supplied`;
- add `spring_domestic_socket_charging_cable_option` linked to `domestic_socket_charging_cable`;
- add 1500 PLN mappings for Essential 70 and Extreme 100;
- create no Expression mapping.

## Current data impact

- master rows changed: **0**;
- commercial items changed: **0**;
- commercial memberships changed: **0**;
- commercial mappings changed: **0**.

## Execution boundary

The attempted branch-local workflow was not executed by GitHub. The package therefore records only the verified review and accepted migration plan. It does not claim that any CSV migration occurred.

## Next package

`spring_charging_cable_commercial_semantics_migration_001` will materialize the accepted three-row net change through a safe self-verifying execution path.
