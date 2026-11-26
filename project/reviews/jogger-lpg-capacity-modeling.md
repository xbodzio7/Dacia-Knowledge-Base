# Jogger LPG Capacity Modeling Review

## Status

`SELECTED`

The Jogger MY26 page-6 fuel-capacity row contains three distinct concepts for
Eco-G configurations: a 50 L petrol tank, a 50 L total LPG vessel volume and a
40 L LPG filling volume. The petrol value is already represented by
`fuel_tank_capacity` with `fuel_type_code=lpg` deliberately absent and
`fuel_type_code=petrol` explicitly present.

## Source evidence

The authoritative source is `src_pl_jogger_price_my26_20260401`, page 6. For
all Eco-G 120 manual and automatic columns it states:

- `Ben: 50` for petrol;
- `LPG całkowita pojemność/pojemność napełniania: 50/40`.

The slash-separated LPG pair is not one interchangeable tank-capacity value.
It identifies total pressure-vessel volume and the smaller volume permitted for
filling.

## Selected canonical attributes

### `lpg_vessel_capacity_total`

- category: `Capacities`;
- name: `Total LPG vessel capacity`;
- data type: `decimal`;
- unit: `L`;
- meaning: total internal capacity of the LPG pressure vessel.

### `lpg_vessel_filling_capacity`

- category: `Capacities`;
- name: `LPG vessel filling capacity`;
- data type: `decimal`;
- unit: `L`;
- meaning: source-stated LPG volume available or permitted for filling,
  distinct from total vessel volume.

Both observation sets will use `fuel_type_code=lpg`.

## Selected import denominator

The repository contains 10 active Eco-G Jogger configurations:

| Group | Configurations | Total-vessel rows | Filling rows | Total |
| --- | ---: | ---: | ---: | ---: |
| Eco-G 120 manual | 6 | 6 × 50 L | 6 × 40 L | 12 |
| Eco-G 120 automatic | 4 | 4 × 50 L | 4 × 40 L | 8 |
| **Total** | **10** | **10** | **10** | **20** |

The implementation will add two strict declarative specifications using the
next contiguous configuration-value IDs after 1172.

## Existing-value boundary

- Existing petrol `fuel_tank_capacity=50 L` observations remain unchanged.
- No LPG row is added to generic `fuel_tank_capacity` from the `50/40` pair.
- Total vessel capacity and filling capacity are never collapsed or ranked.
- TCe 110 and Hybrid 155 configurations receive no LPG-capacity observations.
- No value is derived from the common 80% LPG filling rule; the source states
  both 50 and 40 directly.

## Acceptance criteria

- two active decimal attributes in `Capacities` using the existing `L` unit;
- two strict 10-row specifications and 20 exact observations;
- LPG context on every new observation;
- exact 50/40 values for all and only the 10 active Eco-G configurations;
- unchanged petrol tank observations and no generic LPG tank rows;
- registered source hash, page and exact source-text contracts;
- full cross-platform Quality before merge.

## Next package after implementation

**Jogger Hybrid System Semantics Review** will assess source-stated total system
power and lithium-ion chemistry. The 1.4 kWh battery value remains outside that
package unless its gross, nominal or usable basis can be resolved without
reinterpretation.
