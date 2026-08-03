# Data Products v1.12.1 Corrective Release Preparation

Date: 2026-08-03

Package ID: `data_products_v1_12_1_corrective_release_preparation_001`

Status: **complete**

## Goal

Prepare immutable `data-products-v1.12.1` assets from the verified repository state that includes the direct model-family download entry point and dedicated offline workspace card delivered in PR #486.

## Exact publication contract

The publication package must:

1. use the exact publication PR merge SHA as `repository_commit`;
2. build the archive, manifest and `SHA256SUMS` twice in independent empty directories;
3. compare all outputs byte for byte;
4. verify both builds with the canonical release verifier;
5. publish tag `data-products-v1.12.1` only from that exact SHA;
6. download the public assets again and verify checksums;
7. verify the complete extracted workspace offline, including `model_family_summary_html` and the dedicated **Model family summary** card;
8. write a permanent publication receipt only after every check passes.

## Corrective delta

The patch release makes the previously agreed model-family interface available in the published consumer workspace. The model-family data assets themselves remain the same verified product delivered in `v1.12.0`.

`data-products-v1.12.0` remains immutable. No source data, reporting scope, comparison pair, ranking, recommendation or inferred value changes are introduced.

## Validation

Canonical project-state and documentation-baseline generators must be clean before publication preparation is merged.

## Next package

`data_products_v1_12_1_publication_001` performs the exact-SHA publication and post-download verification.
