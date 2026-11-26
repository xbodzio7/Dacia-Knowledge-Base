# Sandero Page 17 Power and Torque RPM Range Import Closure

Status: complete with preserved boundaries  
Package: `post_residual_sandero_page17_power_torque_rpm_range_import_closure_001`  
Source: `src_pl_sandero_brochure_20260202`, page 17

## Exact receipt

- two strict range specifications are present and source-bounded;
- IDs `279–298` form one contiguous 20-row suffix;
- `max_power_rpm` contains 11 observations and `max_torque_rpm` contains 9 observations;
- all intervals are closed, use `rpm`, retain observation date `2026-02-02` and target exactly seven active Sandero III configurations;
- fuel context remains explicit: 12 petrol observations and 8 LPG observations.

## Reconciliation closure

Both import-ready decisions from the 46-candidate Sandero page-17 reconciliation are fully materialized. The original partition remains exact: 11 scalar-coverage candidates, 2 configuration/fuel-identity candidates, 2 imported range candidates, 1 context-model boundary and 30 explicit non-import/context candidates. No import-ready exact gap remains.

## Preserved boundaries

- the printed `100 TCe` / `74 (120 KM)` inconsistency remains literal and does not create another scalar power value;
- no petrol torque-speed interval is inferred for the two Eco-G automatic configurations because the reviewed source has no aligned RPM continuation;
- petrol and LPG subcolumns remain separate source contexts;
- the shared direct-injection row remains deferred for dual-fuel Eco-G rather than becoming an unscoped scalar;
- protocol labels, country-dependent continuations and context-only fragments remain non-imports.

## Release checkpoint

The bounded Sandero page-17 import chain is complete. The next package prepares, but does not publish, `data-products-v1.9.0` from the current source-backed repository state.
