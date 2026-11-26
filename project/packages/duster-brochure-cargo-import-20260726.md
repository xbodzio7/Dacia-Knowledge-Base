# Duster Brochure Cargo Value Import

Date: 2026-07-26
Status: complete

## Goal

Import only Duster cargo observations whose source column maps exactly to an active configuration by model, drive type, powertrain and transmission.

## Included

- 64 `boot_capacity` observations;
- 64 one-to-one cargo contexts;
- ten `brochure_technical_data_for` relationships;
- four Eco-G 120 4x2 manual configurations;
- three mild hybrid 140 4x2 manual configurations;
- three hybrid 155 4x2 automatic configurations.

## Context

Each observation preserves:

- VDA/ISO 3832 or ordinary-litre measurement basis;
- upright or folded second-row state;
- main luggage compartment or source-stated total;
- explicit repair-kit and spare-wheel presence state;
- empty third-row and double-floor qualifiers where the source does not state them.

## Excluded

- Eco-G 120 automatic configurations, because the brochure column is explicitly manual;
- hybrid-G 150 4x4 values, because no exact modeled Duster configuration exists;
- generic dimensions-page values, because the page does not identify an exact powertrain;
- historical Eco-G 100, mild hybrid 130 and hybrid 140 configurations.

## Verification

The importer is append-only and idempotent, verifies the archived brochure SHA-256, exact configuration identity, sequential IDs, source relationships and the absence of forbidden projections.
