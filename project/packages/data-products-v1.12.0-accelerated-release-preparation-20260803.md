# Data Products v1.12.0 Accelerated Release Preparation

Date: 2026-08-03

Package ID: `data_products_v1_12_0_accelerated_release_preparation_001`

Status: **complete**

## Goal

Prepare the immutable `data-products-v1.12.0` release containing the verified portfolio model-family product.

## Exact publication contract

The publication package must:

1. use the exact publication PR merge SHA as `repository_commit`;
2. build `dacia-knowledge-base-data-products-v1.12.0.zip`, the release manifest and `SHA256SUMS` twice in independent empty directories;
3. compare all three outputs byte for byte;
4. verify both builds with the canonical release verifier;
5. publish tag `data-products-v1.12.0` only from that exact SHA;
6. download the public assets again, verify checksums and safely extract them;
7. verify the extracted workspace offline, including the family-summary HTML and its relative navigation path;
8. write a permanent publication receipt only after every check passes.

## Release delta

Version 1.12.0 adds the source-preserving portfolio model-family JSON, Markdown and standalone HTML to the versioned archive. The product covers six families, 81 active configurations, 22 reporting scopes, 33 provenance sources and 251 explicit source-to-configuration relationships.

No source data, reporting scope, comparison pair, ranking, recommendation or inferred value changes are introduced. Public `data-products-v1.11.0` remains immutable.

## Next package

`data_products_v1_12_0_publication_001` performs the exact-SHA publication and post-download verification.
