# Configurator Navigation State Integration 001

Date: 2026-08-07  
Baseline main: `0f8c6022b70d1545f9e7b6e385f067f3d4148a1d`

## Purpose

Connect the existing eight-step configurator navigation to the real commercial selector from step 7 and the deterministic summary from step 8, without replacing the navigation component or changing shortlist semantics.

## Problem closed

After the commercial selector and final summary were implemented, the navigation shell still exposed legacy generic state:

- `Pakiety i opcje` reported only how many result cards contained offer blocks;
- `Podsumowanie` reported only a generic result count;
- step 8 still scrolled to the general results heading rather than the new summary panel;
- step 7 could navigate to the first offer block even when several configurations remained visible.

Those states no longer represented the actual configurator flow.

## Behaviour

An additive state bridge inside the already embedded pricing/UI module now overlays only the two steps whose implementation evolved:

### Step 7 — Pakiety i opcje

Status is derived from the live browser state:

- selected commercial items: `wybrano: N`;
- one exact visible configuration with mapped offers: `oferty: N`;
- more than one visible configuration: `najpierw 1 wariant`;
- no visible configuration: `brak wyniku`;
- one visible configuration without confirmed mapped offers: `brak potwierdzonych ofert`.

When exactly one result is visible, navigation focuses that result's commercial selector. With multiple results it focuses the result set instead of arbitrarily choosing the first vehicle.

### Step 8 — Podsumowanie

Status is derived from the actual visible result cards:

- zero: `brak wyników`;
- one: `gotowe`;
- more than one: `zawęź: N wariantów`.

Navigation focuses `#configurator-summary-panel`, with the historical results heading retained only as a fallback.

## Integration contract

The bridge:

- does not create a second navigation shell;
- waits until the existing `configurator_step_navigation_v1` shell exists;
- refreshes after `dkb:results-rendered` and commercial checkbox changes;
- uses capture only for commercial/summary navigation clicks so the legacy targets cannot override the new exact targets;
- preserves `aria-current="step"` when those clicks are redirected;
- leaves model, version, powertrain and exact-observation appearance steps untouched.

## Evidence boundary

No evidence semantics change. The package does not infer commercial compatibility, does not promote exact appearance observations to catalogues and does not turn equipment filters into ordered options.

## Tests

The existing `test_unfiltered_shortlist_is_price_sorted_and_reports_unknowns` method is extended; no new discovered test method is added.

Static checks confirm the integration marker and exact targets. When Node.js is available, the test executes the exported navigation-state helpers and verifies zero/one/many result states plus selected/available/multi-result commercial states.

The canonical discovered unittest baseline remains 1885.

## Repository impact

Interface integration only:

- no master-data mutation;
- no schema change;
- no source inference;
- no additional application shell;
- no change to the deferred Spring retry package.

## Files

- `tools/reporting/configuration_shortlist_v12_pricing.js`
- `tests/test_configuration_shortlist.py`
- `project/packages/configurator-navigation-state-001-20260807.md`
- `project/state.json`
- `project/STATE_SUMMARY.md`
