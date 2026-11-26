# Spring Saved-State Artifact Intake

**Status:** complete  
**Date:** 2026-08-02  
**Master-data mutation:** one normalized source registration only

## Exact artifacts

Two official Dacia Polska saved-configuration PDFs were supplied and hash-verified:

- Spring Expression 70 MY26.b, configuration `7OO7LQ`, catalogue price 81,500 PLN;
- Spring Extreme 100 MY26.b, configuration `WKAWYV`, catalogue price 85,900 PLN.

The available GitHub connector cannot write local binary files. The normalized source retains each original file name, SHA-256 digest, byte size, page count and saved-state reference so that a later binary archive can be matched exactly.

## Charging-cable result

Both PDFs list the Type 2 charging cable under standard battery-and-charging equipment. This independently resolves the Expression state and confirms the Extreme state.

The Expression PDF does not list a domestic-socket charging cable. That omission is not evidence of `not_available`, because the PDF describes the selected configuration and its standard equipment rather than every unselected option.

## Architecture decision

The repository will represent two independent boolean equipment concepts:

1. `type2_charging_cable_supplied`;
2. `domestic_socket_charging_cable`.

Both will use configuration-level equipment availability. They must not be collapsed into `charging_connector_type` or one overloaded commercial item.

## Evidence matrix

- Essential Electric 70: Type 2 standard; domestic cable optional at 1,500 PLN.
- Expression Electric 70: Type 2 standard; domestic cable unresolved.
- Extreme Electric 100: Type 2 standard; domestic cable optional at 1,500 PLN.

## Data boundary

No attributes, availability records, configuration values or commercial mappings are changed by this package. Historical brochure-backed commercial records remain unchanged.

## Next package

`spring_charging_cable_representation_migration_001` will implement the two canonical concepts and import only the exact-current availability supported by the evidence matrix.
