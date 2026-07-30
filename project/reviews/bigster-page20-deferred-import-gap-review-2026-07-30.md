# Bigster Page 20 Deferred Import Gap Review

Date: 2026-07-30  
Package: `post_residual_bigster_page20_deferred_import_gap_review_001`  
Status: complete

## Decision

Approve a narrow follow-up import for three atomic subfacts that are independent of the conflicts contained in the same page-20 rows:

- total Hybrid-G 150 4×4 system power: `113 kW`;
- Hybrid-G 150 4×4 traction-motor torque: `87 Nm`;
- lithium-ion hybrid-battery chemistry: `lithium_ion`.

The resulting import contains exactly 20 observations: six values across the three Hybrid-G 150 4×4 configurations and battery chemistry across all 14 active Bigster configurations.

## Semantic boundary

`hybrid_system_power_total` stores source-stated total propulsion-system output and does not inherit the combustion-engine RPM conflict. `traction_motor_torque` stores the motor torque only; the printed `1630 rpm` is excluded because no motor-specific RPM contract is approved. Battery chemistry uses `hybrid_battery_type`, which already carries the canonical `lithium_ion` enum in hybrid configuration data.

## Preserved conflicts

The review does not change or reinterpret:

- engine maximum-power RPM `4500` versus `5000`;
- engine maximum-torque RPM `4000` versus `1750`;
- traction-motor operating-speed context `1630 rpm`;
- battery capacity `0.84` versus `0.839 kWh`;
- Hybrid 155 voltage `280` versus `200 V`.

## Validation boundary

All 14 targets are active and linked to `src_pl_bigster_brochure_20251210` through `brochure_technical_data_for`. No file under `data/master/**` or `data/imports/**` changes in this review package. The next package must update the affected completeness scopes and current coverage contracts together with the 20 imported observations.
