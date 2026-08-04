# Cross-model Configurator Commercial Data Migration

## Package

- Package ID: `cross_model_configurator_commercial_data_migration_001`
- Kind: `source_backed_commercial_observation_migration`
- Status: complete
- Source date: 2026-08-04

## Result

Persisted exact page-2 commercial observations for all 18 saved configurator states: displayed catalogue price, base colour and its price, wheel designation and its price, upholstery designation and its price.

Every record is keyed by the configurator code. All selected colour, wheel and upholstery prices are zero in the supplied saved states.

## Boundary

The package does not promote the observations into canonical master rows because Sandero F.2, Sandero Stepway F.2 and the new Jogger require explicit canonical entity creation or mapping. The exact observations are retained without propagation across grade, powertrain, transmission, seat-count or phase boundaries.

## Next package

`cross_model_configurator_standard_equipment_migration_001` will migrate the exact standard-equipment lists from the dedicated equipment pages while preserving the same identity boundaries.
