# Equipment Filter Regression and Model Price Ordering

Date: 2026-07-26

## User report

Public versions `data-products-v1.6.1` and `data-products-v1.7.0` do not provide usable equipment filtering or equipment selection. Model choices should also be displayed from the cheapest model to the most expensive model.

The same equipment regression is present in the current source used by `data-products-v1.8.0`, so the correction must be delivered through a new immutable patch release rather than rewriting older assets.

## Reproduction

The current generated shortlist contains:

- 72 active configurations;
- 110 equipment facets;
- zero visible equipment choices after the initial dynamic-facet refresh;
- no JavaScript exception.

The search input itself accepts text, but it cannot return a usable choice because every equipment button is hidden.

## Root cause

The dynamic equipment facet previously exposed an attribute only when every currently considered configuration had a complete, non-unknown source statement and the attribute differed between available and unavailable states.

After the portfolio expanded across five model families, every equipment attribute had at least one missing or unknown observation somewhere in the 72-configuration set. The source-completeness guard therefore hid all 110 attributes.

This was a user-interface regression, not evidence that equipment is absent.

## Corrected filtering semantics

An equipment attribute is visible when:

1. at least one currently compatible configuration has a source-confirmed `standard` or `optional` state; and
2. at least one other configuration is `not_available`, `unknown` or has no statement.

Selecting an attribute still matches only source-confirmed `standard` or `optional` states. Missing and unknown observations do not satisfy the filter and are never converted into availability.

Conflicting selections remain selected and visible. The interface must tell the user that no configuration satisfies the combination rather than silently removing a requirement.

## Browser verification target

For the current 72-configuration snapshot:

- 108 equipment choices are initially visible;
- searching for `kamera` leaves one visible choice: `Kamera cofania`;
- selecting it changes the selected-equipment count to one;
- the result count changes from 72 to 66;
- no JavaScript error occurs.

## Model order

Model choices are ordered by the lowest recorded current Polish catalogue gross price among their active configurations:

1. Sandero — 68,000 PLN;
2. Sandero Stepway — 71,700 PLN;
3. Jogger — 77,900 PLN;
4. Duster — 82,000 PLN;
5. Bigster — 101,400 PLN.

A model without any recorded current price sorts after all models with a known minimum. Model name and code provide deterministic tie-breakers.

Configuration result cards continue to sort by their individual catalogue prices, then model, version and configuration code.

## Data boundary

The package changes no master CSV data, equipment observations or comparison relationships. It adds no ranking, recommendation or inferred value.

The baseline remains:

- 46 CSV files;
- 9688 rows;
- 2949 scalar values;
- 244 value ranges;
- 4754 equipment-availability records;
- 385 attributes.

The target automated-test baseline is 1030.

## Release policy

Public releases 1.6.1, 1.7.0 and 1.8.0 remain immutable. The corrected interface will be prepared as `data-products-v1.8.1` after the source package is merged and passes independent browser, release and offline-workspace verification.

## Next package

`Data Products v1.8.1 Release Preparation` — prepare the patch release with restored equipment filtering and cheapest-to-most-expensive model ordering, without changing source-backed data or rewriting historical assets.
