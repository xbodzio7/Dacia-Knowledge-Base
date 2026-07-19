# Jogger MY26 Page-6 Source Completion Review

## Status

`COMPLETE`

The accepted Polish Jogger MY26 page-6 technical source is complete for every fact that can be represented without changing its meaning.

## Source denominator

- source: `src_pl_jogger_price_my26_20260401`;
- market: Poland;
- observation date: `2026-04-01`;
- page: 6.

## Exact scalar coverage

The continuous configuration-value suffix `725-1204` contains 480 page-6 observations:

- 312 exact technical values;
- 32 injection-type values;
- 38 gearbox-type and gear-count values;
- 22 minimum kerb weights;
- 44 measurement-specific VDA cargo values;
- 20 LPG total and filling capacities;
- 6 total hybrid-system-power values;
- 6 controlled lithium-ion chemistry values.

Cargo measurement boundaries, LPG capacity concepts and hybrid component semantics remain separate.

## Range coverage

Range IDs `1-144` contain:

- 32 fuel-consumption ranges;
- 32 CO2 ranges;
- 22 seat-qualified payload ranges;
- 6 Hybrid acceleration ranges;
- 26 maximum-power RPM ranges;
- 26 maximum-torque RPM ranges.

All ranges preserve both endpoints, inclusive boundaries, dates, source references and fuel contexts where applicable. No midpoint or preferred endpoint is introduced.

## Deferred fact

The source states `200 V / 1.4 kWh` for Hybrid 155. The voltage is imported. The capacity remains deliberately absent because the source does not identify it as gross, nominal or usable, while the current `hybrid_battery_capacity` attribute explicitly means usable capacity.

This is a semantic deferral, not a missing-data gap.

## Result

The page-6 portfolio contains 624 source-backed observations:

- 480 scalar observations;
- 144 range observations;
- zero unsupported representative values;
- zero scalar/range semantic collisions;
- one documented basis-ambiguous deferred fact.

No further page-6 import package is selected.

## Next package

**Jogger Technical Reporting Scope Selection** will define the first bounded homogeneous reporting group without changing source data.
