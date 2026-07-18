# Duster Technical Specification Import

## Scope

This package imports source-explicit technical observations from pages 8 and 9 of the official Duster MY26/PY25 price list for all 24 catalogue configurations.

The import is generated from 33 versioned configuration-value specifications and adds 392 dated observations across 17 existing canonical attributes.

## Imported domains

- engine displacement, cylinder count and total valve count,
- combustion-engine power and torque with exact fuel context where the source distinguishes petrol and LPG,
- engine-speed points for maximum power and torque where an unambiguous integer is stated,
- top speed, 0-100 km/h acceleration and the page-8 standing kilometre,
- petrol and LPG tank capacities,
- combined WLTP CO2 emissions and fuel consumption,
- luggage volume without a spare wheel under ISO 3832,
- maximum braked trailer weight,
- separately stated traction-motor and HSG power for full hybrids.

## Evidence boundary

The package deliberately excludes trim-ambiguous masses, payload ranges and tyre alternatives; it also does not infer a driven axle from 4X2, duplicate gearbox facts, collapse hybrid component powers into system power or create a configuration for the unpriced hybrid-G 150 4x4 column.

No missing value, dash, range or alternative is converted into a single configuration-level fact.

## Dates and provenance

All rows reference src_pl_duster_price_my26_py25_20260206 and the registered source file hash.

General observations use 2026-02-06. The 20 page-9 WLTP consumption and CO2 observations use 2025-10-01, matching the explicit as-of statement printed below that table.

## Result

- 392 Duster technical observations,
- 702 total configuration values,
- 44 total versioned configuration-value specifications,
- 320 observations without fuel context,
- 36 petrol-context observations,
- 36 LPG-context observations,
- unchanged 24 Duster prices,
- unchanged seven-configuration Sandero reporting subset.
