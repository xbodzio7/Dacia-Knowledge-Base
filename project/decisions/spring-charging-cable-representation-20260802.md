# Spring Charging-Cable Representation Decision

Decision code: `spring_independent_charging_cable_concepts`

Status: Accepted

Date: 2026-08-02

## Decision

A cable supplied with a vehicle is represented independently from the vehicle's charging-connector standard.

Spring charging equipment requires two separate boolean canonical attributes:

- `type2_charging_cable_supplied`;
- `domestic_socket_charging_cable`.

Their commercial state is represented through `configuration_attribute_availability.csv` at exact configuration level.

## Rationale

The current Spring evidence proves that the Type 2 cable is supplied as standard in Essential, Expression and Extreme. Separate official evidence shows that the domestic-socket cable can be an optional item. Both cables may coexist, so one attribute or one overloaded commercial item cannot preserve their independent meanings.

`charging_connector_type` describes the vehicle interface. It does not state whether a physical cable is supplied and therefore must not be reused for either cable.

A selected-configuration PDF lists the configured vehicle and standard equipment. The absence of an unselected domestic cable from the Expression PDF does not prove that the option is unavailable.

## Exact-current evidence boundary

- `spring_essential_electric70_automatic`: Type 2 `standard`; domestic cable `optional` at 1,500 PLN.
- `spring_expression_electric70_automatic`: Type 2 `standard`; domestic cable unresolved.
- `spring_extreme_electric100_automatic`: Type 2 `standard`; domestic cable `optional` at 1,500 PLN.

## Consequences

- The next package adds the two boolean attributes and imports only supported availability states.
- No `not_available` row is created for the Expression domestic cable.
- Historical brochure-backed commercial item and configuration mappings are retained as historical observations and are not rewritten by this decision.
- Current and historical source meanings remain distinguishable.
