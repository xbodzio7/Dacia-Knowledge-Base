# Spring Current Grade Snapshot Capture

**Status:** complete  
**Date:** 2026-08-02  
**Master-data mutations:** 0

## Expression electric 70

Snapshot status: `partial_exact_current`.

The exact current Expression page confirms **46** equipment items, including Media Control, manual air conditioning, rear parking assistance and the lane-keeping system. The optional TECHNO package contains Media Display, USB-C and the reversing camera, but the exact grade page does not state its price.

Unresolved current-grade fields:

- `catalog_price`: not_stated_on_exact_current_grade_page
- `paint_palette`: not_exposed_by_exact_current_grade_pages
- `type2_charging_cable`: not_exposed_by_exact_current_grade_pages
- `home_charging_cable`: not_exposed_by_exact_current_grade_pages
- `dc40_option_price`: not_exposed_by_exact_current_grade_pages

These gaps are not filled from the default Essential configurator or the MY2025 stock-only price list.

## Extreme electric 100

Snapshot status: `partial_exact_current`.

Confirmed current state:

- catalogue price: **85900 PLN**,
- power: **75 kW (100 KM)**,
- battery: **24.3 kWh**,
- WLTP range: **225 km**,
- Type 2 cable: **standard**,
- home charging cable: **optional, 1500 PLN**,
- CITY package: **1800 PLN**,
- POWER package: **3000 PLN**.

Unresolved current-grade fields:

- `paint_palette`: not_exposed_by_exact_current_grade_pages

## Evidence boundaries

- The current Expression grade page confirms 46 equipment items but exposes neither a complete paint palette nor battery-and-charging semantics.
- The default Essential configurator state is not reassigned to Expression.
- The current Extreme comparison state confirms price, technical data, Type 2 standard equipment and current charging/package prices, but not a complete paint palette.
- No MY2025 stock-only value is promoted to a current grade snapshot.
- No dealer-stock card is generalized into a complete grade palette or reusable standalone price.

## Mutation boundary

- master rows changed: **0**,
- prices imported: **0**,
- availability states changed: **0**,
- models or domains added: **0**.

## Next package

`spring_exact_current_semantic_migration_review_001` will compare these exact current snapshots with existing availability and commercial mappings and identify only safely migratable states.
