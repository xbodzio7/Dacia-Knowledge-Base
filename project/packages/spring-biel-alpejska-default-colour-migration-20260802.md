# Spring Essential Biel Alpejska Default Colour Migration

Package ID: `spring_biel_alpejska_default_colour_migration_001`

Status: complete

## Goal

Apply the exact-current Spring Essential Biel Alpejska default-colour state through the canonical declarative configuration-value importer and update only the supported commercial mapping.

## Delivered

- added the canonical scalar import specification `data/imports/configuration_values/spring_biel_alpejska_default_colour_20260802.json`;
- added `spring_essential_electric70_automatic_exterior_color_20260802` as `exterior_color = biel alpejska`;
- registered the exact-current commercial source relationship for Spring Essential;
- converted only `spring_colour_biel_alpejska__spring_essential_electric70_automatic` to `standard` at 0 PLN;
- set the observation and price date to 2026-08-02 with provenance `src_pl_spring_commercial_context_20260802`;
- generated deterministic JSON and Markdown migration reports.

## Preserved boundaries

- Expression Biel Alpejska remains optional with an unknown price and brochure-only provenance;
- Extreme Biel Alpejska remains optional with an unknown price and brochure-only provenance;
- all completed Type 2 and domestic-socket charging-cable representations remain unchanged;
- no new architecture or domain concept is introduced.

## Master-data delta

- configuration value rows added: 1;
- source-configuration relationship rows added: 1;
- commercial mapping rows updated: 1;
- commercial mapping rows added: 0;
- net master-row increase: 2;
- attributes, commercial items and sources added: 0.

## Verified baseline after migration

- master rows: 11729;
- configuration values: 3568;
- canonical configuration import specifications: 139;
- tests: 1793.

## Next package

`post_spring_biel_alpejska_priority_selection_review_001` selects the next bounded package without changing master data.
