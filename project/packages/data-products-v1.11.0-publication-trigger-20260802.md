# Data Products v1.11.0 Publication Trigger

## Package

- ID: `data_products_v1_11_0_publication_001`
- Kind: `data_product_release`
- Status before merge: `planned`
- Publication tag: `data-products-v1.11.0`

## Purpose

This dedicated package intentionally changes only this trigger document. Its merge to `main` selects the exact immutable source SHA consumed by `.github/workflows/temporary-publish-data-products-v1.11.0.yml`.

## Required publication contract

The publisher must:

1. refuse to replace an existing `data-products-v1.11.0` tag or release;
2. verify the canonical state and focused release contracts;
3. build the release assets twice from the exact publication merge SHA;
4. require byte-for-byte equality between both builds;
5. verify the archive and a fully materialized offline workspace;
6. publish the archive, manifest and checksums against the exact merge SHA;
7. download the public assets and compare them with the verified local build;
8. record the immutable publication receipt, update canonical project state and remove all temporary publication automation.

## Scope boundary

The release contains the 36 source-bounded common Spring technical observations materialized as configuration-value IDs 3569–3604. The documented MY2025-only and semantically ambiguous Spring values remain deferred.

No data, release metadata, state transition or tag is created on this branch. Publication starts only after this package passes full Quality and its merge commit lands on `main`.

## Verified retry after workflow repair

The first exact-SHA publication run `30771150367` completed the focused contracts and two byte-identical builds, then stopped before publication because the inline offline-workspace materializer did not expose the repository `tools` directory to Python. It created no tag, release or receipt.

PR #473 repaired that bounded workflow defect by invoking the materializer with `PYTHONPATH=tools` and adding a persistent regression assertion. This retry keeps every original immutability and evidence boundary. Its own green merge commit, not the failed earlier trigger commit, becomes the exact source SHA for `data-products-v1.11.0`.
