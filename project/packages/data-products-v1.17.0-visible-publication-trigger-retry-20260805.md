# Data Products v1.17.0 Visible Publication Trigger Retry

Date: 2026-08-05

## Exact source

The corrected bounded publication workflow is pinned to `ee7a55f3a01daafed7d13ac937eaa43af2c225ee`, the merge commit containing the verified one-line publication-guard correction.

## Corrected guard

The first activation stopped before release creation because the publisher referenced nonexistent closure-row key `exact_configuration_code`. The corrected publisher validates the exact saved configurator identifiers through the canonical `configuration_code` field.

## Contract

The workflow checks out only the exact source commit, refuses any existing `data-products-v1.17.0` tag or release, runs focused contracts, validates all 18 exact saved-state joins and all 1355 preserved standard-equipment source lines, builds independently twice, requires byte identity, verifies normalized Spring media and exact configurator-observation filters in the archive, verifies the complete offline workspace, publishes exactly three immutable assets, downloads and compares them byte for byte, records the receipt and removes the temporary publisher and recorder from `main`.

This activation pull request is not intended to merge. It changes no source data, master data, cross-phase semantics, ranking, recommendation or inferred values and will be closed after independent receipt verification.
