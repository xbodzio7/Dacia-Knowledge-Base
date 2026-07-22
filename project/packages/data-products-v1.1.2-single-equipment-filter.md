# Data Products v1.1.2 Single Equipment Filter

Date: 2026-07-22

## Purpose

Make equipment selection reflect the buyer's intent: choose the desired feature once, regardless of whether a matched configuration includes it as standard equipment, a package or an individual option.

The immutable `data-products-v1.1.1` release remains unchanged. The correction is published as patch release `data-products-v1.1.2`.

## Browser behavior

- one visible `Wyposażenie` picker replaces the separate standard-or-optional and standard-only controls;
- a browser result matches when every selected item is either standard or available optionally;
- legacy initial standard-only values are merged into the one visible picker;
- duplicated equipment badges are removed from result cards;
- the end of each matched price block contains `Wybrane wyposażenie` and explains each selected item's delivery path;
- the explanation distinguishes `w standardzie — bez dopłaty`, a named package, a named individual option and an unknown surcharge.

The core non-browser shortlist contract still supports explicit standard-only filtering for CLI and API consumers.

## Verification

The exact release HTML was exercised in Chromium. It contained one equipment picker, no standard-only picker and displayed selected-equipment status in matched price breakdowns without JavaScript errors.

All 15 Pull Request workflows passed on head `4c64e0c4bd949021b6d2f739426849f9183d5b11`, including `Quality` run 1176, Python 3.10, 3.13 and 3.14, Windows, `Configuration Shortlist HTML`, `Configuration Selection Export`, the workbook and the versioned release builder.

## Publication

`data-products-v1.1.2` was published from exact main commit `8b08dbd8d846610577437c150a0d39aeb3d868f4`. The three public assets were downloaded again and accepted by the independent release verifier.
