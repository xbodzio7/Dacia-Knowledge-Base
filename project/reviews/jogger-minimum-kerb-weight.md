# Jogger Minimum Kerb Weight Modeling and Import

## Status

`IMPLEMENTED`

The page-6 row `masa własna min (kg) 5-m / 7-m` is represented without
weakening its minimum qualifier or rewriting it as the existing unqualified
`kerb_weight` concept.

## Canonical model

The package introduces one attribute:

- code: `minimum_kerb_weight`;
- category: `Weights`;
- data type: `integer`;
- unit: `kg`;
- status: `active`;
- meaning: minimum kerb weight explicitly stated by a source, distinct from an
  unqualified kerb-weight observation.

No new category, unit, enum or general range representation is introduced.

## Imported denominator

| Powertrain | 5-seat value | 7-seat value | Configurations | Observations |
| --- | ---: | ---: | ---: | ---: |
| Eco-G 120 manual | 1292 kg | 1321 kg | 6 | 6 |
| Eco-G 120 automatic | 1326 kg | 1354 kg | 4 | 4 |
| TCe 110 manual | 1193 kg | 1221 kg | 6 | 6 |
| Hybrid 155 automatic | 1359 kg | 1388 kg | 6 | 6 |
| **Total** | - | - | **22** | **22** |

The declarative specification uses configuration-value IDs 1107-1128,
observation date `2026-04-01`, source page 6 and section `MASY (kg)`.
Each active Jogger configuration receives exactly one value selected by its
explicit five- or seven-seat identity.

## Evidence boundary

- The source's `min` qualifier is preserved in the attribute definition and
  observation notes.
- No `kerb_weight` value is created from this row.
- No value is inferred from gross vehicle weight or payload.
- Payload ranges remain deferred rather than being collapsed to endpoints or
  averages.
- The completed scalar IDs 725-1036, injection IDs 1037-1068 and gearbox IDs
  1069-1106 remain independent and unchanged.

## Regression guarantees

Six dedicated tests require:

- the active integer `minimum_kerb_weight` contract;
- one strict 22-row specification and contiguous IDs 1107-1128;
- exactly one observation for every active Jogger configuration;
- exact powertrain and seating-value counts;
- absence of source-backed `kerb_weight` rows from the minimum-qualified row;
- registered source, page, section, text pairs and PDF SHA-256.

## Expected verified baseline

After materialization:

- 476 tests;
- 34 master CSV files and 3,753 rows;
- 1,128 dated configuration values;
- 65 declarative configuration-value import specifications;
- 1,811 equipment-availability records;
- 352 canonical attributes in 30 categories.

## Next package

**Jogger Cargo Measurement Modeling Review** will define separate VDA
measurement concepts for volume to parcel-shelf height and volume to seat-back
height before importing the 44 exact five-/seven-seat observations.
