# Portfolio Model Family Workspace Entry Point

Date: 2026-08-03

Package ID: `portfolio_model_family_workspace_entry_point_001`

Status: **complete**

## Result

Verified release downloads expose `model_family_summary_html` whenever the immutable archive contains `model-families/portfolio_model_family_summary.html`.

The generated offline workspace adds a dedicated **Model family summary** card after verifying both manifest membership and the extracted local file. The command-line summary prints this direct entry point only when it exists.

## Compatibility

Older immutable releases without the optional family member remain valid. Their extraction, verification, entry-point inventory and workspace navigation are unchanged.

## Boundaries

The package does not modify any published release, source or master data, reporting scope, comparison pair, ranking, recommendation or inferred value.

## Verification

The existing Quality, Versioned Data Product Release and Verified Data Product Release Download workflows exercise the wrapper integration and backward-compatible extraction path.
