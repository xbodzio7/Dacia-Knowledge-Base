# Data Products v1.8.1 Release Preparation

Date: 2026-07-27

## Purpose

Prepare an immutable patch release that delivers the restored equipment filtering and cheapest-to-most-expensive model ordering without changing source-backed data, comparison scopes or missing-evidence semantics.

This package prepares but does not publish the release.

## Public baseline

The latest verified public release is `data-products-v1.8.0`:

- release ID `360115681`;
- exact source commit `becd218228e3f4f0cdd312b0ed836ade487422b1`;
- 72 active configurations;
- 19 independent scopes;
- 114 within-scope pairs;
- 1,695 recorded differences;
- 85 deterministic archive members.

The public tag and assets remain immutable.

## v1.8.1 candidate

The patch candidate retains the complete member set and data products of v1.8.0. It changes generated behavior and explanatory release text only:

- `shortlist/configuration-shortlist.html` contains the corrected interactive equipment filter and price-ordered model choices;
- `RELEASE_NOTES.md` describes the patch behavior and immutability boundary.

The archive remains at exactly eighty-five members and preserves:

- 72 active configurations;
- 19 comparable scopes;
- 114 pairs generated only within existing scopes;
- 1,695 recorded differences;
- JSON, Markdown, CSV, HTML and XLSX formats;
- 124 technical comparison facets;
- 110 equipment facets.

## Equipment-filter contract

The candidate must verify:

- 110 equipment facets in the catalog;
- 108 initially visible equipment choices;
- searching for `kamera` leaves one visible choice;
- selecting the rear-view camera narrows 72 configurations to 66;
- one selected equipment item remains recorded after the click;
- missing, unknown and `not_available` evidence does not satisfy the filter;
- conflicting selected requirements are never removed silently.

## Model-order contract

Model choices are ordered by the minimum recorded current Polish catalogue price:

1. Sandero — 68,000 PLN;
2. Sandero Stepway — 71,700 PLN;
3. Jogger — 77,900 PLN;
4. Duster — 82,000 PLN;
5. Bigster — 101,400 PLN.

Models without a recorded current catalogue price sort after priced models.

## Semantic boundary

The release may not introduce:

- new data imports;
- new comparison pairs;
- cross-scope pairs;
- ranking or winner labels;
- recommendations;
- inferred values;
- replacement of missing evidence with availability;
- rewriting of public 1.6.1, 1.7.0 or 1.8.0 assets.

## Release identity

The target version is `1.8.1`, with tag `data-products-v1.8.1` and exactly three public assets:

- `dacia-knowledge-base-data-products-v1.8.1.zip`;
- `data-product-release-manifest.json`;
- `SHA256SUMS`.

The preparation branch is not the final source identity. Final source commit, sizes and SHA-256 values remain unset until a separate preflight builds twice from the exact squash-merged preparation commit.

## Publication lifecycle

The established lifecycle remains:

1. preflight — no tag or release;
2. publish — exact preflight identity only;
3. independent public audit;
4. durable publication record.

The preflight must additionally execute the real Chromium equipment-filter smoke test against the generated release HTML.

## Repository boundary

The package changes no master CSV data. The baseline remains:

- 46 CSV files;
- 9,688 rows;
- 2,949 scalar values;
- 244 value ranges;
- 4,754 equipment-availability records;
- 385 attributes.

The prepared test baseline is 1,038.

## Next package

`Data Products v1.8.1 Preflight` — build the assets twice from the exact merged preparation commit, prove byte identity, verify all release and offline-workspace contracts including the real Chromium interaction, and establish final sizes and hashes without creating a tag or release.
