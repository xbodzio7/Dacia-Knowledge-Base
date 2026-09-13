# Sandero Stepway Full Modal Residual Technical Reconciliation

Package: `sandero_stepway_full_modal_residual_technical_reconciliation_001`
Observed source: `src_pl_sandero_stepway_full_modal_20260809`

## Purpose

Reconcile the existing 315-candidate technical-scalar package from PR #634 against the current `main` dictionary and configuration-value state without modifying PR #634 and without materializing any data.

## Result contract

The audit verifies:

- the source still yields exactly 315 candidates;
- all 21 mapping targets exist in the current attribute dictionary;
- exact configuration slots already occupied in current master data are identified instead of duplicated;
- `Liczba drzwi` remains mapped only to `number_of_doors`;
- no `door_count` target is introduced;
- the audit performs no master-data writes and explicitly reports promotion as disallowed.

## Known semantic boundary

`Rodzaj napędu` is mapped by the historical PR #634 package to `drive_layout`, but its source values require explicit value-vocabulary reconciliation before promotion. This is intentionally surfaced as a blocker rather than silently converting source values.

This boundary is especially important because the earlier partial attempt to materialize technical values produced invalid `drive_layout` values. The present package therefore audits compatibility only.

## Safety boundaries

- PR #634 is not modified, rerun, closed, or merged.
- No duplicate materialization package is created.
- No values are normalized by inference.
- No cross-configuration projection is performed.
- No `data/master` file is modified.

## Tool

`tools/reconcile_sandero_stepway_full_modal_residual_technical_20260913.py`

## Test

`tests/test_sandero_stepway_full_modal_residual_technical_reconciliation_20260913.py`
