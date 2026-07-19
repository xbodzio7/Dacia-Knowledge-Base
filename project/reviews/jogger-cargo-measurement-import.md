# Jogger Cargo Measurement Modeling and Import

## Status

`IMPLEMENTED`

The two Jogger MY26 page-6 VDA luggage-compartment measurements are represented
as separate canonical concepts. Their source-stated vertical boundaries remain
part of the attribute meaning and are not collapsed into generic cargo volume.

## Canonical attributes

### `cargo_volume_vda_to_luggage_cover`

- ID 360;
- category `Capacities`;
- integer value using existing unit `L`;
- volume measured according to VDA up to luggage-cover or roller-blind height.

### `cargo_volume_vda_to_seatback`

- ID 361;
- category `Capacities`;
- integer value using existing unit `L`;
- volume measured according to VDA up to seat-back height.

Both remain distinct from `boot_capacity` and `cargo_volume_vda`, whose current
definitions do not identify the same complete measurement boundary.

## Imported denominator

| Seating identity | Configurations | To luggage cover | To seat back | Observations |
| --- | ---: | ---: | ---: | ---: |
| 5-seat | 11 | 708 L | 607 L | 22 |
| 7-seat | 11 | 160 L | 506 L | 22 |
| **Total** | **22** | **22 rows** | **22 rows** | **44** |

Two strict declarative specifications materialize IDs 1129-1172 with
observation date `2026-04-01`, source page 6 and section `BAGAŻNIK`.

## Evidence boundary

- The exact `do wysokości rolety` and `do wysokości oparcia` meanings are
  preserved independently.
- Values are selected solely from explicit five-/seven-seat configuration
  identity.
- No powertrain or trim variance is inferred.
- No generic `boot_capacity` or `cargo_volume_vda` observation is created from
  the qualified source rows.
- No preferred, maximum or combined cargo figure is calculated.
- Existing scalar, injection, gearbox and minimum-weight ID ranges remain
  unchanged.

## Regression guarantees

Six dedicated tests require:

- both active integer attribute contracts;
- two strict 22-row specifications and contiguous IDs 1129-1172;
- both measurements for every active Jogger configuration;
- exact 11/11 five-/seven-seat value counts;
- absence of generic cargo observations from these source rows;
- registered source, page, section, source text and PDF SHA-256.

## Expected verified baseline

After materialization:

- 482 tests;
- 34 master CSV files and 3,799 rows;
- 1,172 dated configuration values;
- 67 declarative configuration-value import specifications;
- 1,811 equipment-availability records;
- 354 canonical attributes in 30 categories.

## Next package

**Jogger LPG Capacity Modeling Review** will separate total LPG vessel capacity
from permitted filling capacity before importing the source-stated 50/40 L
pairs for all 10 active Eco-G configurations.
