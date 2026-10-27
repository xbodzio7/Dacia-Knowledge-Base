# Post-v1.12.0 Release Priority Selection Review

Date: 2026-08-03

Package ID: `post_v1_12_0_release_priority_selection_review_001`

Status: **complete**

## Result

The immutable `data-products-v1.12.0` publication receipt and current consumer path were reviewed. The release was built twice with byte-identical assets, its offline workspace passed verification, and publicly downloaded assets matched the verified build.

The portfolio model-family JSON, Markdown and standalone HTML are already present in the archive. The remaining bounded usability gap is discoverability: the family HTML is reached indirectly through the cross-model page rather than exposed as a direct verified consumer entry point.

## Selected package

`portfolio_model_family_workspace_entry_point_001` — **Portfolio Model Family Workspace Entry Point**

Expose the verified portfolio model-family HTML as a direct backward-compatible download entry point and dedicated offline workspace card, without changing release contents, source data or comparison semantics.

## Boundaries

The selected package will not modify published releases, source or master data, reporting scopes, comparison pairs, rankings, recommendations or inferred values. Older releases without the family member remain valid.
