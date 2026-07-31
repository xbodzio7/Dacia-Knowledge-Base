# Spring Version Equipment Matrix Availability Import

Date: 2026-07-31

Status: **complete**

## Source contract

- Source: `src_pl_spring_brochure_20260219`.
- Pages: 19-20.
- Exact source grades: Essential, Expression and Extreme.
- Exact current configurations: `spring_essential_electric70_automatic`, `spring_expression_electric70_automatic`, `spring_extreme_electric100_automatic`.
- Provenance links: three `source_configurations.csv` relations connect the brochure matrix to those exact configurations while preserving the grade-column expansion boundary.
- Evidence type: direct grade-column matrix cells. The explicit Essential → Expression → Extreme chain is not needed to reconstruct any row.

## Imported observations

The package imports 42 existing canonical equipment attributes for each of the three selected configurations, for a total of 126 dated records:

- 106 `standard`;
- 7 `optional`;
- 13 `not_available`.

Every row preserves the source page and source label. Combined brochure rows are split only where matching canonical attributes already exist, for example regulator/limiter, side/curtain airbags and front/rear belt pretensioners.

## Exclusions

The package does not import:

- Pakiet Techno, Pakiet Power or Pakiet City membership;
- the Type 2 cable choice;
- package prices, because the brochure states none;
- exterior appearance strings, wheel designs or upholstery names;
- manual parking-brake or steering-system type strings;
- YouClip count or the front 12 V socket without matching approved attributes;
- colours, technical data or Cargo values;
- inferred inheritance or facts transferred from another source, model year, campaign, powertrain or configuration.

Optional statuses qualified by `patrz: pakiety` remain direct availability observations. Their commercial package membership is deliberately deferred to a separate package.

## Integrity

`tools/import_spring_equipment_availability.py` verifies the registered source SHA-256, three active configuration/version relationships, brochure-to-version relations, exact matrix dimensions, status distribution, canonical attribute compatibility, idempotent output and the contiguous availability ID suffix `5771-5896` and source-link suffix `248-250`.

The final cumulative diff contains exactly the fifteen package paths declared in `project/state.json`; the temporary workflows, materializer and encoded payload parts are absent. The deterministic verified-PDF coverage reconciliation JSON is regenerated because its master-data evidence counts depend on `configuration_attribute_availability.csv`; the Markdown rendering remains byte-identical.
