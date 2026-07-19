# Jogger Payload and Performance Range Selection

## Status

`SELECTED`

The remaining interval evidence on page 6 of the accepted Polish Jogger MY26 source was reviewed after the first production range import. All selected facts fit the existing configuration-value range architecture and existing active numeric attributes.

## Source denominator

The authoritative source is `src_pl_jogger_price_my26_20260401`, page 6. The selected rows are:

- `ładowność (kg) 5-m / 7-m` in section `MASY (kg)`;
- Hybrid 155 `0–100 km/h` range `8,9-9,0` in section `OSIĄGI`;
- maximum-power and maximum-torque engine-speed ranges in section `SILNIKI`.

No endpoint is converted into a scalar value or midpoint.

## Selected package

Eleven strict import specifications will create 80 closed ranges using the next contiguous range IDs `65-144`.

### Maximum payload — 22 ranges, IDs 65-86

| Powertrain | 5-seat range | 7-seat range | Configurations | IDs |
| --- | ---: | ---: | ---: | --- |
| Eco-G 120 manual | 453-473 kg | 598-619 kg | 6 | 65-70 |
| Eco-G 120 automatic | 450-459 kg | 596-606 kg | 4 | 71-74 |
| TCe 110 manual | 455-492 kg | 594-634 kg | 6 | 75-80 |
| Hybrid 155 automatic | 457-471 kg | 595-612 kg | 6 | 81-86 |

The existing active integer attribute `maximum_payload` with unit `kg` is source-equivalent. Each configuration receives the range matching its explicit five- or seven-seat identity.

### Hybrid 155 acceleration — 6 ranges, IDs 87-92

The source gives one group-level Hybrid 155 range `8.9-9.0 s` in the row labelled `0–100 km/h (s) 5-m. / 7-m.` without assigning either endpoint to a seat count. The range will therefore be preserved unchanged for all six active Hybrid 155 configurations using the existing decimal attribute `acceleration_0_100`; no five-/seven-seat endpoint inference is made.

### Engine-speed ranges — 52 ranges, IDs 93-144

| Group and attribute | Fuel context | Range | Configurations | Observations | IDs |
| --- | --- | ---: | ---: | ---: | --- |
| Eco-G 120 manual `max_power_rpm` | LPG | 4500-5000 rpm | 6 | 6 | 93-104 shared spec |
| Eco-G 120 manual `max_power_rpm` | petrol | 4500-5750 rpm | 6 | 6 | 93-104 shared spec |
| Eco-G 120 manual `max_torque_rpm` | LPG | 1750-3750 rpm | 6 | 6 | 105-116 shared spec |
| Eco-G 120 manual `max_torque_rpm` | petrol | 2000-4000 rpm | 6 | 6 | 105-116 shared spec |
| Eco-G 120 automatic `max_power_rpm` | LPG | 4500-5000 rpm | 4 | 4 | 117-124 shared spec |
| Eco-G 120 automatic `max_power_rpm` | petrol | 4500-5750 rpm | 4 | 4 | 117-124 shared spec |
| Eco-G 120 automatic `max_torque_rpm` | LPG | 1750-3750 rpm | 4 | 4 | 125-132 shared spec |
| Eco-G 120 automatic `max_torque_rpm` | petrol | 2000-4000 rpm | 4 | 4 | 125-132 shared spec |
| TCe 110 manual `max_power_rpm` | petrol | 5000-5250 rpm | 6 | 6 | 133-138 |
| TCe 110 manual `max_torque_rpm` | petrol | 2900-3500 rpm | 6 | 6 | 139-144 |

The existing active integer attributes `max_power_rpm` and `max_torque_rpm`, both with unit `rpm`, preserve the source meaning. Eco-G observations keep separate `lpg` and `petrol` contexts. TCe 110 uses `petrol`.

## Specification plan

The implementation will add:

1. four `maximum_payload` specifications, one per powertrain/transmission group;
2. one Hybrid 155 `acceleration_0_100` specification;
3. six engine-speed specifications: maximum power and torque for Eco-G manual, Eco-G automatic and TCe 110.

Every specification will use observation date `2026-04-01`, the registered source code, page 6, its exact source section and inclusive endpoints.

## Existing-data boundary

- Range IDs `1-64` from the WLTP efficiency package remain unchanged.
- All 1,204 scalar configuration values remain unchanged.
- The exact Hybrid combustion-engine `max_torque_rpm = 3000` observation remains scalar and is not replaced.
- The Hybrid traction-motor torque speed `7000 rpm` is not imported into the combustion-engine RPM attributes.
- No range is added for exact scalar values, cargo measurements, LPG capacities or battery capacity.

## Acceptance criteria

- exactly 11 new strict range specifications;
- exactly 80 new ranges with contiguous IDs `65-144`;
- 22 seat-qualified `maximum_payload` ranges;
- 6 unchanged Hybrid 155 acceleration ranges;
- 52 fuel-context-preserving engine-speed ranges;
- no scalar/range semantic collision;
- registered PDF hash and page-6 source text verified;
- canonical range counters become 144 values and 19 specifications;
- full cross-platform Quality before merge.

## Next package

**Jogger Payload and Performance Range Modeling and Import** will materialize this selected denominator without changing scalar observations.
