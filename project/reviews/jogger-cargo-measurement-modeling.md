# Jogger Cargo Measurement Modeling Review

## Status

`SELECTED`

The Jogger MY26 page-6 luggage-compartment evidence contains two independently
qualified VDA measurements. They cannot be represented faithfully by the
existing generic `boot_capacity` or `cargo_volume_vda` attributes.

## Source evidence

The authoritative source is `src_pl_jogger_price_my26_20260401`, page 6,
section `BAGAŻNIK`.

It states two five-/seven-seat pairs for every powertrain:

| Source measurement boundary | 5-seat | 7-seat |
| --- | ---: | ---: |
| to luggage-cover height (`do wysokości rolety`) | 708 dm³ | 160 dm³ |
| to seat-back height (`do wysokości oparcia`) | 607 dm³ | 506 dm³ |

The source explicitly identifies both rows as VDA measurements. One cubic
decimetre is represented using the repository's existing litre unit, as in the
current `cargo_volume_vda` contract.

## Selected canonical attributes

### `cargo_volume_vda_to_luggage_cover`

- category: `Capacities`;
- name: `Cargo volume VDA to luggage-cover height`;
- data type: `integer`;
- unit: `L`;
- meaning: luggage-compartment volume measured according to VDA up to the
  source-stated luggage-cover or roller-blind height.

### `cargo_volume_vda_to_seatback`

- category: `Capacities`;
- name: `Cargo volume VDA to seat-back height`;
- data type: `integer`;
- unit: `L`;
- meaning: luggage-compartment volume measured according to VDA up to the
  source-stated seat-back height.

Both attributes are measurement-specific and remain distinct from:

- `boot_capacity`, whose definition does not state a VDA method or height;
- `cargo_volume_vda`, whose definition states VDA but not the vertical boundary.

No existing observation is rewritten or reinterpreted.

## Selected import denominator

All 22 active Jogger configurations receive both values:

| Seating identity | Configurations | Luggage-cover rows | Seat-back rows | Total |
| --- | ---: | ---: | ---: | ---: |
| 5-seat | 11 | 11 × 708 L | 11 × 607 L | 22 |
| 7-seat | 11 | 11 × 160 L | 11 × 506 L | 22 |
| **Total** | **22** | **22** | **22** | **44** |

The implementation will use two strict declarative specifications and the next
contiguous configuration-value IDs after 1128.

## Evidence boundary

- Values are selected only from explicit five-/seven-seat configuration
  identity; no trim or powertrain difference is inferred.
- The two vertical boundaries are never collapsed to one generic volume.
- No arithmetic conversion, maximum selection or preferred-value ranking is
  performed.
- Generic `boot_capacity` and `cargo_volume_vda` remain unchanged.
- The completed scalar, injection, gearbox and minimum-weight ID ranges remain
  independent.

## Acceptance criteria

- two active integer attributes in `Capacities`, using the existing `L` unit;
- two strict specifications and 44 exact observations;
- exact 11/11 five-/seven-seat coverage per attribute;
- no new generic cargo-volume observations from the two qualified rows;
- registered source hash, page, section and exact source-text contracts;
- full cross-platform Quality before merge.

## Next package after implementation

**Jogger LPG Capacity Modeling Review** will separate total LPG vessel capacity
from permitted filling capacity before importing the source-stated 50/40 L
pairs for the 10 active Eco-G configurations.
