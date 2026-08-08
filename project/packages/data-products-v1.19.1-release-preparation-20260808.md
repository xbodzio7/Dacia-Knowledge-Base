# Data Products v1.19.1 Release Preparation

## Package

- Package ID: `data_products_v1_19_1_release_preparation_001`
- Date: 2026-08-08
- Baseline main: `9fffae0db419852fc7ef52287f2a2bddae62c477`
- Status: complete

## Release contract

Data Products v1.19.1 is prepared as a backward-compatible patch release on top of immutable v1.19.0. Its bounded user-facing change is the Spring Type 2 current-selector reconciliation merged in PR #617.

Publication must:

- use the exact merge SHA of the bounded v1.19.1 publication package;
- prove that tag and release `data-products-v1.19.1` do not already exist;
- prove that public `data-products-v1.19.0` remains immutable at exact source `c121e600de48576f2da53cba2eb42075b6632504`;
- build v1.19.1 twice in independent empty directories and require byte-identical ZIP, manifest and checksums;
- verify the canonical archive and complete offline workspace before publication;
- preserve all established v1.19.0 configurator navigation, deterministic single-configuration summary, session persistence, JSON selection export and comparison-bundle metadata behavior;
- preserve `compatibility_inference_performed=false` and reject payloads that claim compatibility inference;
- preserve all three February brochure-backed `spring_type2_charging_cable_option` mappings in master history;
- preserve all three later exact-current `type2_charging_cable_supplied = standard` canonical availability rows;
- require the current selector to omit the historical Type 2 option for Spring Essential electric 70, Expression electric 70 and Extreme electric 100 once the later exact-current standard observations apply;
- preserve historical `as_of` visibility before the later exact-current standard observations;
- preserve the separate domestic-socket/FlexiCharger commercial option;
- preserve the existing Duster offer-plus-selected-state semantics;
- verify the reconciled current commercial layer at 164 selector offers, 162 priced offers and exactly 2 unpriced offers;
- verify that the only two unpriced current Spring offers are `spring_techno_package` and `spring_dc40_charging_option` for Spring Expression electric 70;
- keep those two prices unknown unless an exact-current MY26 source is introduced by a separate source package;
- preserve the historical reviewed-gap ledger even though the three historical Type 2 decisions no longer attach to current selector components;
- preserve all 18 exact saved configurator observations, all 1355 exact standard-equipment source lines, all 162 grouped technical categories and all 349 exact technical source lines;
- retain exactly three public top-level assets: archive, manifest and SHA-256 checksums;
- re-download all public assets and compare them byte for byte before recording the publication receipt;
- preserve all earlier immutable releases.

## Product boundary

This patch release changes derived current-selector semantics only. It does not alter the historical Spring brochure records or current canonical equipment-availability evidence.

The release introduces no `data/master` mutation, source mutation, schema migration, generic commercial temporal-precedence rule, package/component dependency graph, conflict graph, simultaneous-orderability inference, appearance-catalogue inference, ranking or recommendation change.

The Spring Type 2 correction is intentionally item-specific. It must not be generalized into a rule that a commercial package becomes unselectable merely because one of its component attributes is standard.

Appearance evidence remains bounded exactly as before; v1.19.1 does not attempt to close the source-blocked exact appearance surfaces. New Spring Shop unresolved references also remain unresolved unless new direct evidence is captured by a separate source package.

## Pre-publication verification

- `data-products-v1.19.1` tag lookup: absent on 2026-08-08 before preparation.
- `data-products-v1.19.1` release lookup: absent on 2026-08-08 before preparation.
- Spring Type 2 reconciliation final head `324221d889e22c8be43e131bd60f7ef14328df52` from PR #617 passed full Quality run `31246369245`.
- The same final head passed Versioned Data Product Release run `31246369251` and Verified Data Product Release Download run `31246369217`, together with the triggered shortlist, selection-export, comparison and reporting workflows.
- The canonical discovery baseline remains 1885 tests.
- This release-preparation Pull Request must pass its own full repository Quality gate and release/workspace workflows on its final head before merge.
- Final public v1.19.1 source SHA must be the exact source established by the later bounded publication package.
- Required independent double build, archive/workspace verification and public-download byte comparison remain mandatory in the publication package because only that package establishes the final immutable source SHA.

## Repository impact

Exactly three manifest paths:

- `project/STATE_SUMMARY.md`;
- `project/packages/data-products-v1.19.1-release-preparation-20260808.md`;
- `project/state.json`.

No production code, workflow, schema, test-baseline, source or `data/master` path changes.

## Next package

The sole next package is `data_products_v1_19_1_publication_001`. Actual public publication is an irreversible operation and remains an `ACTION_REQUIRED` boundary requiring fresh explicit authorization.
