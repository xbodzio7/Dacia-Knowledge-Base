# Spring Charging-Cable Representation Migration

**Status:** complete  
**Date:** 2026-08-02

## Result

The accepted independent-cable architecture is now represented by two boolean canonical attributes:

- `type2_charging_cable_supplied`;
- `domestic_socket_charging_cable`.

Five exact-current configuration-level availability observations were added: Type 2 is standard in Essential 70, Expression 70 and Extreme 100; the domestic-socket cable is optional in Essential 70 and Extreme 100.

No domestic-socket row was created for Expression 70 because its saved-configuration PDF does not enumerate unselected options.

## Data impact

- attributes added: **2**;
- availability records added: **5**;
- net master-row increase: **7**;
- attributes after migration: **387**;
- availability records after migration: **5911**;
- historical commercial records changed: **0**.

## Next package

`spring_charging_cable_commercial_semantics_review_001` will review the historical Spring cable commercial item without rewriting its source-bounded history.
