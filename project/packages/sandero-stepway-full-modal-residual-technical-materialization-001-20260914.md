# Sandero Stepway Full Modal Residual Technical Materialization

Package: `sandero_stepway_full_modal_residual_technical_001`
Source: `src_pl_sandero_stepway_full_modal_20260809`

## Purpose

Materialize the 315 source-bounded technical scalar/source-state candidates isolated by the 2026-08-09 full-modal capture and reconciled against current `main`.

## Scope

The package is limited to the existing 21-label mapping from the residual technical reconciliation. It may add only rows whose exact configuration/attribute/fuel/gear slot is not already occupied in `data/master/configuration_attribute_values.csv`.

The source literal is preserved. Numeric scalar values are parsed only where the existing mapping explicitly declares `integer` or `number`; composite values remain deferred evidence and are not split or inferred.

`Liczba drzwi` maps only to `number_of_doors`. No `door_count` attribute is introduced.

## Drive-layout boundary

Before any write, the materializer compares every source literal for `Rodzaj napędu` with the values already present for `drive_layout` in current master data. Materialization aborts if any source literal is absent from that vocabulary.

This is an exact vocabulary gate. No normalization, synonym replacement, or inference is performed. In particular, `przedni` is not converted to `FWD`.

## Safety boundaries

- PR #634 is not modified, rerun, closed, or merged.
- PR #639 remains closed and is not revived.
- No cross-configuration projection is performed.
- Existing occupied slots are skipped; no duplicate slot is written.
- No source value is rewritten by normalization.
- No materialization occurs if the drive-layout vocabulary gate fails.
- Composite/non-scalar source values remain deferred.

## Idempotence

The materializer derives occupied slots and materialization codes from current master data before writing. A repeated run therefore adds only still-missing candidates and does not duplicate previously materialized rows.

## Acceptance criteria

1. Live source candidate count remains exactly 315.
2. All mapped attributes are resolved by the current dictionary.
3. `number_of_doors` is used for `Liczba drzwi`; `door_count` is absent.
4. All source `drive_layout` literals are already present in the current master vocabulary before write.
5. Only unoccupied exact slots are materialized.
6. Composite/non-scalar values are reported as deferred, not transformed.
7. The materialization is bounded to the 315 source candidates.
8. Tests and the full Quality workflow pass on the final head.

## Files

- `tools/materialize_sandero_stepway_full_modal_residual_technical_20260914.py`
- `tests/test_sandero_stepway_full_modal_residual_technical_20260914.py`
- `data/master/configuration_attribute_values.csv` — changed only by `--apply` after all pre-write gates pass.
