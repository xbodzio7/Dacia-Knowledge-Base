# Data Products v1.9.0 Release Preparation

Date: 2026-07-31

## Purpose

Prepare an immutable minor release that publishes the current source-backed portfolio after the completed Sandero page-17 technical chain. The candidate adds six manual Sandero and Sandero Stepway configurations, one independent comparison scope and the associated source-backed technical coverage.

This package prepares but does not publish the release.

## Public baseline

The latest verified public release is `data-products-v1.8.1`:

- release ID `360138130`;
- exact source commit `0b7009fd1950693e347638a6b96756aeefb43b8a`;
- 72 active configurations;
- 19 independent scopes;
- 114 within-scope pairs;
- 1,695 recorded differences;
- 85 deterministic archive members;
- 124 technical comparison facets and 110 equipment facets.

The public tag and assets remain immutable.

## v1.9.0 candidate

The current candidate contains:

- 78 active configurations;
- 20 independent and comparable scopes;
- 129 pairs generated only within existing scope boundaries;
- 2,180 recorded differences;
- 89 deterministic archive members;
- 127 technical comparison facets;
- 110 equipment facets;
- JSON, Markdown, CSV, HTML and XLSX products.

The minor-version increment records a real source-backed expansion rather than an interface-only correction.

## New source-backed configurations

The release adds exactly six active manual configurations:

- `sandero_iii_essential_tce100_manual`;
- `sandero_iii_expression_tce100_manual`;
- `sandero_iii_journey_tce100_manual`;
- `sandero_stepway_iii_essential_tce110_manual`;
- `sandero_stepway_iii_expression_tce110_manual`;
- `sandero_stepway_iii_extreme_tce110_manual`.

They are partitioned in the independent reporting scope `sandero_tce100_stepway_tce110_manual`. The scope contributes 15 new within-scope pairs and does not create any comparison across unrelated scopes.

## Release delta

Relative to public v1.8.1, the candidate adds:

- 6 configurations;
- 1 reporting scope;
- 15 within-scope pairs;
- 485 recorded differences;
- 4 archive members;
- 3 technical comparison facets;
- no new equipment facet.

The verified repository has also grown by 1,692 master rows, 549 scalar configuration values, 54 configuration ranges and 1,016 equipment-availability records since the v1.8.1 source commit.

## Shortlist contract

The candidate must preserve:

- 78 active configurations;
- 110 equipment facets and 108 initially visible equipment choices;
- 71 configurations matching the rear-view-camera requirement;
- missing, unknown and explicitly unavailable evidence as exclusions;
- model order by minimum current Polish catalogue price: Sandero 63,900 PLN, Sandero Stepway 71,700 PLN, Jogger 77,900 PLN, Duster 82,000 PLN and Bigster 101,400 PLN.

## Semantic boundary

The release may contain new source-backed configurations, a new independent scope and new pairs within that scope. It may not introduce:

- cross-scope pairs;
- ranking or winner labels;
- recommendations;
- inferred values;
- replacement of missing evidence with availability;
- rewriting of public 1.6.1, 1.7.0, 1.8.0 or 1.8.1 assets.

## Release identity

The target version is `1.9.0`, with tag `data-products-v1.9.0` and exactly three public assets:

- `dacia-knowledge-base-data-products-v1.9.0.zip`;
- `data-product-release-manifest.json`;
- `SHA256SUMS`.

The preparation branch is not the final source identity. Final source commit, sizes and SHA-256 values remain unset until a separate preflight builds twice from the exact squash-merged preparation commit.

## Publication lifecycle

The established lifecycle remains:

1. preflight — no tag or release;
2. publish — exact preflight identity only;
3. independent public audit;
4. durable publication record.

The preflight must prove byte-identical rebuilds, verify the six new configurations and 20-scope partition, check the offline workspace and independently download public v1.8.1 as the immutable control.

## Repository boundary

The prepared repository baseline is:

- 1,684 tests;
- 46 CSV files;
- 11,380 rows;
- 3,498 scalar values and 138 scalar import specifications;
- 298 value ranges and 24 range import specifications;
- 5,770 equipment-availability records;
- 385 attributes in 30 categories.

## Next package

`Data Products v1.9.0 Preflight` — build the assets twice from the exact merged preparation commit, prove byte identity, verify all release and offline-workspace contracts, and establish final sizes and hashes without creating a tag or release.
