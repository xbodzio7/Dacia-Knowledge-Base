# Post-v1.17.0 Release Priority Selection Review

## Package

- Package ID: `post_v1_17_0_release_priority_selection_review_001`
- Kind: `bounded_priority_review`
- Date: 2026-08-05
- Status: complete

## Purpose

Review the verified v1.17.0 publication, current canonical interface implementation, completed exact configurator observations and remaining source-backed continuations, then select exactly one bounded next package without reopening the immutable release or combining unrelated data and interface changes.

## Evidence reviewed

- `project/state.json` identifies this review as the sole planned continuation after completion of `data_products_v1_17_0_publication_001`.
- `data/reporting/data_products_v1_17_0_publication.json` records a complete public v1.17.0 publication with exact-source, double-build, offline-workspace and public-download byte verification.
- No open Pull Request competes for the next package.
- `data/reporting/cross_model_configurator_technical_data.json` preserves 18 exact saved configurator states, 162 technical category blocks and 349 exact source lines from page 5 of the registered official PDFs.
- The technical observation artifact explicitly forbids semantic key-value coercion and transfer across model family, source phase, grade, powertrain, transmission or seat count.
- `tools/reporting/commercial_offers.py` currently constructs one exact saved-configuration observation from commercial data, standard equipment and identity closure only; the completed technical observation artifact is not yet joined to that user-facing object.
- `tools/reporting/configuration_shortlist_equipment_groups.js` already provides the bounded browser contract for exact saved-state evidence and filtering by selected colour, wheels, upholstery and standard-equipment source lines.
- The options, packages and accessories coverage audit found zero exact entries in all 18 saved PDFs and explicitly prohibits inferred availability, compatibility or pricing.
- The completed residual-review and conflict-closure packages leave no competing unresolved source-backed correction queue.

## Selection

The next package is:

- Package ID: `configuration_shortlist_exact_technical_observation_filters_001`
- Kind: `user_interface_data_integration`
- Name: `Configuration Shortlist Exact Technical Observation Filters`
- Boundary: join the completed exact technical-data report to the existing exact saved-configuration observation bundle, expose searchable exact technical source-line filtering and grouped technical evidence in the shortlist, and preserve the existing exact-state, source-date and no-inference boundaries.

## Rationale

This is the highest-priority unblocked continuation because it:

1. makes an already completed and verified source-backed artifact directly useful in the primary shortlist interface;
2. extends the exact saved-state contract introduced in v1.17.0 instead of creating a parallel transport path;
3. has complete one-to-one configurator-code coverage for all 18 observations and deterministic counts of 162 category blocks and 349 source lines;
4. can be implemented without changing canonical master data, parsing technical lines into inferred attributes or promoting observations across source phases;
5. preserves the empty options, packages and accessories boundary until a separate authoritative source is captured.

## Explicit non-selections

The review does not select:

- semantic parsing or promotion of technical source lines into canonical master attributes;
- inference or propagation between model families, phases, grades, powertrains, transmissions or seat counts;
- an inferred catalogue of available options, packages or accessories;
- changes to recommendation, ranking, pricing or comparison semantics;
- changes to source PDFs or completed cross-model observation artifacts;
- unrelated model, media, roadmap or architecture work;
- v1.18.0 release preparation or public tag and release creation.

## Acceptance criteria for the selected package

The selected package is complete when:

- the exact technical report is a required member of the saved-configurator observation bundle and partial or mismatched bundles fail closed;
- all four observation reports share the same source code, observation date and exact configuration-code set;
- each joined observation preserves grouped technical categories and a flat exact technical source-line list without semantic coercion;
- the shortlist exposes a searchable multi-select filter for exact technical source lines and a grouped evidence section on each matching configuration card;
- exact counts remain 18 saved states, 162 technical category blocks and 349 technical source lines;
- commercial exports continue to exclude the transport-only configurator observation object;
- existing colour, wheel, upholstery and standard-equipment filters retain their semantics;
- project-state validation, focused Python and browser-contract tests, deterministic release tests and the complete required CI matrix pass on the final head.

## Result

The post-v1.17.0 priority-selection review is complete. Work may continue with `configuration_shortlist_exact_technical_observation_filters_001` as the sole bounded next package.
