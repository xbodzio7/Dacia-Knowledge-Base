# Spring Current Grade Snapshot Capture

Package ID: `spring_current_grade_snapshot_capture_001`

Status: complete

## Goal

Capture exact current official Expression and Extreme grade states, including explicitly unresolved paint and charging fields, before any bounded master-data migration.

## Delivered

- captured the current exact Expression grade equipment page with 46 items and the TECHNO package composition;
- retained the Expression catalogue price, paint palette and charging semantics as unresolved because exact current grade pages do not expose them;
- captured the current Extreme grade equipment page with 48 items;
- captured the exact Extreme electric 100 comparison state: 85,900 PLN, 75 kW, 24.3 kWh, 225 km WLTP and 40 kW DC charging;
- retained the current Type 2 cable as standard for Extreme, the home cable at 1,500 PLN, CITY at 1,800 PLN and POWER at 3,000 PLN;
- retained both current grade paint palettes as unresolved where a complete exact grade list is not exposed;
- generated deterministic JSON and Markdown reports.

## Evidence boundary

No Essential default state is copied to Expression. No MY2025 stock-only value is promoted to a current grade. No stock vehicle is generalized into a complete grade palette or reusable standalone price.

## Master-data boundary

This package changes no master row, price, availability state, model, domain or attribute.

## Follow-up

Proceed with `spring_exact_current_semantic_migration_review_001` to compare the captured current states with existing availability and commercial mappings and enumerate only safely migratable records.
