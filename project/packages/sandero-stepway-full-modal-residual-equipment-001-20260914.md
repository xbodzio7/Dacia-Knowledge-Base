# Sandero Stepway Full Modal Residual Equipment

Package: `sandero_stepway_full_modal_residual_equipment_001`
Source: `src_pl_sandero_stepway_full_modal_20260809`

## Purpose

Reconcile the 286 standard-equipment occurrences classified as safe by the full-modal canonical reconciliation against the current `main` master availability data, materializing only genuinely absent canonical observations.

## Result

The live materializer preflight found:

- 286 safe equipment occurrences in scope;
- 277 occurrences with explicit canonical mappings;
- 370 canonical availability targets already occupied in current master data;
- 0 new availability rows required;
- 9 `kluczyk z 3 przyciskami` occurrences preserved as schema-gap evidence;
- 155 other residual equipment occurrences preserved outside positive normalization.

Therefore this package also closes with a **zero data delta**. The older PR #637 branch is not a source of current-main truth and is not reused or rerun.

The higher occupied-target count is expected because several source literals intentionally map to multiple canonical availability attributes.

## Mapping policy

Only explicit source-literal mappings are used. Composite literals may create multiple canonical availability targets, but no first-match inference is performed.

The five negative/base literals remain excluded from the positive candidate set:

- `bez automatycznego parkowania`
- `bez podłogi bagażnika ustawianej w dwóch płaszczyznach (góra i dół)`
- `brak świateł przeciwmgielnych`
- `kierownica nieogrzewana`
- `szyba przednia nieogrzewana`

`kluczyk z 3 przyciskami` remains a schema gap and is not mapped to the unrelated `key_count` attribute.

## Safety boundaries

- PR #637 is not reused, rerun, or modified.
- PR #634 remains untouched and #639 remains closed.
- No negative wording is converted into a positive standard state.
- No cross-configuration projection is performed.
- Existing canonical availability codes are not duplicated.
- No arbitrary first-match mapping is used.
- Source literals remain available in the reconciliation/source evidence; no source literal is rewritten.

## Acceptance criteria

1. The safe occurrence count is exactly 286.
2. The explicitly materializable subset is exactly 277 occurrences.
3. All 277 occurrences have explicit mappings.
4. The 9 schema-gap occurrences remain preserved.
5. All mapped canonical targets are already present in current master data.
6. No availability rows are added by this package.
7. The current baseline remains 7286 availability records.
8. Tests and the full Quality workflow pass on the final head.

## Files

- `project/packages/sandero-stepway-full-modal-residual-equipment-001-20260914.md`
- `tools/materialize_sandero_stepway_full_modal_residual_equipment_20260914.py`
