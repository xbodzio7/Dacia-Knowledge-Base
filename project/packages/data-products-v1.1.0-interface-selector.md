# Data Products v1.1.0 HTML Selector

Date: 2026-07-22

## Purpose

Prepare the next immutable public data-product release after `data-products-v1.0.0` by incorporating the source-backed catalogue expansion completed since the first release and by removing the remaining friction in the offline configuration selector.

The published `data-products-v1.0.0` assets remain immutable. The corrected public identity was published as `data-products-v1.1.0` from exact main commit `397958ba740c0b3b9370822d7e1d473c4829c11e`.

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

## Release scope

The release builder continues to create exactly three top-level assets:

1. `dacia-knowledge-base-data-products-v1.1.0.zip`,
2. `data-product-release-manifest.json`,
3. `SHA256SUMS`.

The archive is expected to contain the complete current shortlist for 67 active configurations, 17 independent comparison scopes, the existing comparison workbook and all companion JSON, Markdown, CSV and HTML products. Existing deterministic ZIP, manifest, SHA-256, exact-commit and non-overwrite rules remain unchanged.

## Validation

The package adds regression coverage for:

- clean model labels without appended codes;
- dependent version filtering by selected models;
- single-choice transmission markup;
- multi-select powertrain markup;
- browser-native selection state based on `Set` without initialization errors;
- reset behavior in the presence of a form control named `reset`;
- complete release construction and independent verification.

The final generated shortlist was also exercised in headless Chromium through
the complete interaction path: model selection, dependent versions,
single-choice transmission, multi-select powertrains, persistent configuration
selection and full filter reset. The browser reported no runtime errors.

The complete repository quality portfolio passed before merge. After the package was merged and verified on exact `main`, `data-products-v1.1.0` was published and all three public assets were downloaded again and accepted by the independent release verifier. Durable identities and hashes are recorded in `project/releases/data-products-v1.1.0.md`.
