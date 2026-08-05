# Data Products v1.18.0 Visible Publication Trigger

Date: 2026-08-05

## Exact source

The bounded publication workflow is pinned to `21a4d875c9f3d4f155d0ac81aec7b30d5e4d35ed`, the merge commit containing the verified v1.18.0 publication tooling and the generic equipment-visibility correction.

## Contract

The workflow checks out only that base commit, refuses any existing `data-products-v1.18.0` tag or release, validates 18 exact saved-state joins, 1,355 preserved standard-equipment source lines, 162 technical categories and 349 technical source lines, builds independently twice, requires byte identity, verifies the complete offline workspace, publishes exactly three immutable assets, downloads and compares them byte for byte, records the receipt and removes temporary publication tools from `main`.

The published shortlist keeps any equipment item visible when it remains standard or optional in at least one compatible configuration. An item is hidden only when it is unavailable in all compatible configurations. This is a generic rule, not an automatic-climate-control exception.

This activation pull request is not intended to merge and will be closed after independent publication verification.
