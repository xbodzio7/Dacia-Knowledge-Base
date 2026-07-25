# Duster Eco-G 120 Automatic Homologation Evidence — 2026-07-25

Status: complete

## Goal

Replace the deliberately incomplete automatic Duster technical scope with exact automatic-specific evidence while preserving every unresolved value as unknown rather than inheriting manual homologation data.

## Sources

The package registers two dated official-web snapshots:

- three exact Dacia Romania 2026 `ECO-G 120 auto, 2WD` stock pages for Expression, Extreme and Journey;
- three matching Dacia Poland exact Eco-G 120 automatic stock pages for supplementary LPG WLTP CO2 and source-stated fuel-tank capacity.

The Romanian market remains explicit in source provenance. No Romanian price, equipment availability or market-specific commercial state is transferred to the Polish configurations.

## Scalar observations

The package adds 60 dated scalar configuration observations, 20 for each exact automatic configuration:

- LPG and petrol engine power: 90 and 84 kW;
- LPG and petrol torque: 200 and 190 Nm;
- six forward ratios;
- maximum speed: 180 km/h;
- 0–100 km/h: 11.7 s on LPG and 11.4 s on petrol;
- standing kilometre: 33.6 s on LPG and 33.3 s on petrol;
- turning circle: 10.96 m;
- gross vehicle weight: 1805 kg;
- gross train weight: 3305 kg;
- braked trailer weight: 1500 kg;
- unbraked trailer weight: 715 kg;
- roof load: 80 kg;
- combined consumption: 7.6 l/100 km on LPG and 6.2 l/100 km on petrol;
- LPG WLTP CO2: 123 g/km;
- source-stated fuel-tank capacity: 51 L.

## Range observations

The package adds 18 closed source-stated ranges:

- maximum-power speed: LPG 4500–5000 rpm and petrol 4500–5750 rpm;
- maximum-torque speed: LPG and petrol 1750–4000 rpm;
- empty/kerb mass: 1358–1381 kg;
- payload with a 75 kg driver: 454–477 kg.

Endpoints are preserved exactly. The importer does not select one endpoint, average them or derive payload from other mass fields.

## Remaining unknowns

Automatic-specific luggage volume remains unimported. None of the six exact automatic pages states a canonical VDA or ISO luggage-volume value, so manual cargo figures are not inherited.

Petrol CO2 also remains unknown because the exact Polish cards expose only the LPG WLTP CO2 value.

## Reproducibility

`tools/import_duster_ecog120_automatic_homologation_20260725.py` verifies both snapshot SHA-256 values, exact configuration and trim coverage, active attributes and units, fuel contexts, 60 scalar observations, 18 ranges and the cargo non-import boundary. `--apply` owns only records attached to the two new source codes; `--check` reproduces the normalized contract without mutation.
