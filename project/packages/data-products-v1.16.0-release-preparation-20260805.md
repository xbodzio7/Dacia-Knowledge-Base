# Data Products v1.16.0 Release Preparation

## Package

- Package ID: `data_products_v1_16_0_release_preparation_001`
- Date: 2026-08-05
- Status: complete

## Release contract

Data Products v1.16.0 is prepared as a backward-compatible minor release from the verified powertrain/transmission matrix integration state.

Publication must:

- use the exact merge SHA of the bounded publication package;
- prove that tag and release `data-products-v1.16.0` do not already exist;
- build twice in independent empty directories and require byte-identical ZIP, manifest and checksums;
- verify the canonical archive and complete offline workspace before publication;
- require the existing family summary, family comparison, model-version comparison, source-coverage and new powertrain/transmission entry points and dedicated workspace cards;
- retain exactly three public top-level assets: archive, manifest and SHA-256 checksums;
- re-download all public assets and compare them byte for byte before recording the publication receipt;
- preserve all earlier immutable releases.

## Product boundary

The release adds the verified powertrain/transmission matrix in JSON, CSV and standalone HTML under `powertrains/`. It covers all 81 active configurations exactly once using only exact recorded `powertrain_label` and `transmission_type` values. It introduces no master-data change, normalization, ranking, recommendation or inferred value.

## Next package

The sole next package is `data_products_v1_16_0_publication_001`. Actual public publication is an irreversible operation and requires explicit authorization at the ACTION_REQUIRED boundary.