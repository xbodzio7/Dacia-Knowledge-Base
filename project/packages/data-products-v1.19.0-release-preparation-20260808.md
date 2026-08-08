# Data Products v1.19.0 Release Preparation

## Package

- Package ID: `data_products_v1_19_0_release_preparation_001`
- Date: 2026-08-08
- Baseline main: `53e13ec0e028071d24d4a3ec2a950a1d8a9fb6c7`
- Status: complete

## Release contract

Data Products v1.19.0 is prepared as a backward-compatible minor release from the verified post-v1.18.0 configurator interaction state.

Publication must:

- use the exact merge SHA of the bounded publication package;
- prove that tag and release `data-products-v1.19.0` do not already exist;
- build twice in independent empty directories and require byte-identical ZIP, manifest and checksums;
- verify the canonical archive and complete offline workspace before publication;
- preserve the eight-step offline configurator navigation;
- preserve exact configuration-mapped packages and options, including individual confirmed prices and explicit unknown-price states;
- preserve the deterministic final summary only for one visible canonical configuration and never select a vehicle implicitly from multiple results;
- preserve exact colour, wheel and upholstery status only from explicit filters or saved exact configurator observations, without promoting observations to a complete availability catalogue;
- preserve browser-session commercial selection state, normalization and canonical reset behavior;
- preserve additive JSON `commercial_selection` export metadata, provenance and deterministic price preview with `compatibility_inference_performed=false`;
- preserve source-specific commercial-selection metadata in the configuration comparison bundle and reject payloads claiming compatibility inference;
- retain exactly three public top-level assets: archive, manifest and SHA-256 checksums;
- re-download all public assets and compare them byte for byte before recording the publication receipt;
- preserve all earlier immutable releases.

## Product boundary

The release exposes the completed post-v1.18.0 configurator interaction increment through the established exact-source offline data-product pipeline. It adds navigation, source-bounded commercial choice, deterministic summary, session persistence, JSON export and comparison-bundle metadata behavior without changing canonical vehicle-selection semantics.

The release introduces no master-data mutation, schema migration, inferred package/option dependency graph, inferred conflict rule or assertion that arbitrary simultaneous commercial selections are orderable. Five valid Spring commercial offers still have no captured amount; those prices remain unknown, never zero.

Appearance evidence remains deliberately bounded:

- strict complete exact-current appearance coverage: 7 of 81 active configuration surfaces;
- `CAT-GAP-002`: open for 74 exact surfaces;
- complete visible grade-level Design lists: 3 of 21 grade surfaces;
- model packshots and saved selected appearances remain evidence-labelled representations, not an exact render matrix.

The current New Spring official Polish Dacia Shop reconciliation state is unchanged by this release preparation: 28 confirmed cards, 28 unresolved exact references, 14 exact current-price matches and zero established mismatches. An unresolved Shop reference is not evidence of withdrawal, incompatibility or unavailability.

## Pre-publication verification

- `data-products-v1.19.0` tag lookup: absent on 2026-08-08 before preparation.
- `data-products-v1.19.0` release lookup: absent on 2026-08-08 before preparation.
- The final production implementation head `60c03aa4d47509516e3bfa98c8b6d06ac346cf83` from PR #609 passed the complete required workflow set, including Quality run `31221967097`, Versioned Data Product Release run `31221967116` and Verified Data Product Release Download run `31221967184`.
- PR #610 subsequently repaired traceability and direct regression coverage without changing production logic, schema or master data.
- Milestone Review 003 final head `183e3b4f32fe1633a608222bb264017df365acb0` passed Quality run `31226626560` before merge as PR #612.
- This release-preparation Pull Request must pass its own full repository Quality gate and the release/workspace workflows on its final head before merge.
- Final publication source SHA must be the merge SHA of the bounded publication package.
- Required independent double build, archive/workspace verification and public-download verification remain mandatory in the publication package because only that package establishes the final immutable source SHA.

## Repository impact

Exactly three manifest paths:

- `project/STATE_SUMMARY.md`;
- `project/packages/data-products-v1.19.0-release-preparation-20260808.md`;
- `project/state.json`.

No production code, workflow, schema, test-baseline or `data/master` path changes.

## Next package

The sole next package is `data_products_v1_19_0_publication_001`. Actual public publication is an irreversible operation and remains an `ACTION_REQUIRED` boundary.
