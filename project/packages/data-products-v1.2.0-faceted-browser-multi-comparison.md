# Data Products v1.2.0 Faceted Browser and Multi-Comparison

Date: 2026-07-23

## Purpose

Improve the offline configuration selector after direct user testing of `data-products-v1.1.2`. The package keeps the canonical data, evidence states and pricing semantics unchanged while making filtering and comparison usable without external tools.

## Dynamic equipment facets

The visible equipment list is derived from the configurations that satisfy all current non-equipment filters and the already accepted equipment choices.

- equipment absent from every compatible configuration is hidden;
- hidden equipment returns automatically when broader filters make it available again;
- a newly incompatible selection is removed before it can reduce the result set to zero;
- selected compatible equipment remains visible and removable;
- the interface explains when a choice was removed because no current variant could provide the complete requested set.

No missing source statement is converted into availability. Only source-backed `standard` and `optional` states are considered available.

## Multi-configuration comparison

The browser selection panel now compares any number of explicitly selected configurations directly in the same offline HTML file.

The comparison table includes model, version, powertrain, transmission, catalogue price, seat count, configured price and one row for every selected equipment item. Different values are highlighted and the table scrolls horizontally instead of imposing a two-configuration limit.

JSON and TXT exports remain available and preserve their existing deterministic contracts.

## Interface simplification

- remove the buyer-facing `Jawność wykluczeń i braków` diagnostics panel;
- remove the redundant global text-search control;
- stretch the equipment selector across the complete filter width;
- retain concise matched/excluded and missing-data counters at the top;
- keep detailed provenance on each result card.

## Offline model thumbnails

The package adds deterministic inline SVG silhouettes for Bigster, Duster, Jogger, Sandero and Sandero Stepway. They are generated from repository code, require no network access and appear in model choices, result cards and comparison headers.

These are model-oriented visual identifiers, not official vehicle photographs or colour/trim representations.

## Verification

- 700 Python tests;
- JavaScript syntax and v1.2 pricing contract checks;
- complete CSV validation, project-state and documentation-baseline checks;
- generated 67-configuration HTML exercised in Chromium;
- model filter reduced the visible equipment facet from 107 to 53 Jogger-compatible items;
- three selected configurations compared in one table without JavaScript console errors;
- all remaining quality-report commands executed independently after the monolithic local quality wrapper exceeded the execution window.

## Publication

`data-products-v1.2.0` was published from exact merged main commit `2982ff68b8e1f3097403d96afd1754ae473c2aa3`. The public release is final, contains the canonical three assets and was independently downloaded and accepted by `data-product-release --verify`.

The exact release HTML repeated the Chromium scenario with 67 initial configurations, 22 Jogger configurations, an equipment facet reduced from 107 to 53 possible choices, one compatible equipment selection and a three-configuration comparison without JavaScript errors.
