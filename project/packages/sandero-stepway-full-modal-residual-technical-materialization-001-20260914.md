# Sandero Stepway Full Modal Residual Technical Materialization

Package: `sandero_stepway_full_modal_residual_technical_001`
Source: `src_pl_sandero_stepway_full_modal_20260809`

## Purpose

Reconcile the 315 source-bounded technical scalar/source-state candidates isolated by the 2026-08-09 full-modal capture against current `main`, and materialize only candidates whose exact configuration/attribute/fuel/gear slot is genuinely absent.

## Result

The live materialization preflight found:

- 315 source candidate rows;
- 297 scalar candidates already occupied by exact current configuration/attribute slots;
- 18 composite/non-scalar candidates that remain deferred;
- 0 pending scalar rows available for safe materialization;
- 0 rows added to `data/master/configuration_attribute_values.csv`.

For occupied slots the materializer also checks that the current value contains the exact parsed source value. A disagreement is a hard pre-write conflict rather than an overwrite or normalization opportunity.

Therefore this package closes the residual technical materialization scope with a **zero data delta**. The 315-row historical candidate set does not represent 315 missing master-data rows in the current repository state.

## Scope and mapping

The package remains limited to the existing 21-label mapping from the residual technical reconciliation.

`Liczba drzwi` maps only to `number_of_doors`. No `door_count` attribute is introduced.

The source literal is preserved. Numeric scalar values are parsed only where the mapping explicitly declares `integer` or `number`; composite values are deferred and are not split or inferred.

## Drive-layout boundary

Before any write, the materializer compares every source literal for `Rodzaj napędu` with the values already present for `drive_layout` in current master data. The live preflight completed this gate successfully.

This is an exact vocabulary gate. No normalization, synonym replacement, or inference is performed. In particular, `przedni` is not converted to `FWD`.

## Safety boundaries

- PR #634 is not modified, rerun, closed, or merged.
- PR #639 remains closed and is not revived.
- No cross-configuration projection is performed.
- Existing occupied slots are not duplicated.
- Occupied-slot value disagreements are fatal before any write.
- No source value is rewritten by normalization.
- No materialization occurs if the drive-layout vocabulary gate fails.
- Composite/non-scalar values remain deferred.

## Idempotence

The materializer derives occupied slots and materialization codes from current master data before writing. With the current repository state, a repeated `--apply` run remains a zero-data-delta operation.

## Acceptance criteria

1. Live source candidate count is exactly 315.
2. All mapped attributes are resolved by the current dictionary.
3. `number_of_doors` is used for `Liczba drzwi`; `door_count` is absent.
4. All source `drive_layout` literals are already present in the current master vocabulary.
5. All 297 scalar candidates are occupied by exact current slots with matching values.
6. The remaining 18 candidates are explicitly deferred as composite/non-scalar.
7. No master-data write is performed because there are no pending scalar rows.
8. Tests and the full Quality workflow pass on the final head.

## Files

- `tools/materialize_sandero_stepway_full_modal_residual_technical_20260914.py`
- `tests/test_sandero_stepway_full_modal_residual_technical_20260914.py`
