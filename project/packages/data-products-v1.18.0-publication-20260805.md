# Data Products v1.18.0 Publication

Date: 2026-08-05

## Result

The immutable `data-products-v1.18.0` release was published from exact source commit `a13587ff0bf9d683d7a450f0fbb15aa610693f03`.

The release adds exact technical-observation filtering for 18 saved configurator states: 162 grouped technical categories and 349 preserved technical source lines. It also includes the corrected generic equipment-facet rule: an equipment item remains visible whenever it is standard or optional in at least one compatible configuration, and is hidden only when unavailable in all compatible configurations.

No equipment-specific exception was introduced. Technical lines remain dated source evidence and are not semantically coerced or transferred between model families, grades, powertrains, transmissions, seat counts or source phases.

Both independent builds were byte-identical, the complete offline workspace passed verification, and the publicly downloaded assets matched the verified build byte for byte. Public `data-products-v1.17.0` remains immutable.

## Assets

- `dacia-knowledge-base-data-products-v1.18.0.zip`;
- `data-product-release-manifest.json`;
- `SHA256SUMS`.

Exact sizes and SHA-256 values are stored in `data/reporting/data_products_v1_18_0_publication.json`.

## Next package

`post_v1_18_0_release_priority_selection_review_001` selects one bounded next package from canonical repository evidence.
