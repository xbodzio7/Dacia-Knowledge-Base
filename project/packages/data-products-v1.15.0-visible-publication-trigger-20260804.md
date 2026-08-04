# Data Products v1.15.0 Visible Publication Trigger

Date: 2026-08-04

## Exact source

The bounded publication workflow is pinned to `5a824010921ef305b481f8284ae45bdfd8801780`, the merge commit of the verified publication tooling.

## Contract

The workflow checks out only that base commit, refuses any existing `data-products-v1.15.0` tag or release, runs the focused release contracts, builds independently twice, requires byte identity, verifies all twelve family, version and source-coverage product files, all four direct entry points and all four workspace cards, publishes exactly three immutable assets, downloads and compares them byte for byte, records the receipt and removes the temporary publisher and recorder from `main`.

This activation pull request is not intended to merge. It changes no source data or release semantics and will be closed after independent receipt verification.
