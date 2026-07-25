# Brochure Cargo Context Schema Foundation

Date: 2026-07-25

## Purpose

Implement the schema and validation surfaces accepted in D-023 without importing any
brochure cargo observation.

## Delivered schema

- header-only `data/master/configuration_cargo_volume_contexts.csv`;
- `cargo_measurement_bases.csv`;
- `cargo_seat_states.csv`;
- `cargo_compartment_types.csv`;
- `context_presence_states.csv`.

The relation references one existing configuration value and preserves measurement
basis, second- and third-row state, compartment and independent spare-wheel, repair-kit
and double-floor qualifiers.

## Validation

- eight cross-file reference rules;
- four active-status rules for the controlled dictionaries;
- one-to-one semantic cardinality by referenced value;
- rejection of contexts attached to attributes other than `boot_capacity`;
- automatic SQLite and data-dictionary discovery.

## Data impact

The four dictionaries add eleven controlled rows. The cargo-context relation remains
empty. Configuration values, value ranges, availability, prices and source mappings are
unchanged.

## Acceptance criteria

- 46 master CSV files and 8156 master rows;
- zero cargo-context observations;
- 1831 configuration values remain unchanged;
- complete validation and SQLite coverage;
- next work is context-aware reporting before brochure values are imported.
