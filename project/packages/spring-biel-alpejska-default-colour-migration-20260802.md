# Spring Essential Biel Alpejska Default Colour Migration

Package ID: `spring_biel_alpejska_default_colour_migration_001`

Status: complete

## Goal

Apply the exact-current Spring Essential Biel Alpejska default-colour state using the existing repository representation approved by the preceding review.

## Delivered

- added the canonical scalar import specification `data/imports/configuration_values/spring_biel_alpejska_default_colour_20260802.json`;
- added `spring_essential_electric70_automatic_exterior_color_20260802` as a direct `exterior_color = biel alpejska` value;
- converted only `spring_colour_biel_alpejska__spring_essential_electric70_automatic` from an unresolved optional relationship to `standard` at 0 PLN;
- set the observation and price date to 2026-08-02 and the provenance to `src_pl_spring_commercial_context_20260802`;
- generated deterministic JSON and Markdown migration reports.

## Preserved boundaries

- Expression Biel Alpejska remains optional with an unknown price and brochure-only provenance;
- Extreme Biel Alpejska remains optional with an unknown price and brochure-only provenance;
- all three Type 2 mappings remain optional and unchanged;
- no Type 2 or home charging-cable attribute, item or mapping is added;
- no new architecture or domain concept is introduced.

## Master-data delta

- configuration value rows added: 1;
- commercial mapping rows updated: 1;
- commercial mapping rows added: 0;
- net master-row increase: 1;
- attributes, items and sources added: 0.

## Verified baseline after migration

- master rows: 11715;
- configuration values: 3568;
- canonical configuration import specifications: 139;
- tests: 1788.

## Architecture boundary

Further charging-cable work requires an explicit canonical model decision. Type 2 and home charging cables are independently supplied concepts that may coexist and have different standard or optional states. No cable mutation is authorized by this package.
