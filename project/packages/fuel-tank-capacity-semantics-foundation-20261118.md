# Fuel Tank Total vs Usable Capacity Semantics

**Package ID:** `fuel_tank_capacity_semantics_foundation_20261118_001`  
**Date:** 2026-11-18  
**Status:** Implementation prepared; pending exact-HEAD CI validation and merge  
**Architecture decision:** D-032

## Objective

Represent total physical fuel-tank capacity separately from explicitly stated usable fuel volume without changing the existing observation table or invalidating historical records.

## Changes

- Added `fuel_tank_capacity_total` (decimal litres) to the canonical `Capacities` attribute category.
- Added `fuel_tank_capacity_usable` (decimal litres) to the canonical `Capacities` attribute category.
- Preserved the legacy `fuel_tank_capacity` attribute unchanged.
- Reused the existing optional `fuel_type_code` observation context for source-stated petrol/LPG-specific values.
- Recorded D-032 in `project/DECISIONS.md`.
- Updated `project/DATA_SCHEMA.md` and `project/ATTRIBUTE_CATALOG.md`.
- Added contract tests for the two new definitions and legacy compatibility.
- Refreshed canonical project state and generated documentation baseline counters.

## Evidence and non-goals

This is a schema-foundation package only. It does not import tank-capacity values and does not change existing configuration observations.

The next package must inspect the exact archived Polish Sandero/Sandero Stepway and Jogger price-list pages. Each value must be classified as total or usable only when the source establishes that meaning. Fuel context and exact configuration applicability must be explicit. No value may be transferred between models or powertrains based on similarity.

If a source states a capacity without establishing total versus usable semantics, leave it unclassified and record the gap for review.

## Acceptance criteria

- Both new attributes have unique IDs and codes and reference the existing `Capacities` category.
- Existing attribute definitions and observations remain unchanged.
- The test suite verifies the exact contracts and legacy compatibility.
- `project/state.json`, `project/STATE_SUMMARY.md` and managed documentation baseline counters agree with the repository.
- Required CI checks pass on the exact PR head before merge.
