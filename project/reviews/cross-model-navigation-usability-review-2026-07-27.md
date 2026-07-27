# Cross-Model Navigation Usability Review

Date: 2026-07-27

## Decision

Select a conditional fifth `Start here` card in the generated workspace `index.html`.

The card should be titled `Models and comparison scopes`, describe the product as a route from model families to existing reports and link to:

```text
contents/cross-model/cross-model-comparison-view.html
```

It must appear only when the exact verified release member `cross-model/cross-model-comparison-view.html` exists.

## Current discoverability gap

Public `data-products-v1.8.1` contains 85 verified content files. Its generated workspace index contains 83 local links:

- four primary product cards;
- 76 report links across 19 scopes;
- three original-asset links.

The current primary cards lead to the shortlist, workbook, bundle manifest and release notes. Neither cross-model member is linked from the landing page.

The published cross-model HTML already presents five model families, 19 established scopes and 57 local report launches. It is deterministic, offline, JavaScript-free and creates no new comparison pair. Without a landing-page link, the user must know its internal path or discover it through documentation outside the workspace.

## Selected option

For a release containing the verified HTML member:

- the primary-card count changes from four to five;
- the current v1.8.1 workspace local-link count changes from 83 to 84;
- the card opens the existing immutable cross-model HTML;
- the workspace index does not parse cross-model JSON or duplicate model cards.

For an older release without the member, the index retains four primary cards.

## Why this option

The dedicated product already contains the model-family and scope navigation. Recreating that structure in `index.html` would duplicate logic and increase maintenance risk.

Adding search, filtering or return navigation inside the cross-model page would change an immutable release member and require a new semantic version. That is unnecessary to close the current discovery gap.

The selected card is therefore the smallest change with the highest consumer value. It uses the existing verified-inventory and safe-path mechanisms, requires no new architecture and leaves release assets untouched.

## Implementation contract

The implementation package must:

- detect the exact HTML member in the verified release manifest;
- require the corresponding file under `contents/`;
- use existing safe relative-path and percent-encoding helpers;
- add exactly one primary card when present;
- retain exactly four primary cards when absent;
- keep the cross-model JSON as a non-primary machine-readable product;
- preserve an offline, JavaScript-free workspace index;
- cover member-present and member-absent fixtures;
- verify every local link;
- preserve deterministic Linux/Windows bytes;
- smoke-test a public v1.8.1 download.

## Boundaries

This review changes no public tag or release asset, imports no data and changes no schema or comparison engine. It creates no pair, ranking, recommendation or inferred value.

The historical v1.8.1 audit remains exact at 83 workspace links. A later downloader implementation may generate an 84-link index from the same immutable assets; that does not rewrite the historical public audit.

## Next package

`Cross-Model Workspace Entry Point` — implement the selected conditional primary card and compatibility tests without modifying or republishing `data-products-v1.8.1`.
