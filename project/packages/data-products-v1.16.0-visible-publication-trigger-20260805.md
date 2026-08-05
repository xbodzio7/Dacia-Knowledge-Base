# Data Products v1.16.0 Visible Publication Trigger

Date: 2026-08-05

## Exact source

The bounded publication workflow is pinned to `bc6523ba3a37df40e879a8f8f5cf0fce8f0dcfd3`, the merge commit of the verified publication tooling.

## Contract

The workflow checks out only that base commit, refuses any existing `data-products-v1.16.0` tag or release, runs focused contracts, builds independently twice, requires byte identity, verifies all fifteen family, version, source-coverage and powertrain product files, all five direct entry points and all five workspace cards, publishes exactly three immutable assets, downloads and compares them byte for byte, records the receipt and removes the temporary publisher and recorder from `main`.

This activation pull request is not intended to merge. It changes no source data or release semantics and will be closed after independent receipt verification.
