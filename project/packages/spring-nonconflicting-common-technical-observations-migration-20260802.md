# Spring Non-conflicting Common Technical Observations Migration

Package ID: `spring_nonconflicting_common_technical_observations_migration_001`

Status: **complete**

## Goal

Materialize only the 36 observations approved by the preceding source-to-master review: twelve common brochure facts for each of the three exact active Spring configurations.

## Data delivered

- controlled `electric_motor_type` domain with `permanent_magnet_synchronous`;
- controlled `traction_battery_type` mapping to the shared battery chemistry domain with `lithium_iron_phosphate`;
- electric power steering;
- nine common page-21 dimensions;
- 36 source-dated configuration values using contiguous IDs 3569-3604;
- one declarative 36-row specification, deterministic importer, migration report and regression contract.

## Evidence boundary

All imported values come from the exact SHA-256-pinned 2026-02-19 Polish Spring brochure. The package does not promote:

- 204 kg battery mass or 354 V from the MY2025 stock-only price list;
- the unqualified 24.3 kWh capacity;
- charging times;
- range or maximum speed already represented elsewhere;
- the 15-inch-wheel-only ground-clearance value.

## Verification

```bash
python tools/import_spring_nonconflicting_common_technical_20260219.py --verify
python -m unittest tests.test_spring_nonconflicting_common_technical_observations_migration_20260802
python tools/dkb.py project-state --check
python tools/dkb.py quality --concise
```

## Handoff

The next package is `spring_legacy_pdf_assimilation_closure_001`, a bounded closure audit confirming that both fully assimilated Spring PDFs have no remaining eligible untracked observations and that every preserved deferral remains explicit.
