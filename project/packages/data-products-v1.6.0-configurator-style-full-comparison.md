# Data Products v1.6.0 Configurator-Style Full Comparison

Date: 2026-07-24

## Purpose

Resolve the buyer-facing problems found during direct review of `data-products-v1.5.0`: incorrect-looking model miniatures, unclear equipment search, misleading partial equipment coverage, separated price bounds and an equipment-only comparison.

## Official model photographs

The browser registers one current official Dacia Polska packshot for each active model family: Sandero, Sandero Stepway, Jogger, Duster and Bigster. The dated registry is stored in `project/sources/dacia-pl-model-media-20260724.json`.

Photographs are loaded directly from the official Dacia Polska image endpoint and are not copied into repository or release assets. Every image has a deterministic, model-specific SVG fallback. The selector and all comparison functions therefore continue to work without network access; only the official photograph is replaced by the local fallback when it cannot be loaded.

## Configurator-style controls

- model choices use official model photographs and dark Dacia-style selection tiles;
- version, transmission and powertrain use the same compact selectable-tile language;
- all primary filter sections remain stacked vertically;
- minimum and maximum catalogue price share one row, with minimum on the left and maximum on the right;
- technical configuration codes remain hidden from buyer-facing titles and stay available in provenance and exports.

## Source-complete equipment facets

The equipment selector no longer treats incomplete source coverage as a useful difference.

A non-selected equipment facet is visible only when every currently compatible configuration has an explicit availability record and the records contain both:

- at least one `standard` or `optional` state;
- at least one `not_available` state.

Universally available equipment is hidden because it cannot narrow the results. Equipment with missing or explicit unknown records is also hidden because absence of evidence must not be presented as unavailability. An already selected valid facet remains visible and removable.

The text field is renamed to `Filtruj listę wyposażenia` and explicitly states that it filters labels in the list; it does not search vehicles until an equipment item is selected.

This rule intentionally hides cross-model items such as the shark-fin antenna while source coverage is incomplete. Exact optional/package coverage and prices remain a separate source-import package.

## Full comparison

The in-page comparison now contains:

- model, version, powertrain, transmission, catalogue price and seat count;
- every latest dated configuration value or value range available for at least one selected configuration;
- fuel-specific technical observations kept as separate rows;
- all source-backed equipment availability states;
- configured price when equipment selections support it.

Technical labels are translated through `configuration_attribute_labels_pl.json`. Existing category translations are reused. `Pokaż tylko różnice` applies to all basic, technical and equipment rows.

## Data boundary

This package changes reporting and source presentation only. It does not add or rewrite vehicle availability, package, option, technical or price observations. In particular, missing configurator option coverage is not inferred from another model or configuration.

## Verification

- 717 Python tests;
- JavaScript syntax checks for browser, selection and configurator-style modules;
- exact production catalogue: 69 active configurations, 88 technical comparison facets and 109 equipment attributes;
- three-configuration production comparison: 125 rows, including 43 technical and 76 equipment rows;
- dynamic-facet regression proving that incomplete and universally available equipment are hidden;
- versioned release archive regression allowing only whitelisted official Dacia Polska HTTPS media URLs and requiring a local SVG fallback;
- full repository unit-test discovery: PASS.

## Publication

`data-products-v1.6.0` was published from exact merged `main` commit `539fba58d1ee2ef538c782b20e049be482d72988`. The immutable release contains 69 active configurations and 18 independent scopes. Its exact public assets were downloaded again, accepted by the release verifier and audited for 79 archive members, 88 technical comparison facets, 109 equipment facets and five official model-media entries.
