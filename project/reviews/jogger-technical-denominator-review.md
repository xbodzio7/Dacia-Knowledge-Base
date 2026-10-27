# Jogger Technical Denominator Review

## Decision status

`SELECTED`

The accepted Polish Jogger MY26 source contains one page-6 technical table for
four powertrain/transmission groups. The table is not trim-specific, but every
active Jogger configuration belongs unambiguously to one group and one explicit
five- or seven-seat variant.

The first technical import will therefore use separate source-stated
denominators per homogeneous group and will create only exact scalar
configuration observations supported by the table.

## Catalogue groups

| Group | Configurations | Exact slots per configuration | Planned observations |
| --- | ---: | ---: | ---: |
| Eco-G 120 manual | 6 | 15 | 90 |
| Eco-G 120 automatic | 4 | 15 | 60 |
| TCe 110 manual | 6 | 12 | 72 |
| Hybrid 155 automatic | 6 | 15 | 90 |
| **Total** | **22** | — | **312** |

The six Eco-G manual configurations comprise Essential, Expression and Extreme
in five- and seven-seat form. Eco-G automatic comprises Extreme and Journey;
TCe 110 and Hybrid 155 each comprise Expression, Extreme and Journey in both
seat counts.

## Selected exact denominator

### Eco-G 120 manual and automatic — 15 slots

- `emission_standard`
- `engine_displacement`
- `cylinder_count`
- `total_valve_count`
- `engine_power` with separate `lpg` and `petrol` contexts
- `engine_torque` with separate `lpg` and `petrol` contexts
- `start_stop_system`
- `top_speed`
- `acceleration_0_100` with separate `lpg` and `petrol` contexts and the
  configuration's explicit seat count
- `fuel_tank_capacity` for the separately stated petrol tank only
- `gross_vehicle_weight` using the explicit five-/seven-seat value
- `braked_trailer_weight`

The LPG line states both total capacity and permitted filling capacity (`50/40`).
It is not collapsed into one generic `fuel_tank_capacity` value.

### TCe 110 manual — 12 slots

- `emission_standard`
- `engine_displacement`
- `cylinder_count`
- `total_valve_count`
- `engine_power`
- `engine_torque`
- `start_stop_system`
- `top_speed`
- `acceleration_0_100` using the explicit five-/seven-seat value
- `fuel_tank_capacity`
- `gross_vehicle_weight` using the explicit five-/seven-seat value
- `braked_trailer_weight`

### Hybrid 155 automatic — 15 slots

- `emission_standard`
- `engine_displacement` for the combustion engine
- `cylinder_count` for the combustion engine
- `total_valve_count` for the combustion engine
- `engine_power` for the combustion engine
- `engine_torque` for the combustion engine
- `max_torque_rpm` for the combustion engine
- `traction_motor_power`
- `starter_generator_power`
- `traction_motor_torque`
- `hybrid_battery_voltage`
- `top_speed`
- `fuel_tank_capacity`
- `gross_vehicle_weight` using the explicit five-/seven-seat value
- `braked_trailer_weight`

The separately stated 116 kW system power is not written to `engine_power`.
The combustion engine remains 80 kW, while the traction motor and HSG retain
separate values.

## Exact source values selected

| Item | Eco-G 120 | Eco-G 120 auto | TCe 110 | Hybrid 155 |
| --- | --- | --- | --- | --- |
| Emission standard | Euro 6e BIS | Euro 6e BIS | Euro 6e BIS | Euro 6e BIS |
| Displacement | 1199 cm³ | 1199 cm³ | 999 cm³ | 1789 cm³ |
| Cylinders / valves | 3 / 12 | 3 / 12 | 3 / 12 | 4 / 16 |
| Engine power | LPG 90 kW; petrol 84 kW | LPG 90 kW; petrol 84 kW | 81 kW | 80 kW |
| Engine torque | LPG 197 Nm; petrol 190 Nm | LPG 197 Nm; petrol 190 Nm | 200 Nm | 172 Nm |
| Top speed | 180 km/h | 180 km/h | 180 km/h | 180 km/h |
| 0–100 km/h, 5 / 7 seats | LPG 10.9 / 11.0 s; petrol 11.9 / 12.0 s | LPG 10.4 / 10.7 s; petrol 11.4 / 11.7 s | 10.5 / 11.2 s | range only; deferred |
| Petrol tank | 50 L | 50 L | 50 L | 50 L |
| Gross vehicle weight, 5 / 7 seats | 1765 / 1940 kg | 1785 / 1960 kg | 1685 / 1855 kg | 1830 / 2000 kg |
| Braked trailer | 1200 kg | 1200 kg | 1200 kg | 1000 kg |

Hybrid 155 additionally states combustion-engine maximum torque at 3000 rpm,
traction-motor power 36 kW, HSG power 15 kW, traction-motor torque 205 Nm and
hybrid-battery voltage 200 V.

## Deferred evidence

The following source content is intentionally not part of the scalar import:

- fuel-consumption and CO2 ranges for every group;
- payload ranges for every group and seat count;
- the Hybrid 155 acceleration range `8.9–9.0` without a seat assignment;
- minimum kerb weights, because the existing `kerb_weight` attribute does not
  preserve the source's explicit minimum qualifier;
- the two separate VDA cargo measurements, one to roller height and one to
  seat-back height, because the existing generic cargo attributes do not retain
  that measurement boundary;
- the LPG `50/40` total/filling-capacity pair;
- Hybrid 155 system power, because no canonical attribute distinguishes total
  system power from combustion-engine power;
- hybrid-battery chemistry and 1.4 kWh capacity, because the current enum and
  `usable` capacity semantics are not source-equivalent;
- gearbox type and gear count, pending reconciliation with the current gearbox
  entities and model associations;
- injection type, pending a controlled mapping of Polish `pośredni` to the
  existing injection enum;
- maximum-power and maximum-torque RPM ranges for Eco-G 120 and TCe 110.

A deferred value is not missing and must not become `0`, a midpoint, a bound or
an inferred trim-specific value.

## Master-entity boundary

The existing `eco_g100_2025` engine entity describes a different 999 cm³,
100-horsepower generation and cannot represent this 1199 cm³ Eco-G 120 source.
The existing Hybrid 155 entity also mixes aggregate powertrain semantics that
must not overwrite the table's separate 116 kW system, 80 kW combustion-engine,
36 kW traction-motor and 15 kW HSG values.

This package therefore does not modify engine or gearbox master entities. The
selected facts are dated configuration observations with exact source text and
page provenance.

## Next package

**Selected Jogger Technical Specification Import** will materialize 312 dated
configuration values in 17 declarative import specifications, verify the
repository-local PDF by SHA-256 and preserve every excluded range and modelling
boundary documented above.
