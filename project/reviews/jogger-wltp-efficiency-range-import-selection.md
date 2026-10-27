# Jogger WLTP Efficiency Range Import Selection

## Status

`SELECTED`

This review selects the first source-data package using the approved separate
range-observation architecture. The source is the registered Polish Jogger MY26
price list `src_pl_jogger_price_my26_20260401`, page 6, section `OSIĄGI`.

## Source interpretation

The page-6 table has four homogeneous powertrain columns. The row labelled
`Cykl mieszany (l/100 km)` contains combined WLTP fuel-consumption ranges, while
`Emisja CO2 (g/km)` contains combined WLTP CO2 ranges. Every range uses two
explicit endpoints separated by a hyphen. Both endpoints will be stored as
inclusive; no average, midpoint, preferred value or trim-specific variation is
inferred.

The existing canonical attributes are reused:

- `fuel_consumption_combined`, decimal, `l/100 km`;
- `co2_emissions`, decimal, `g/km`.

## Selected source values

| Powertrain | Fuel context | Consumption | CO2 |
| --- | --- | --- | --- |
| Eco-G 120 manual | `lpg` | 7.3-7.4 l/100 km | 119-121 g/km |
| Eco-G 120 manual | `petrol` | 5.8-5.9 l/100 km | 133-134 g/km |
| Eco-G 120 automatic | `lpg` | 7.5-7.6 l/100 km | 121-123 g/km |
| Eco-G 120 automatic | `petrol` | 6.0-6.1 l/100 km | 137-138 g/km |
| TCe 110 manual | `petrol` | 5.7-5.8 l/100 km | 129-131 g/km |
| Hybrid 155 automatic | `petrol` | 4.5-4.6 l/100 km | 103-104 g/km |

The source labels Eco-G values explicitly as LPG and petrol (`Ben`). TCe 110 and
Hybrid 155 are petrol powertrains, so their observations use the existing
`petrol` fuel context rather than an empty context.

## Configuration denominator

| Group | Configurations | Range slots per configuration | Observations |
| --- | ---: | ---: | ---: |
| Eco-G 120 manual | 6 | 4 | 24 |
| Eco-G 120 automatic | 4 | 4 | 16 |
| TCe 110 manual | 6 | 2 | 12 |
| Hybrid 155 automatic | 6 | 2 | 12 |
| **Total** | **22** | - | **64** |

The Eco-G slots are consumption and CO2 for each of `lpg` and `petrol`. TCe and
Hybrid each receive one petrol consumption range and one petrol CO2 range.
Five- and seven-seat configurations share the same source-column ranges because
the source does not split these rows by seating capacity.

## Declarative package shape

The implementation will use eight strict range-import specifications:

1. Eco-G 120 manual consumption — 12 rows;
2. Eco-G 120 manual CO2 — 12 rows;
3. Eco-G 120 automatic consumption — 8 rows;
4. Eco-G 120 automatic CO2 — 8 rows;
5. TCe 110 manual consumption — 6 rows;
6. TCe 110 manual CO2 — 6 rows;
7. Hybrid 155 automatic consumption — 6 rows;
8. Hybrid 155 automatic CO2 — 6 rows.

Range IDs will form the first contiguous suffix `1-64`. Every row will use
observation date `2026-04-01`, page 6, the registered source code, exact source
text and closed endpoint flags.

## Evidence boundary

This package excludes:

- payload ranges, which depend on seat count and belong to a separate package;
- Hybrid 155 acceleration `8.9-9.0 s`;
- maximum-power and maximum-torque RPM ranges;
- the unqualified 1.4 kWh battery capacity;
- any summary range from the page footer, because the detailed powertrain rows
  are the authoritative denominator.

No scalar configuration value is created or replaced.

## Acceptance criteria

- exactly 64 range observations and eight specifications;
- IDs `1-64` with no gaps;
- all and only the 22 active Jogger configurations;
- exact fuel contexts and closed endpoints;
- no scalar/range semantic collision;
- source PDF hash and page-6 text verification;
- completeness and source coverage recognize all imported ranges;
- pairwise reporting preserves identical, overlapping and disjoint semantics;
- full cross-platform Quality before merge.

## Next package

**Jogger WLTP Efficiency Range Modeling and Import** will materialize the eight
selected specifications. Payload, acceleration and RPM ranges remain separate
follow-up packages.
