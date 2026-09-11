# Sandero Stepway Full Modal Residual Technical Materialization

Package: `sandero_stepway_full_modal_residual_technical_001`
Observed source: `src_pl_sandero_stepway_full_modal_20260809`

## Scope

Materialize the 315 source-bounded technical scalar/source-state candidates identified by the verified residual review, using only the current canonical attribute dictionary and exact values from the 2026-08-09 full-modal capture.

The package is deliberately limited to labels whose target attribute and value semantics are unambiguous. Composite technical strings that require contextual decomposition remain outside this package, as do model-qualified/multi-context values and all equipment residuals.

## Mapping contract

- `Liczba drzwi` targets `number_of_doors`; the obsolete `door_count` target is forbidden.
- Numeric values are imported only when the captured value is a single scalar.
- Source-stated text attributes preserve the literal source value without reinterpretation.
- Existing exact configuration slots are not duplicated; the full-modal observation remains evidence through its source relationship.
- No value is projected between configurations, grades, engines or transmissions.

## Acceptance criteria

1. The live candidate count is exactly 315.
2. The materializer is idempotent.
3. The 315 candidates are either already covered or materialized against the exact configuration/source.
4. No `door_count` observation is introduced.
5. Repository Quality passes on the final head.

## Deferred scope

The remaining residual review contains 286 equipment candidates, 124 contextual technical candidates and 215 preserved-evidence rows. Those remain separate bounded work and are not silently promoted by this package.
