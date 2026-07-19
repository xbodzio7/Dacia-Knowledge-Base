# Jogger Payload and Performance Range Modeling and Import

## Status

`IMPLEMENTING`

This package materializes the denominator selected in PR #125 through the canonical configuration-value range table. It does not change scalar observations.

## Denominator

Eleven strict specifications create 80 closed page-6 ranges with IDs `65-144`:

- 22 seat-qualified `maximum_payload` ranges;
- 6 Hybrid 155 `acceleration_0_100` ranges preserving `8.9-9.0 s` without endpoint-to-seat inference;
- 52 `max_power_rpm` and `max_torque_rpm` ranges with explicit LPG or petrol contexts.

## Preservation boundary

Range IDs `1-64` and all 1,204 scalar observations remain unchanged. Exact Hybrid combustion-engine and electric-motor RPM evidence is not remapped.

## Expected baseline

- 536 tests;
- 37 master CSV files and 3,989 rows;
- 1,204 scalar values and 71 scalar specifications;
- 144 range values and 19 range specifications;
- 1,811 availability records;
- 357 attributes in 30 categories.

## Next package

**Jogger Remaining Page-6 Exact Measurement Review** will review cargo, LPG-capacity and hybrid-system exact measurements.
