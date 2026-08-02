# Spring Charging-Cable Commercial Semantics Decision

Decision code: `spring_charging_cable_commercial_semantics`

Status: Accepted

Date: 2026-08-02

## Findings

The historical item `spring_type2_charging_cable_option` genuinely describes a physical Type 2 cable. The February brochure explicitly presents that cable as an option for Essential, Expression and Extreme. Its current membership in `charging_connector_type` is semantically incorrect because that attribute describes the vehicle interface, not a supplied cable.

Later exact-current evidence supersedes the current commercial state without invalidating the historical observation:

- the Type 2 cable is standard in current Essential 70, Expression 70 and Extreme 100 configurations;
- the domestic-socket cable is a separate optional item at 1500 PLN in exact-current Essential 70 and Extreme 100 states;
- current Expression domestic-socket option applicability remains unresolved.

## Accepted migration plan

A later bounded migration shall:

1. preserve `spring_type2_charging_cable_option` and its three brochure-backed option mappings unchanged;
2. replace only its membership `charging_connector_type` with `type2_charging_cable_supplied`;
3. add `spring_domestic_socket_charging_cable_option` linked to `domestic_socket_charging_cable`;
4. add 1500 PLN optional mappings only for Essential 70 and Extreme 100, dated 2026-08-02 and sourced to `src_pl_spring_commercial_context_20260802`;
5. create no Expression domestic-socket mapping without exact option-state evidence.

## Current package boundary

This review changes no master data. The accepted migration is intentionally deferred to a separate package because the available GitHub execution path did not permit a safe, self-verifying rewrite of the existing CSV tables in this package.
