# Post-v1.16.0 Release Priority Selection Review

## Package

- Package ID: `post_v1_16_0_release_priority_selection_review_001`
- Kind: `bounded_priority_review`
- Date: 2026-08-05
- Status: complete

## Purpose

Review the verified v1.16.0 publication, current canonical interface implementation, exact configurator observations and explicit user priority, then select exactly one bounded continuation without reopening the immutable release or combining unrelated interface changes.

## Evidence reviewed

- `project/state.json` identifies this review as the sole planned continuation after completion of `data_products_v1_16_0_publication_001`.
- `data/reporting/data_products_v1_16_0_publication.json` records a complete public v1.16.0 publication with exact-source, double-build, offline-workspace and public-download byte verification.
- No open Pull Request competes for the next package.
- `project/sources/dacia-pl-model-media-20260724.json` is the shared official Dacia Polska model-media catalogue used by Sandero, Sandero Stepway, Jogger, Duster and Bigster.
- `project/sources/dacia-pl-spring-model-media-20260801.json` and `_apply_supplemental_model_media(...)` currently override Spring with a separate `3dv2.renault.com` parking-scene image and Spring-only framing.
- The current official Dacia Polska Spring page exposes a clean car-picker packshot through the same `d_brandSite_carPicker_1.png` mechanism already used by the shared catalogue.
- The completed cross-model configurator packages persist 18 exact saved states, including exact selected colour, wheels, upholstery and standard-equipment source lines keyed by configurator code, with mandatory source-phase boundaries and no inferred alternatives.
- The requested configurator-observation filters are a separate, broader product change that requires a dedicated data-to-interface contract and focused regression coverage.

## Selection

The next package is:

- Package ID: `configuration_shortlist_spring_media_normalization_001`
- Kind: `user_interface_repair`
- Name: `Configuration Shortlist Spring Media Normalization`
- Boundary: add the current official Spring car-picker packshot to the shared model-media catalogue, remove the Spring-only supplemental media override and remove Spring-only crop/scale behavior that is no longer necessary, while preserving deterministic offline fallback and all other model media.

## Rationale

This is the highest-priority unblocked continuation because it:

1. directly resolves the visible inconsistency identified by the user;
2. uses a current official Dacia Polska source and the established shared car-picker mechanism;
3. is mechanically bounded and does not require changes to master data, configuration identity or release artifacts;
4. isolates media-source and framing risk from the later configurator-observation filter contract;
5. leaves a clean common media path for all model cards before the main shortlist interface gains additional filters.

## Explicit non-selections

The review does not select:

- configurator-observation filters in the same Pull Request as the Spring media repair;
- inferred catalogues of available colours, wheels, upholstery, packages, options or accessories;
- propagation of exact PDF observations between phases, grades, powertrains, transmissions or seat counts;
- changes to photos of Sandero, Sandero Stepway, Jogger, Duster or Bigster;
- changes to master data, schemas or the immutable v1.16.0 release;
- v1.17.0 release preparation or public tag and release creation.

## Acceptance criteria

This review is complete when:

- `configuration_shortlist_spring_media_normalization_001` is recorded as the sole planned next package in `project/state.json`;
- generated state documentation reflects the selection;
- the package manifest records the official-source and scope boundaries;
- no domain data, interface implementation or release asset is modified;
- the final head passes canonical project-state validation and the complete required CI matrix.

## Result

The post-v1.16.0 priority-selection review is complete. Work may continue with `configuration_shortlist_spring_media_normalization_001` as the next bounded package.
