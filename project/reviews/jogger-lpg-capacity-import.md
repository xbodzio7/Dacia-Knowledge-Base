# Jogger LPG Capacity Modeling and Import

## Status

`IMPLEMENTED`

The Jogger MY26 source-stated LPG pair is represented as two separate capacity
concepts with explicit LPG fuel context. Existing petrol tank observations are
unchanged.

## Canonical attributes

### `lpg_vessel_capacity_total`

- ID 362;
- category `Capacities`;
- decimal value using existing unit `L`;
- total internal volume of the LPG pressure vessel.

### `lpg_vessel_filling_capacity`

- ID 363;
- category `Capacities`;
- decimal value using existing unit `L`;
- source-stated LPG volume available or permitted for filling.

Both remain distinct from generic `fuel_tank_capacity`.

## Imported denominator

| Group | Configurations | Total vessel | Filling volume | Observations |
| --- | ---: | ---: | ---: | ---: |
| Eco-G 120 manual | 6 | 50 L | 40 L | 12 |
| Eco-G 120 automatic | 4 | 50 L | 40 L | 8 |
| **Total** | **10** | **10 rows** | **10 rows** | **20** |

Two strict declarative specifications materialize IDs 1173-1192 with
observation date `2026-04-01`, source page 6 and LPG fuel context.

## Evidence boundary

- The source-stated `50/40` pair is preserved as total vessel and filling
  capacity, never as one interchangeable value.
- All new rows use `fuel_type_code=lpg`.
- Existing Eco-G petrol `fuel_tank_capacity=50 L` rows remain unchanged.
- No generic LPG `fuel_tank_capacity` row is created.
- TCe 110 and Hybrid 155 receive no LPG-capacity observation.
- No 80% filling ratio is calculated; both values are explicit source text.
- Existing scalar, injection, gearbox, minimum-weight and cargo ID ranges remain
  unchanged.

## Regression guarantees

Six dedicated tests require:

- both active decimal LPG-capacity attribute contracts;
- two strict 10-row specifications and contiguous IDs 1173-1192;
- all and only the 10 active Eco-G configurations;
- exact 50/40 value counts and LPG context;
- unchanged petrol tank rows and absence of generic LPG tank rows;
- registered source, page, source text and PDF SHA-256.

## Verified local baseline

The one-shot materializer passed compilation, 488 unit tests, orchestration
contracts, registered-source and PDF verification, canonical project-state and
documentation checks, and the complete local Quality gate.

The resulting repository baseline is:

- 488 tests;
- 34 master CSV files and 3,821 rows;
- 1,192 dated configuration values;
- 69 declarative configuration-value import specifications;
- 1,811 equipment-availability records;
- 356 canonical attributes in 30 categories.

## Next package

**Jogger Hybrid System Semantics Review** will assess the source-stated 116 kW
total system power and lithium-ion chemistry. The 1.4 kWh capacity remains
deferred because the source does not identify its gross, nominal or usable
basis.
