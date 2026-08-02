# Spring Charging-Cable Commercial Semantics Review

**Status:** complete  
**Date:** 2026-08-02  
**Master-data changes:** none

## Result

The historical February brochure item `spring_type2_charging_cable_option` genuinely represents a physical Type 2 cable. Its three option mappings remain valid historical observations and must not be rewritten.

Its current membership in `charging_connector_type` is semantically incorrect. The accepted target membership is `type2_charging_cable_supplied`.

A separate current commercial item is required for the domestic-socket cable:

- Essential electric 70: optional, 1500 PLN;
- Extreme electric 100: optional, 1500 PLN;
- Expression electric 70: unresolved, no mapping authorized.

## Data impact

This review changes **0 master rows**. It authorizes a later bounded migration with a net increase of three rows: one commercial item, one membership and two configuration mappings, while preserving all three historical Type 2 mappings.

## Next package

`spring_charging_cable_commercial_semantics_migration_001` will materialize the accepted plan when a safe self-verifying CSV execution path is available.
