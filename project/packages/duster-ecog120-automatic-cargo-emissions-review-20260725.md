# Duster Eco-G 120 Automatic Cargo and Emissions Gap Review — 2026-07-25

Status: complete

## Goal

Close the automatic-specific luggage-volume gap from the registered official Polish MY26 catalogue while preserving petrol CO2 as unknown when the source does not distinguish the value by fuel.

## Source

The package reuses the registered official Dacia Poland source:

- source code: `src_pl_duster_price_my26_20260703`;
- document: `PDF/Cenniki/DACIA DUSTER cennik MY26 20260703.pdf`;
- effective date: 2026-07-03;
- verified SHA-256: `40bb4f3db9019c500fcb4c759f5ad395aa3b35a68bb22aa74f031fefe09727f2`.

The price matrix explicitly identifies `Eco-G 120 auto`. Page 6 provides the corresponding luggage-compartment values and separates that automatic column from manual Eco-G 120 and the other powertrains.

## Imported observations

For each exact automatic configuration — Expression, Extreme and Journey — the package imports:

- `cargo_volume_without_spare_wheel_iso3832 = 439 dm3`;
- `maximum_cargo_volume_iso3832 = 1373 dm3`.

The six dated observations use the existing ISO 3832 attributes already established by the Bigster technical package. No generic boot-capacity or VDA value is synthesized.

## Emissions boundary

The same automatic column prints `123 g/km` but does not identify that value as petrol or LPG within the bi-fuel configuration. The repository already contains exact LPG CO2 from separate stock-card evidence. This package does not duplicate or reinterpret the catalogue figure and does not create a petrol CO2 observation.

## Reproducibility

Two declarative scalar specifications own IDs 1826–1831. `tools/import_duster_ecog120_automatic_cargo_20260725.py` verifies the registered PDF identity and page evidence, exact configuration coverage, source relationships, six scalar observations and the petrol-CO2 non-import boundary. It supports `--apply` and `--check`.

## Reporting

The Duster Eco-G 120 automatic completeness scope expands from 29 to 31 technical slots. Three configurations across 31 slots produce 93 present observations and zero missing observations. Petrol CO2 remains outside the denominator until exact fuel-specific evidence exists.
