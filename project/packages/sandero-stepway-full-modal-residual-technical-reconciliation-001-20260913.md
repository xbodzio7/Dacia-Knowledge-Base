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
- `Rodzaj napędu` is reconciled against the current `drive_layout` value vocabulary using exact source literals;
- no value normalization or inference is performed;
- the audit performs no master-data writes.

## Resolved semantic boundary

The previous package treated `Rodzaj napędu` → `drive_layout` as an unresolved blocker because an earlier partial materialization attempt had produced invalid values.

The current audit no longer assumes that blocker. It reads the source literals and the values already present for `drive_layout` in current master data and reports any source literal not already represented there. This is an exact vocabulary check, not a normalization step.

If the source value is already present in the current vocabulary, it remains unchanged. No conversion such as `przedni` → `FWD` is performed.

## Safety boundaries

- PR #634 is not modified, rerun, closed, or merged.
- No duplicate materialization package is created.
- No values are normalized by inference.
- No cross-configuration projection is performed.
- No `data/master` file is modified.

## Tool

`tools/reconcile_sandero_stepway_full_modal_residual_technical_20260913.py`

The tool now performs the `drive_layout` vocabulary reconciliation directly against current master data.

## Next step

If the audit reports no unresolved `drive_layout` source values, the remaining work is a separate materialization package which must preserve exact source literals, skip already occupied slots, and remain bounded to the 315 source candidates.
