# Portfolio Model Family Summary Release Integration

Date: 2026-08-03

Package ID: `portfolio_model_family_summary_release_integration_001`

Status: **complete**

## Goal

Integrate the verified portfolio model-family summary into every newly generated versioned data-product release and its offline consumer workspace without altering source data or comparison semantics.

## Integrated release members

- `model-families/portfolio_model_family_summary.json`;
- `model-families/portfolio_model_family_summary.md`;
- `model-families/portfolio_model_family_summary.html`.

## Release contract

The release CLI first performs the canonical data-product build, verifies it, copies the three committed family-summary outputs byte-for-byte, adds one relative offline link from the existing cross-model page, deterministically rebuilds the archive and rewrites the external manifest and checksums.

The integrated manifest records the product directory and formats. The family JSON contract preserves 81 configurations, six families, 22 reporting scopes, 251 explicit source relationships and zero configurations without provenance.

## Consumer contract

Verified download extracts every manifest member, including all family-summary files. The existing offline workspace links to the cross-model page, which now contains a relative link to the family-summary HTML. Older immutable releases remain valid because verification does not require the new optional manifest fields.

## Non-inference boundary

The integration creates no cross-scope pairs, rankings, recommendations or inferred values and changes no source or master data.

## Next package

`data_products_v1_12_0_accelerated_release_preparation_001` prepares the first immutable release containing the integrated family summary.
