# Data Products v1.3.0 Full Comparison and Official Configurator Intake

Date: 2026-07-23

## Purpose

Make the offline shortlist read like a buyer-facing configurator instead of a technical report, and register official Dacia web configurators as dated evidence for later configuration-level option imports.

## Browser changes

- model, version, gearbox, powertrain and price controls are arranged vertically;
- buyer-facing cards place the recognizable model silhouette and vehicle name first;
- technical configuration codes remain available only in provenance and deterministic exports;
- all active equipment categories have Polish interface labels;
- comparison includes every equipment attribute recorded for at least one selected configuration, not only filter selections;
- optional equipment states distinguish standard, package, individual option, unavailable and unknown;
- `Pokaż tylko różnice` hides equal comparison rows while preserving category structure;
- model and trim silhouettes are deterministic offline SVG illustrations and do not claim to be official photographs.

## Official configurator intake

The normalized source snapshot `project/sources/dacia-pl-configurators-20260723.json` registers the official Polish configurator catalogue and model configurators for Sandero, Sandero Stepway, Duster, Jogger and Bigster.

The intake records only visible, dated facts. It does not infer that an option visible for a default configuration applies to every trim, powertrain or gearbox. The observed Stepway default exposes `pakiet MEDIA DISPLAY` at 1,900 PLN, but that observation is not imported into configuration-level commercial data until exact applicability is proven.

Official photographs are not archived or redistributed. The offline browser uses repository-generated silhouettes.

## Verification

- 703 Python tests;
- full CSV and project-state validation;
- JavaScript syntax and pricing contract;
- full 67-configuration HTML exercised in Chromium;
- all equipment picker category headings were Polish;
- Jogger selection retained 22 configurations;
- three configurations produced 59 comparison rows, including full equipment;
- `Pokaż tylko różnice` reduced the view to 15 differing rows;
- no JavaScript console errors.
