# Data Products v1.13.0 Visible Publication Trigger

Date: 2026-08-03

## Exact source

The bounded publication workflow is pinned to `0e7a8b4106bc830d39a257e5ef18fb2adcd44d0d`, the merge commit of the verified publication tooling.

## Contract

The workflow checks out only that base commit, refuses any existing `data-products-v1.13.0` tag or release, runs the focused release contracts, builds independently twice, requires byte identity, verifies both model-family entry points and workspace cards, publishes exactly three immutable assets, downloads and compares them byte for byte, records the receipt and removes the temporary publisher and recorder from `main`.

This activation pull request is not intended to merge. It changes no source data or release semantics and will be closed after independent receipt verification.
