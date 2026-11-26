# Bigster MY26 price list — 2026-10-01 technical scalar reconciliation

- Source: `src_pl_bigster_price_my26_20261001`
- Official URL: `https://cdn.group.renault.com/dac/pl/pdf/cenniki/bigster-price.pdf.asset.pdf/d477c604e8.pdf`
- Archived bytes: `owner_supplied/2026-10-01/d477c604e8.pdf`
- SHA-256: `0964b3a3311708698ef3cee6bd28244f76c1db36d0d9452e128e5113384dac97`
- Effective date: 2026-10-01
- Evidence: page 6 technical table. The canonical source record states that the full 8-page document was reconciled; this package materializes the page-6 scalar subset.

## Exact configurations

- `bigster_expression_mildhybridg140_4x2_automatic`
- `bigster_extreme_mildhybridg140_4x2_automatic`
- `bigster_journey_mildhybridg140_4x2_automatic`
- `bigster_expression_tribrid150_4x4_automatic`
- `bigster_extreme_tribrid150_4x4_automatic`
- `bigster_journey_tribrid150_4x4_automatic`

## Imported facts

Twenty-two declarative import specifications create 150 dated observations after the Tribrid 150 engine-power closure (PR #778) covering displacement, cylinder and total valve counts, explicitly separated engine power where unambiguous, torque and RPM, hybrid battery capacity/voltage, automatic gearbox type/gears, top speed, 0–100 km/h acceleration, standing kilometre, ISO 3832 luggage volumes, kerb/GVW/trailer masses, CO2, combined fuel consumption and fuel tank capacities. Each row preserves source date, page, section, exact configuration, source text and fuel type where applicable.

## Tribrid 150 engine-power closure and remaining boundaries

The page-6 table separates two rows:
- `Moc maksymalna`: the combustion engine is explicitly `103 (140)` at 5,000 rpm in the Tribrid 150 4x4 column.
- `Moc maksymalna (układ hybrydowy)`: the combined system is `103 (140) + 10 (13)`.

The three Tribrid 150 4x4 automatic configurations now have `engine_power=103 kW` (IDs 8231–8233), imported from the exact combustion-engine row. This closes the earlier source-to-master gap; do not reimport these observations. Closure: PR #778, commit `a856cfaf14bfc0fbccc1d10a4da8b2fda20ba704`.

The combined hybrid-system power remains deferred and is not normalized into `engine_power`. The separate electric-motor figures (36 kW, 205 Nm at 1,630 rpm) remain component-level evidence and are not flattened into engine-specific attributes without an approved component context. No values are inferred from the 2026-07-03 price list; it was consulted only for existing repository import conventions.

## Acceptance boundary

- all observations use source date 2026-10-01 and page-6 provenance;
- all six target configurations already have exact source relationships in `data/master/source_configurations.csv`;
- no price, equipment, colour or configurator facts are changed;
- full quality checks are required before merge.
