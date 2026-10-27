# Bigster Page 20 Remaining Conflict Boundary Review

Date: 2026-07-30  
Package: `post_residual_bigster_page20_remaining_conflict_boundary_review_001`  
Status: complete

## Decision

The remaining page-20 contradictions are divided into source-observation-ready and context-blocked boundaries. The repository already supports multiple registered observations for the same configuration/attribute slot when source and observation date differ. Older brochure observations may therefore be preserved without replacing later price-source values.

The next package is restricted to the two explicit Hybrid-G 150 combustion-engine RPM statements: `4500 rpm` at maximum power and `4000 rpm` at maximum torque, each for the three active Hybrid-G 150 4×4 configurations.

## Required coexistence contract

The import must retain all later price-source observations:

- `max_power_rpm=5000` dated 2026-07-03;
- `max_torque_rpm=1750` dated 2026-07-03.

The new brochure observations are dated 2025-12-10 and use `src_pl_bigster_brochure_20251210`. No source is declared authoritative merely because it is newer.

## Deferred boundaries

- Euro 6e-bis versus Euro 6, Hybrid 155 voltage 280 versus 200 V, source-stated battery capacity 0.84 versus 0.839 kWh and the Mild hybrid-G payload range are eligible for later source-preservation packages.
- LPG injection remains blocked because the brochure row lacks fuel scope.
- Motor RPM remains blocked because no motor-specific RPM attribute exists.
- Cargo values remain blocked by contradictory repair-kit/spare-wheel context and one literal anomalous source sequence.

## Scope

This review changes no master data, import specifications, ranges or attributes. It only records the conflict-preservation policy and selects the next six-observation package.
