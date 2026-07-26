# Data Products v1.7.0 Release Preparation

Date: 2026-07-26

## Purpose

This package prepares the next immutable public data-product release without creating a Git tag or GitHub Release.

The target identity is:

- version: `1.7.0`;
- tag: `data-products-v1.7.0`;
- publication mode: exact post-merge preflight, controlled publish, independent public audit and final publication record.

## Prepared portfolio

The deterministic candidate contains:

- 72 active configurations;
- 19 independent and comparable reporting scopes;
- 114 configuration pairs;
- 1,695 recorded differences;
- 83 archive members;
- JSON, Markdown, CSV, HTML and XLSX products.

Every active configuration belongs to exactly one reporting scope. No cross-scope pairs are generated.

## Verification performed

A diagnostic candidate was generated twice from one preparation-branch commit. The three outputs were byte-identical and passed the release verifier.

The candidate was then materialized into the same consumer workspace structure used by the public downloader:

- `assets/` with the three verified release assets;
- `contents/` with all 83 verified archive members;
- deterministic offline `index.html`.

The complete workspace passed `data-product-workspace-verify`. As an independent compatibility control, the already published `data-products-v1.6.1` release was downloaded again and its 69-configuration, 18-scope workspace also passed verification.

The diagnostic sizes and hashes are retained in `data/reporting/data_products_v1_7_0_release_preparation.json`, but they are explicitly not the final publication identity. Later commits on this branch and the squash merge change the source commit embedded in the manifest and archive.

## Semantic boundaries

The release preparation does not:

- alter master data;
- create recommendations or rankings;
- infer missing values;
- compare configurations across independent scopes;
- turn missing evidence into negative availability;
- resolve deferred Duster 4x4 dimensions or ambiguous Jogger mass evidence.

The release pipeline continues to record `cross_scope_pairs_generated`, `ranking_generated`, `recommendations_generated` and `inferred_values_generated` as false.

## Publication sequence

1. Squash merge this fully green preparation package.
2. Run a nonscalable preflight from the exact resulting `main` commit.
3. Build twice, verify byte identity and record the exact sizes and SHA-256 values of all three assets.
4. Confirm that `data-products-v1.7.0` does not yet exist as a tag or GitHub Release.
5. Publish by rebuilding from the same exact commit and requiring the preflight identities.
6. Independently download and audit the public assets, tag target, archive inventory, workspace and browser payload.
7. Record the immutable publication identity in a separate documentation package.

## Required assets

- `dacia-knowledge-base-data-products-v1.7.0.zip`;
- `data-product-release-manifest.json`;
- `SHA256SUMS`.

## Next package

`Data Products v1.7.0 Preflight` — freeze the exact squash-merged source commit and deterministic identities of the three assets without creating a tag or release.
