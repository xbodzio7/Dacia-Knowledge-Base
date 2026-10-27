# Jogger Range and Qualifier Modeling Review

## Status

`SELECTED`

The remaining Jogger MY26 page-6 evidence was reviewed against the current
configuration-value model after completing the exact scalar, injection-type and
gearbox packages.

## Source denominator

The authoritative source is `src_pl_jogger_price_my26_20260401`, page 6,
section `MASY (kg)` and the adjacent technical sections. The review preserves
all source qualifiers and does not convert intervals into point estimates.

## Selected package: minimum kerb weight

The row `masa własna min (kg) 5-m / 7-m` gives one exact minimum value for each
powertrain and seating configuration:

| Powertrain | 5-seat | 7-seat | Active configurations |
| --- | ---: | ---: | ---: |
| Eco-G 120 manual | 1292 kg | 1321 kg | 6 |
| Eco-G 120 automatic | 1326 kg | 1354 kg | 4 |
| TCe 110 manual | 1193 kg | 1221 kg | 6 |
| Hybrid 155 automatic | 1359 kg | 1388 kg | 6 |
| **Total** | - | - | **22** |

The implementation will:

- add one active integer `minimum_kerb_weight` attribute in category `Weights`
  with unit `kg`;
- keep it distinct from the existing unqualified `kerb_weight` attribute;
- materialize exactly 22 dated observations, one per active Jogger
  configuration, using the configuration's explicit five- or seven-seat
  identity;
- preserve source page, section and the `min` qualifier in the attribute
  definition and observation notes;
- use the next contiguous configuration-value IDs after 1106.

This is the smallest complete package that retains the source meaning without a
new interval representation or measurement-context architecture.

## Deferred exact measurement packages

### Cargo measurements

The source gives two different VDA boundaries for every configuration:

- to parcel-shelf height: 708 L for five-seat and 160 L for seven-seat;
- to seat-back height: 607 L for five-seat and 506 L for seven-seat.

These values must not be collapsed into generic `boot_capacity` or
`cargo_volume_vda`. A later package should introduce two measurement-specific
attributes and 44 exact observations.

### LPG capacities

Each Eco-G configuration states `całkowita pojemność/pojemność napełniania:
50/40`. A later package should represent total LPG vessel capacity and filling
capacity as two separate attributes, with petrol 50 L remaining in the existing
`fuel_tank_capacity` observations.

### Hybrid semantics

Hybrid 155 states:

- total hybrid-system power: 116 kW;
- battery chemistry: lithium-ion;
- voltage/capacity: 200 V / 1.4 kWh.

The 200 V value is already imported. Total system power requires a dedicated
hybrid-system attribute. Battery chemistry may reuse the controlled enum after
verification. The 1.4 kWh value remains deferred because the source does not
state whether the capacity is gross, nominal or usable, while the current
`hybrid_battery_capacity` attribute is explicitly defined as usable capacity.

## Deferred interval architecture

The following evidence remains outside the scalar value model:

- Eco-G, TCe and Hybrid WLTP fuel-consumption ranges;
- CO2-emission ranges;
- five-/seven-seat maximum-payload ranges;
- Hybrid 155 0-100 km/h range `8.9-9.0`;
- Eco-G and TCe power- and torque-speed ranges.

No endpoint is imported as a representative value. A later architecture review
must choose an explicit interval representation, endpoint semantics and
comparison behavior before any of these rows can enter master data.

## Decision order

1. Minimum kerb weight modeling and import.
2. Cargo measurement semantics.
3. LPG total and filling capacities.
4. Hybrid system power and battery chemistry.
5. Interval architecture decision for all remaining ranges.

## Acceptance criteria for the selected package

- one new canonical attribute and no new category or unit;
- 22 source-backed configuration observations;
- exact five-/seven-seat mapping for all four powertrain groups;
- no `kerb_weight` rows from the minimum-qualified source row;
- unchanged exact scalar IDs 725-1036, injection IDs 1037-1068 and gearbox IDs
  1069-1106;
- registered PDF hash and page-6 source evidence verified by tests;
- full cross-platform Quality before merge.
