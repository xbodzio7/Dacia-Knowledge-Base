# Data Products v1.13.0 Release Preparation

Date: 2026-08-03

Package ID: `data_products_v1_13_0_release_preparation_001`

Status: **complete**

## Release scope

Prepare the first immutable release containing the portfolio model-family comparison matrix and its direct offline workspace entry point.

Version `1.13.0` is a backward-compatible minor release because it adds three public archive members and one optional consumer entry point without changing existing members, required entry points or report semantics.

## Product contents

The release includes the verified family matrix in JSON, CSV and standalone HTML alongside the existing family summary in JSON, Markdown and standalone HTML.

The matrix covers:

- six canonical model families;
- 81 active configurations;
- 22 existing reporting scopes;
- 33 provenance sources;
- 251 explicit source-to-configuration relationships;
- zero configurations without provenance;
- explicit `not_stated` seat states for Duster and Bigster;
- no new configuration pair, cross-scope pair, ranking, recommendation or inferred value.

## Release notes contract

The archive contains exactly one `## v1.13.0 portfolio model-family comparison matrix` section. It documents the six byte-identical family products, optional `model_family_comparison_matrix_html` entry point, dedicated workspace card, preserved older releases and immutable public `data-products-v1.12.1`.

## Publication contract

Publication must:

- use the exact publication merge SHA;
- prove `data-products-v1.13.0` tag and release absence;
- build independently into two empty directories;
- require complete byte identity of archive, manifest and checksums;
- verify the canonical release manifest and every archive member;
- extract and verify the complete offline workspace;
- require both model-family entry points and both dedicated workspace cards;
- create exactly three immutable public assets;
- download those assets and compare them byte for byte;
- verify the public download again before recording the receipt;
- preserve `data-products-v1.12.1` unchanged.

## Boundaries

No source data, master data, reporting scope, comparison semantics, ranking, recommendation or inferred value changes.

## Next package

`data_products_v1_13_0_publication_001` publishes and records the release only after the full Quality and public-download contracts pass on the final publication source.
