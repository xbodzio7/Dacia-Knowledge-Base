# Data Products v1.8.0 Release Preparation

Date: 2026-07-26

## Purpose

Prepare a new immutable minor release that delivers the completed scope-preserving cross-model navigation products without changing master data or comparison semantics.

This package prepares but does not publish the release.

## Public baseline

The latest documented public release is `data-products-v1.7.0`:

- release ID `360090447`;
- exact source commit `99e0e19b86cad6eae619f37702464e6a5a761cd8`;
- 72 active configurations;
- 19 independent scopes;
- 114 within-scope pairs;
- 1695 recorded differences;
- 83 deterministic archive members.

The public tag and assets remain immutable.

## v1.8.0 candidate

The prepared candidate retains the complete v1.7.0 data products and adds:

- `cross-model/cross-model-comparison-view.json`;
- `cross-model/cross-model-comparison-view.html`.

The resulting archive contains exactly eighty-five members while preserving:

- 72 active configurations;
- 19 comparable scopes;
- 114 pairs generated only within existing scopes;
- 1695 recorded differences;
- JSON, Markdown, CSV, HTML and XLSX formats;
- 124 technical comparison facets;
- 110 equipment facets.

## Cross-model product

The release must verify:

- five model families;
- nineteen reporting scopes;
- seventy-six exact comparison-report paths in JSON;
- two JSON navigation paths;
- fifty-seven local file links in HTML;
- every local target exists in the extracted workspace;
- static HTML with no JavaScript or runtime image dependency;
- explicit `not_stated` seat state for Bigster and Duster.

## Semantic boundary

The release may not generate:

- a pair between independent reporting scopes;
- ranking or winner labels;
- recommendations;
- inferred values;
- new data imports;
- an expanded cross-model user interface.

## Release identity

The target version is `1.8.0`, with tag `data-products-v1.8.0` and exactly three public assets:

- `dacia-knowledge-base-data-products-v1.8.0.zip`;
- `data-product-release-manifest.json`;
- `SHA256SUMS`.

The preparation branch is not the final source identity. Final source commit, sizes and SHA-256 values are intentionally left unset until a separate preflight builds twice from the exact squash-merged preparation commit.

## Publication lifecycle

The established lifecycle remains:

1. preflight — no tag or release;
2. publish — exact preflight identity only;
3. independent public audit;
4. durable publication record.

## Repository boundary

The package changes no master CSV data. The baseline remains:

- 46 CSV files;
- 9688 rows;
- 2949 scalar values;
- 244 value ranges;
- 4754 equipment-availability records;
- 385 attributes.

The prepared test baseline is 1014.

## Next package

`Data Products v1.8.0 Preflight` — build the assets twice from the exact merged preparation commit, verify release and offline workspace behavior, and establish final sizes and hashes without creating a tag or release.
