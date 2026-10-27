# Configurator Commercial Selection State 001

Date: 2026-08-07  
Baseline main: `07444dc1c3a0319d212bdc517699ae80dd128d38`

## Purpose

Make explicit step-7 package/option choices stable across result rerenders and page reloads within the same browser session, while keeping one canonical source-bounded state for JSON export and deterministic reset semantics.

## State ownership

`configuration_shortlist_selection.js` owns the persisted configuration-scoped commercial selection state. The pricing module keeps only its existing transient rendering cache and is synchronized from the canonical selection state through the same checkbox change events already used by the UI.

The canonical state is stored under:

`dkb-commercial-selections-v1`

in `sessionStorage` when browser storage is available.

## Normalization boundary

Stored or submitted state is normalized against the current embedded catalogue before use:

- unknown configuration codes are discarded;
- commercial item codes not mapped as selectable offers for that exact configuration are discarded;
- duplicate commercial item codes collapse deterministically;
- configurations with no valid selected commercial items are omitted from persisted state.

No stale storage value can synthesize an offer or transfer a package/option to another configuration.

## Restore behaviour

On page initialization the selection layer reads and normalizes the stored state. After result cards and commercial panels are rendered, it reconciles visible checkbox controls with the canonical state one mismatch at a time.

Each synthetic checkbox change is sent through the normal bubbling change contract. This updates the existing pricing cache, summary and navigation without a private backdoor or duplicate pricing API.

Selections for temporarily hidden configurations remain in canonical session state. When such a configuration becomes visible again, its controls are reconciled from that state.

## Reset behaviour

The main `Resetuj` action clears the complete canonical commercial-selection map and removes the sessionStorage entry, including selections belonging to configurations that are currently hidden by filters.

Visible controls are then reconciled through normal change events. A previously hidden card cannot restore stale commercial state later because canonical storage is already empty; when it reappears, the stale transient rendering cache is corrected against the empty canonical state.

## Export compatibility

The JSON export introduced by `Configurator Commercial Selection Export 001` now takes its commercial-selection snapshot from the same canonical state. Only configurations actually selected for JSON export contribute commercial metadata.

TXT configuration-code export remains unchanged.

## Failure boundary

If `sessionStorage` is unavailable or rejects access, the report remains fully usable with in-memory state for the current page. Storage failure does not block filtering, pricing, comparison or export.

## Tests

Existing methods in `tests/test_configuration_selection_export.py` are extended; no new discovered unittest method is added.

Node coverage verifies:

- state normalization removes unknown configuration/item mappings and duplicates;
- deterministic snapshotting includes only selected configurations;
- persisted JSON contains only normalized exact-configuration selections;
- persisted state restores identically;
- writing an empty state removes the storage entry;
- the canonical storage key remains stable.

The existing offline HTML test also verifies the storage key, commercial-control reconciliation and explicit `Resetuj` integration.

The canonical discovered unittest baseline remains 1885.

## Repository impact

Interface state only:

- no master-data mutation;
- no schema migration;
- no change to commercial compatibility semantics;
- no change to exact appearance evidence;
- no change to TXT export;
- no change to the deferred Spring retry package.

## Files

- `tools/reporting/configuration_shortlist_selection.js`
- `tests/test_configuration_selection_export.py`
- `project/packages/configurator-commercial-selection-state-001-20260807.md`
- `project/state.json`
- `project/STATE_SUMMARY.md`
