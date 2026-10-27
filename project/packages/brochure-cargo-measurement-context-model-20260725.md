# Brochure Cargo Measurement Context Modeling

Date: 2026-07-25

## Purpose

Accept a minimal architecture for cargo-volume observations whose meaning depends on
measurement basis, seat-row state, compartment and equipment qualifiers.

## Decision

- Keep numeric values in `configuration_attribute_values.csv`.
- Use the existing neutral `boot_capacity` attribute for future context-rich imports.
- Add a separate optional one-to-one `configuration_cargo_volume_contexts.csv` relation
  in the next schema package.
- Preserve measurement basis and cargo-specific dynamic conditions in that relation.
- Preserve passenger layout and drive type through exact configuration identity.
- Retain existing specialized cargo attributes and observations without migration.

## Data impact

This package changes documentation, the machine-readable model contract and project
state only. It adds no master-data rows, no schema file and no brochure cargo value.

## Acceptance criteria

- architecture decision D-023 is recorded;
- the machine-readable contract exactly defines fields, dictionaries, inheritance and
  non-inference rules;
- the review explains accepted and rejected alternatives;
- project state selects a schema-foundation follow-up package;
- the complete repository test suite remains green.
