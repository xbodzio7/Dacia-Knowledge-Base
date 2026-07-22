# Data Products v1.1.0 Interface and Selector Workbook

Date: 2026-07-22

## Purpose

Prepare the next immutable public data-product release after `data-products-v1.0.0` by incorporating the source-backed catalogue expansion completed since the first release and by removing the remaining friction in the offline configuration selector.

The published `data-products-v1.0.0` assets remain immutable. The new public identity is planned as `data-products-v1.1.0`.

## Interactive shortlist changes

The offline shortlist keeps its existing evidence semantics, selection export and commercial-price logic, but changes the primary identity filters:

- model choices show only maintained display names; internal codes are no longer appended in parentheses;
- the version control is hidden and disabled until at least one model is selected;
- after model selection, the version control contains only versions belonging to the selected model or models;
- an initial version-only CLI filter deterministically selects the owning model so the version remains visible;
- transmission is a single-choice filter with an explicit unrestricted state;
- powertrains are presented as a stable multi-select list populated from the current catalogue;
- reset clears the dependent version control and restores the full catalogue.

The browser filtering engine retains the existing Python-compatible semantics. Powertrain values selected from the list remain compatible with the existing substring-based CLI filter contract.

## Selector workbook

The deterministic comparison workbook advances to version 3 and contains nine sheets:

1. `Overview`,
2. `Selector`,
3. `Scopes`,
4. `Configurations`,
5. `Equipment`,
6. `Commercial Offers`,
7. `Comparisons`,
8. `Sources`,
9. `Artifacts`.

`Selector` is a wide, filterable consumer table with exactly one row per selected configuration. Its leading columns contain:

- configuration code,
- model,
- version,
- powertrain,
- transmission,
- current source-backed Polish catalogue price,
- price date and source,
- number of seats,
- equipment recorded and missing counts.

Every source-backed equipment attribute available in the selected portfolio is then represented by one readable Polish column. Each cell uses one of four explicit values:

- `seryjne`,
- `opcjonalne`,
- `niedostępne`,
- `brak danych`.

Excel AutoFilter can therefore narrow the configuration rows directly by model, version, drivetrain, gearbox, price, seats and any combination of equipment requirements. A missing source statement remains `brak danych` and is never converted to `niedostępne`.

## Release scope

The release builder continues to create exactly three top-level assets:

1. `dacia-knowledge-base-data-products-v1.1.0.zip`,
2. `data-product-release-manifest.json`,
3. `SHA256SUMS`.

The archive is expected to contain the complete current shortlist for 67 active configurations, 17 independent comparison scopes, the nine-sheet workbook and all companion JSON, Markdown, CSV and HTML products. Existing deterministic ZIP, manifest, SHA-256, exact-commit and non-overwrite rules remain unchanged.

## Validation

The package adds regression coverage for:

- clean model labels without appended codes;
- dependent version filtering by selected models;
- single-choice transmission markup;
- multi-select powertrain markup;
- browser-native selection state based on `Set` without initialization errors;
- reset behavior in the presence of a form control named `reset`;
- one selector row per chosen configuration;
- Polish equipment-state vocabulary;
- selector equipment-column counts and missing-state accounting;
- nine-sheet package order, dimensions, filters and deterministic bytes;
- complete release construction and independent verification.

The final generated shortlist was also exercised in headless Chromium through
the complete interaction path: model selection, dependent versions,
single-choice transmission, multi-select powertrains, persistent configuration
selection and full filter reset. The browser reported no runtime errors.

The complete repository quality portfolio is required before merge. Publication of `data-products-v1.1.0` is a separate durable operation performed only after the package has been merged and verified on exact `main`.
