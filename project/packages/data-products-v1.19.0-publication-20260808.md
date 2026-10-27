# Data Products v1.19.0 Publication

Date: 2026-08-08

## Result

The immutable `data-products-v1.19.0` release was published from exact source commit `c121e600de48576f2da53cba2eb42075b6632504` by activation PR #615 in workflow run `31245016492`.

The release publishes the completed post-v1.18.0 configurator interaction increment through the established offline data-product pipeline: eight-step navigation, exact configuration-mapped packages and options, deterministic single-configuration summary, browser-session commercial selection state, additive JSON `commercial_selection` export and source-specific comparison-bundle commercial metadata.

The commercial selector remains source-bounded: 34 non-appearance items produce 167 selectable exact-configuration offer rows, 162 with captured prices and 5 valid Spring offers with unknown prices. Unknown prices remain unknown, never zero. No generic dependency/conflict graph or simultaneous-orderability inference was created, and `compatibility_inference_performed` remains false.

Appearance remains evidence-bounded. Saved colour, wheel and upholstery states are exact observations only and are not promoted into a complete availability catalogue. The release also preserves all 18 exact saved configurator states, 1,355 standard-equipment source lines, 162 grouped technical categories and 349 technical source lines from v1.18.0.

Both independent builds were byte-identical, the complete offline workspace passed verification, and the publicly downloaded assets matched the verified build byte for byte. Public `data-products-v1.18.0` remains immutable.

## Assets

- `dacia-knowledge-base-data-products-v1.19.0.zip`;
- `data-product-release-manifest.json`;
- `SHA256SUMS`.

Exact sizes and SHA-256 values are stored in `data/reporting/data_products_v1_19_0_publication.json`.

## Evidence boundary

This release introduces no source-data or master-data mutation, ranking, recommendation, inferred commercial compatibility, inferred simultaneous orderability, appearance-catalogue inference, cross-phase promotion, cross-grade transfer or cross-powertrain transfer.

## Next package

`post_v1_19_0_release_priority_selection_review_001` selects one bounded next package from canonical repository evidence after the v1.19.0 publication checkpoint.
