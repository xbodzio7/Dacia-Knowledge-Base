# Spring Standard Equipment Representation Review

**Status:** complete  
**Date:** 2026-08-02  
**Master-data mutations:** 0

## Existing repository patterns

- Direct default colour: `exterior_color` already has **7** configuration values and is the established scalar representation for a source-stated grade colour.
- Standard equipment: `configuration_attribute_availability` contains **4592** standard rows where a compatible canonical equipment attribute exists.
- Commercial `standard` mappings: **4** rows exist, but **0** are non-stock grade-standard precedents; current rows preserve selected equipment in exact stock vehicles.
- `charging_connector_type` has **0** direct values and describes the vehicle connector standard, not a supplied cable.
- No compatible supplied-charging-cable attribute exists.

## Decisions

### Biel Alpejska — existing pattern available

For Spring Essential, add the exact-current direct value:

- `attribute_code`: `exterior_color`
- `value`: `biel alpejska`
- `observation_date`: `2026-08-02`
- `source_code`: `src_pl_spring_commercial_context_20260802`

Then convert only `spring_colour_biel_alpejska__spring_essential_electric70_automatic` to `standard` at **0 PLN**. The scalar records the grade default; the commercial relationship preserves the zero-surcharge palette state.

### Type 2 cable — new representation decision required

Changing the existing commercial mapping from optional to standard is insufficient because its only membership is `charging_connector_type`, whose meaning is the vehicle connector standard. Essential and Extreme are exact-current standard; Expression remains unresolved.

### Home charging cable — new representation decision required

No compatible item or attribute exists. Reusing `charging_connector_type` would conflate the vehicle connector with a separately supplied cable and could not represent Type 2 and home cables simultaneously.

## Architecture boundary

Before either cable is mutated, choose a canonical supplied-cable representation. The review recommends two independent boolean equipment concepts because the cables can coexist and have independent standard/optional states.

## Next package

`spring_biel_alpejska_default_colour_migration_001` will migrate only the exact-current Essential Biel Alpejska default and will leave all charging-cable records untouched.
