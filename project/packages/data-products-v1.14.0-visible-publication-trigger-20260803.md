# Data Products v1.14.0 Visible Publication Trigger

Date: 2026-08-03

## Exact source

The bounded publication workflow is pinned to `6b02c97344050eab0900a48570a7239c1ce98d52`, the merge commit of the verified publication tooling.

## Contract

The workflow checks out only that base commit, refuses any existing `data-products-v1.14.0` tag or release, runs the focused release contracts, builds independently twice, requires byte identity, verifies all nine product files, all three direct entry points and all three workspace cards, publishes exactly three immutable assets, downloads and compares them byte for byte, records the receipt and removes the temporary publisher and recorder from `main`.

This activation pull request is not intended to merge. It changes no source data or release semantics and will be closed after independent receipt verification.
