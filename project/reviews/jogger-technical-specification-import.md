# Jogger Technical Specification Import

## Status

`COMPLETE`

The selected page-6 technical denominator has been materialized as 312 exact,
dated configuration observations for all 22 active Jogger MY26 catalogue
configurations.

## Imported denominator

| Group | Configurations | Slots per configuration | Observations |
| --- | ---: | ---: | ---: |
| Eco-G 120 manual | 6 | 15 | 90 |
| Eco-G 120 automatic | 4 | 15 | 60 |
| TCe 110 manual | 6 | 12 | 72 |
| Hybrid 155 automatic | 6 | 15 | 90 |
| **Total** | **22** | — | **312** |

The new rows use IDs 725–1036 and observation date `2026-04-01`. Every row
references `src_pl_jogger_price_my26_20260401`, source page 6 and its exact
technical-table section.

## Declarative specifications

Seventeen versioned import specifications cover:

- emission standard, displacement, cylinder and total-valve count;
- combustion-engine power and torque;
- start-stop, top speed and exact 0–100 km/h observations;
- petrol/fixed fuel-tank capacity, gross vehicle weight and braked trailer;
- Hybrid 155 engine maximum-torque RPM, traction-motor power, HSG power,
  traction-motor torque and battery voltage.

The shared importer verifies attribute contracts, registered
source-configuration pairs, contiguous IDs, fuel contexts and the exact
repository-local PDF hash before accepting the rows.

## Preserved contexts

Eco-G engine power, torque and acceleration remain separate LPG and petrol
observations. Its generic fuel-tank record is created only for the separately
stated 50 L petrol tank; the LPG `50/40` total/filling pair remains deferred.

Acceleration and gross vehicle weight use the explicit five-/seven-seat value
for each configuration. Hybrid 155 retains separate 80 kW combustion-engine,
36 kW traction-motor and 15 kW HSG observations; 116 kW total system power is
not written to `engine_power`.

## Deliberately excluded evidence

No scalar row was created for:

- fuel-consumption, CO2, payload or Hybrid acceleration ranges;
- minimum-qualified kerb weights;
- the two condition-specific VDA cargo measurements;
- LPG total and filling capacity;
- Hybrid 155 total system power, battery chemistry or unspecified-basis
  battery capacity;
- gearbox type/count or injection type pending controlled master-data mapping;
- Eco-G and TCe engine-speed ranges.

These exclusions remain evidence boundaries, not missing values.

## Regression result

Eight dedicated tests lock:

- the exact set of 17 specifications and 312 rows;
- IDs 725–1036 and per-configuration denominators;
- LPG/petrol and five-/seven-seat contexts;
- Hybrid component separation;
- absence of every deferred attribute;
- page-6 provenance and the exact 2,031,453-byte PDF SHA-256.

The resulting verified repository baseline is 459 tests, 3,658 master-data
rows, 1,036 dated configuration values and 61 declarative configuration-value
import specifications.

## Next package

The project advances to **Jogger Deferred Technical Evidence Reconciliation**.
It will select one bounded modelling or import package from the deferred ranges,
minimum qualifiers, cargo definitions, LPG capacity, battery semantics,
gearbox entities and injection mapping without weakening the source meaning.
