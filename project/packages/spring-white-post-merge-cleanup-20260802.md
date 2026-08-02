# Spring White Post-Merge Cleanup

**Package ID:** `spring_white_post_merge_cleanup_001`  
**Date:** 2026-08-02  
**Status:** complete

## Purpose

Repair the repository state left by PR #455 before beginning any new Spring data or architecture work.

## Root cause

PR #455 merged temporary GitHub Actions workflows and diagnostic output that were intended only to finalize and inspect the package branch. The diagnostic output also showed that one attempted package verification failed with `unexpected verified counts after migration`; therefore that run cannot be cited as evidence of a green full-quality baseline.

## Changes

- remove four temporary Spring finalization workflows;
- remove two temporary diagnostic files;
- keep the canonical configuration-value import at `data/imports/configuration_values/spring_biel_alpejska_default_colour_20260802.json`;
- advance the operational plan to an official configurator coverage reconciliation;
- decouple the completed Spring white-migration test from the mutable `current_package` and `next_package` fields in `project/state.json`.

## Preserved data boundary

This cleanup does not modify master data, the Spring white value, commercial mappings, charging-cable records, source registrations or recorded baseline counts.

## Next package

`official_configurator_coverage_reconciliation_001` will register and snapshot the active Dacia Polska configurators for Spring, Sandero, Sandero Stepway, Jogger, Duster and Bigster. It will enumerate source-visible grades, powertrains and gearboxes and reconcile unresolved data before any supplied-cable architecture decision.

## Validation boundary

The branch requires fresh CI. Historical diagnostic output from PR #455 is explicitly not accepted as proof of success.
