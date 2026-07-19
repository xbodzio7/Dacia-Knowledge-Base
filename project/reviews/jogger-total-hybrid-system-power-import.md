# Jogger Total Hybrid System Power Modeling and Import

## Status

`IMPLEMENTED`

The source-stated total output of the Jogger Hybrid 155 propulsion system is
represented independently from its combustion-engine, traction-motor and
starter-generator components.

## Canonical attribute

The package introduces:

- ID 364;
- code `hybrid_system_power_total`;
- category `Hybrid System`;
- name `Total hybrid system power`;
- decimal value using existing unit `kW`;
- meaning: source-stated output of the complete hybrid propulsion system, never
  a calculated sum of component powers.

## Imported denominator

| Group | Configurations | Value | Observations |
| --- | ---: | ---: | ---: |
| Hybrid 155 five-seat | 3 | 116 kW | 3 |
| Hybrid 155 seven-seat | 3 | 116 kW | 3 |
| **Total** | **6** | **116 kW** | **6** |

One strict declarative specification materializes IDs 1193-1198 with
observation date `2026-04-01`, source page 6 and section `SILNIKI`.

## Evidence boundary

- Existing 80 kW engine, 36 kW traction-motor and 15 kW starter-generator
  observations remain unchanged.
- The 116 kW value is not calculated from those components.
- Lithium-ion chemistry remains excluded because the repository has no
  controlled battery-chemistry dictionary or validated mapping for
  `hybrid_battery_type`.
- The source-stated 1.4 kWh remains excluded because its gross, nominal or
  usable basis is unspecified, while `hybrid_battery_capacity` means usable
  capacity.
- The existing 200 V battery-voltage observations remain unchanged.
- All earlier Jogger configuration-value ID ranges remain independent.

## Regression guarantees

Six dedicated tests require:

- the active total-system-power attribute contract;
- one strict 6-row specification and contiguous IDs 1193-1198;
- all and only the six active Hybrid 155 configurations;
- unchanged component powers and a source-stated rather than calculated total;
- no battery-chemistry or unspecified-capacity observations;
- registered source, page, source text and PDF SHA-256.

## Expected verified baseline

After materialization:

- 494 tests;
- 34 master CSV files and 3,828 rows;
- 1,198 dated configuration values;
- 70 declarative configuration-value import specifications;
- 1,811 equipment-availability records;
- 357 canonical attributes in 30 categories.

## Next package

**Jogger Remaining Technical Architecture Review** will prepare explicit
options for battery-chemistry controlled values, battery-capacity basis and
interval representation. Those changes cross the repository's architecture
boundary and require an approved decision before implementation.
