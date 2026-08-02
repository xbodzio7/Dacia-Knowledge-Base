# Spring Standard Equipment Representation Review

Package ID: `spring_standard_equipment_representation_review_001`

Status: complete

## Goal

Review the repository's existing representations for the exact-current Spring Essential default paint, the Type 2 supplied cable and the home charging cable before any further master-data mutation.

## Findings

### Essential Biel Alpejska

The repository already has a canonical pattern for a source-stated default paint: a direct `configuration_attribute_values` row for `exterior_color`. Seven current non-Spring configurations use this pattern, while Spring has no direct exterior-colour value yet.

The safe migration is therefore bounded to:

- add `exterior_color = biel alpejska` for `spring_essential_electric70_automatic` from the exact-current source dated 2026-08-02;
- convert only `spring_colour_biel_alpejska__spring_essential_electric70_automatic` to `standard` at zero surcharge;
- leave the Expression and Extreme palette mappings unchanged.

### Type 2 supplied cable

The current commercial item is linked only to `charging_connector_type`. That attribute describes the vehicle connector standard, not a cable supplied with the vehicle. Changing only the Essential and Extreme mappings from optional to standard would preserve the wrong semantic membership.

### Home charging cable

No compatible commercial item or canonical attribute exists. Reusing `charging_connector_type` would conflate the vehicle connector with a separate supplied cable and would not allow the Type 2 and home cables to coexist.

## Existing pattern counts

- direct `exterior_color` values: 7;
- Spring direct `exterior_color` values: 0;
- standard equipment availability rows: 4592;
- commercial mappings marked `standard`: 4;
- non-stock trim-level standard commercial precedents: 0;
- direct `charging_connector_type` values: 0;
- compatible supplied-cable attributes: 0.

## Master-data delta

None. This is a review-only package.

## Architecture boundary

A canonical representation must be chosen before either cable is mutated. The review recommends separate boolean equipment concepts for the Type 2 cable and the home charging cable because both can coexist and have independent standard or optional states.

## Follow-up

Proceed with `spring_biel_alpejska_default_colour_migration_001`. It requires no new attribute and leaves all charging-cable records untouched.
