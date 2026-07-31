# Review — Sandero technical page 17 reviewed-fact reconciliation

Date: 2026-07-31  
Package: `post_residual_sandero_technical_page17_reviewed_fact_reconciliation_001`

## Decision

The current master already covers every reviewed scalar fact for the seven active Sandero III configurations. The remaining exact gap is limited to 20 closed engine-speed ranges from two source rows.

## Preserved boundaries

The printed `100 TCe` / `74 (120 KM)` inconsistency is retained literally and does not create another power value. The shared Eco-G injection row remains fuel-context deferred. The missing automatic-petrol torque rpm continuation, country-dependent values and protocol/context fragments are not inferred.

## Handoff and release

Proceed to `post_residual_sandero_page17_power_torque_rpm_range_import_001`, then its closure. The handoff is bounded to the 20 reviewed ranges and does not reopen scalar or context decisions. Publish `data-products-v1.9.0` immediately after both PRs are green and merged.
