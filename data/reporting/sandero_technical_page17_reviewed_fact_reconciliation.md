# Sandero Technical Page 17 Reviewed Fact Reconciliation

## Result

All 46 authored candidates are reconciled against the current master. Eleven candidates are closed by exact scalar coverage, two by existing configuration/fuel identity, one remains a fuel-context modeling boundary and 30 remain explicit context/non-import evidence.

The only import-ready gap consists of two source rows representing 20 closed RPM ranges: 11 `max_power_rpm` observations and 9 `max_torque_rpm` observations across seven active Sandero III configurations.

## Range handoff

- TCe 100 power: 5000–5250 rpm for three configurations;
- Eco-G 120 power: LPG 4500–5000 rpm and petrol 4500–5750 rpm for manual and automatic configurations;
- TCe 100 torque: 2900–3500 rpm for three configurations;
- Eco-G 120 torque: LPG 1750–3750 rpm for manual and automatic configurations, petrol 2000–4000 rpm for manual configurations only;
- Eco-G automatic petrol torque range is excluded because the reviewed extraction has no aligned rpm continuation.

## Release checkpoint

Publish `data-products-v1.9.0` after the 20-range import and its closure. This is the one small exact package allowed by the queue-review decision rule.
