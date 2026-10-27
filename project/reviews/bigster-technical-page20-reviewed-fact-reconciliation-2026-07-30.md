# Bigster Technical Page 20 Reviewed Fact Reconciliation

Date: 2026-07-30  
Package: `post_residual_bigster_technical_page20_reconciliation_001`  
Status: complete

## Decision

Reconcile the 24 complete visual source facts preserved by `residual_gap_016` and `residual_gap_017` against all 14 current Bigster configurations without changing master data or producing an approved import specification.

The review classifies eight facts primarily as existing coverage, three as import-ready gaps, three as context-model requirements and ten as deferred official-source conflicts. Classification tags overlap where a source row combines covered atomic facts with a safe gap, a missing context model or a conflicting official value.

## Confirmed coverage

The current configuration layer already represents displacement, cylinders and valves, particulate filter, maximum speed, acceleration, normalized drivetrain, front brakes and fuel-tank capacities exactly. It also represents substantial subfacts from the compound power, torque, battery, gearbox and cargo rows.

## Safe import boundary

The safest next import is limited to 30 inclusive `co2_emissions` and `fuel_consumption_combined` range rows for Mild hybrid-G 140, Mild hybrid 140 and Hybrid 155. Their upper endpoints already equal current exact values. Hybrid-G 150 4x4 remains exact-only because its printed pairs are separate petrol/LPG values rather than ranges.

## Preserved conflicts and modeling boundaries

- Hybrid 155 voltage remains 280 V in the brochure versus 200 V in the later exact source.
- Hybrid-G 150 4x4 engine power and torque RPM values conflict with current exact values.
- Unscoped direct injection cannot override fuel-specific LPG injection evidence.
- Euro 6e-bis conflicts with current Bigster Euro 6 observations.
- Mild hybrid-G 140 payload conflicts with the current exact range.
- Hybrid-G 150 4x4 cargo contexts remain blocked by the documented repair-kit/spare-wheel contradiction.
- Multi-mode `4+2`, motor-specific RPM ranges and homologation protocol require context or attribute modeling before import.

## Validation boundary

No file under `data/master/**` or `data/imports/**` changes. No current exact value is replaced, no source conflict is resolved by date preference alone, and no compound source phrase is forced into an incompatible scalar attribute.
