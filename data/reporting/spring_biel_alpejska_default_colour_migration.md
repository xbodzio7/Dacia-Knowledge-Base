# Spring Essential Biel Alpejska Default Colour Migration

**Status:** complete  
**Date:** 2026-08-02

## Direct default-colour value

- Configuration: `spring_essential_electric70_automatic`
- Attribute: `exterior_color`
- Value: **biel alpejska**
- Observation date: `2026-08-02`
- Source: `src_pl_spring_commercial_context_20260802`

The direct scalar records the exact-current grade default independently from the commercial palette relationship.

## Commercial relationship

`spring_colour_biel_alpejska__spring_essential_electric70_automatic` is now:

- availability: `standard`
- surcharge: **0 PLN**
- price date: `2026-08-02`
- source: `src_pl_spring_commercial_context_20260802`

## Preserved boundaries

- Expression Biel Alpejska remains an unresolved optional palette relationship;
- Extreme Biel Alpejska remains an unresolved optional palette relationship;
- all three Type 2 mappings remain unchanged;
- no home-cable item, charging attribute or cable mapping is added.

## Master-data delta

- configuration values added: 1;
- commercial mappings updated: 1;
- net master-row increase: 1;
- attributes and commercial items added: 0.

## Next package

`spring_supplied_charging_cable_model_decision_001` must record the supplied-cable architecture decision before any charging-cable mutation.
