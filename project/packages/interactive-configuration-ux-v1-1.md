# Interactive Configuration UX v1.1

Date: 2026-07-21

## Purpose

Implement the first user-feedback release after the immutable `data-products-v1.0.0` publication. The package improves the offline configuration shortlist without changing source-data semantics or rewriting the existing v1.0.0 release.

## User-facing changes

### Persistent equipment selection summaries

Each scrollable multi-select equipment filter now has a summary placed above the list. It shows:

- the number of selected items;
- every selected item as a removable chip;
- an individual remove action;
- a clear-all action.

The underlying scrollable list keeps a stable order. Selecting an item therefore does not move the list or make the cursor position jump.

Separate summaries are retained for:

- equipment that may be standard or optional;
- equipment that must be standard.

### Polish equipment labels

The browser layer presents maintained Polish labels for the equipment used by the current catalogues. Stable internal codes remain unchanged and are available through control titles and exported data. Exact source wording and page provenance remain in repository observations rather than being replaced by interface copy.

### Configuration price breakdown

Each configuration card now distinguishes:

1. configuration price;
2. standard catalogue price;
3. known selected option or package surcharges;
4. selected optional equipment whose surcharge is not present in source-backed data;
5. selected standard equipment already included in the standard price.

Known surcharges are added exactly once. A package may declare which equipment codes it covers so covered items are not listed or charged again as separate options.

When one or more selected optional items have no recorded amount, the card shows an `od` price and the explicit label `cena nieustalona`. Unknown amounts are not silently treated as zero and are not included in the displayed sum.

### Selected configuration visibility

A selected configuration card receives a visible border and selection background in addition to its checked control. Selection state is therefore not communicated by colour alone.

## Data boundary

The current master data contains dated catalogue gross prices for configurations and availability states for equipment. It does not yet contain a complete dated commercial price model for named packages and individual options.

Version 1.1 therefore implements a forward-compatible `price_components` rendering contract but does not invent commercial amounts. Current optional selections without a source-backed amount are displayed as unknown.

The planned **Source-Backed Commercial Option Pricing** package will add commercial entities and dated price observations only after suitable official source evidence is registered.

## Technical changes

- add `tools/reporting/configuration_shortlist_labels_pl.json`;
- add `tools/reporting/configuration_shortlist_v11_pricing.js`;
- add `tools/reporting/configuration_shortlist_v11.js`;
- extend `configuration_shortlist_selection_html.py` with v1.1 styles and script injection;
- retain the existing browser filtering and selection-export contracts;
- add a Node contract covering Polish labels, known package prices, unknown optional prices, standard-price inclusion and complete/incomplete totals;
- run the contract in the existing Configuration Shortlist HTML workflow.

## Compatibility

The following remain unchanged:

- configuration codes and exported selection JSON/TXT formats;
- filter semantics for `standard`, `optional`, `not_available` and missing records;
- source-backed catalogue prices;
- immutable public `data-products-v1.0.0` assets;
- the 667-test Python baseline;
- current Python 3.10 support during its published deprecation period.

The previously planned Python 3.10 retirement implementation remains required before or with upstream end of support in October 2026, but is deferred behind the user-facing v1.1 and commercial-pricing work.

## Validation

The package is validated by:

- JavaScript syntax checks;
- a deterministic Node contract for v1.1 price and label behaviour;
- the existing Python/JavaScript shortlist-filter parity suite;
- generation of both complete and filtered offline HTML artifacts;
- the repository Pull Request quality portfolio.
