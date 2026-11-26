# Jogger Hybrid System Semantics Review

## Status

`SELECTED`

The remaining Jogger Hybrid 155 page-6 evidence was reviewed against the
repository's current Hybrid System attributes, controlled-value files and
validation rules.

## Source evidence

The authoritative source is `src_pl_jogger_price_my26_20260401`, page 6. For
all six active Hybrid 155 configurations it states:

- `Łączna moc układu hybrydowego: 116 kW`;
- lithium-ion battery chemistry;
- `200 V / 1.4 kWh` battery voltage and capacity.

The 200 V observation is already present in the completed exact scalar
package.

## Selected package: total hybrid-system power

The source identifies 116 kW as total power of the complete hybrid system. It
must remain distinct from:

- combustion-engine power;
- traction-motor power;
- starter-generator power;
- any arithmetic sum of component observations.

The implementation will add one canonical attribute:

- code: `hybrid_system_power_total`;
- category: `Hybrid System`;
- name: `Total hybrid system power`;
- data type: `decimal`;
- unit: `kW`;
- meaning: source-stated total output of the complete hybrid propulsion system,
  not a calculated sum of component powers.

One strict declarative specification will materialize 6 observations of 116 kW
for all and only the active Hybrid 155 Jogger configurations, using the next
contiguous configuration-value IDs after 1192.

## Battery chemistry boundary

`hybrid_battery_type` already exists as an active enum attribute, but the
repository contains no controlled battery-chemistry file. Current reference
and status validators enumerate only the existing engine, fuel, injection,
emission, drive and transmission dictionaries; no battery dictionary or
attribute-to-dictionary contract exists.

Importing `lithium-ion` would therefore require a new controlled-value mapping
and validation decision, not merely another configuration observation. That
architecture extension remains outside this bounded package.

## Battery capacity boundary

The source states 1.4 kWh but does not identify whether it is gross, nominal or
usable capacity. The existing `hybrid_battery_capacity` attribute is explicitly
defined as usable capacity. The value is not imported and is not reinterpreted.

## Selected denominator

| Group | Configurations | Value | Observations |
| --- | ---: | ---: | ---: |
| Hybrid 155 five-seat | 3 | 116 kW | 3 |
| Hybrid 155 seven-seat | 3 | 116 kW | 3 |
| **Total** | **6** | **116 kW** | **6** |

## Acceptance criteria

- one active decimal `Hybrid System` attribute using existing unit `kW`;
- one strict 6-row specification and contiguous IDs 1193-1198;
- all and only the six active Hybrid 155 configurations;
- no component power rewritten or summed;
- no battery chemistry or 1.4 kWh observation;
- registered source hash, page and exact source-text contract;
- full cross-platform Quality before merge.

## Remaining architecture boundary

After this bounded implementation, remaining Jogger evidence requires explicit
architecture decisions:

- battery chemistry controlled-value mapping;
- gross, nominal and usable battery-capacity semantics;
- interval representation for WLTP consumption, CO2, payload, acceleration and
  engine-speed ranges.
