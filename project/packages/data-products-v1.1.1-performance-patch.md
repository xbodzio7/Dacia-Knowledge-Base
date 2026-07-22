# Data Products v1.1.1 Performance Patch

Date: 2026-07-22

## Purpose

Remove the browser stall reported when selecting equipment in the self-contained configuration shortlist while preserving the complete `data-products-v1.1.0` dataset, evidence semantics, selection exports and comparison outputs.

The immutable `data-products-v1.1.0` release remains unchanged. The correction is published as patch release `data-products-v1.1.1`.

## Root cause

The v1.2 card enhancement observed the complete results subtree and then rewrote equipment badge text inside that same subtree. Those writes triggered the observer again, creating a self-sustaining microtask refresh loop after an equipment filter changed the result cards.

The equipment picker also emitted both `input` and `change` for one click, causing duplicate complete filtering and rendering. Package-price coverage used bit-shift subset enumeration, which was also unsafe for larger candidate sets.

## Correction

- replace mutation-driven synchronization with one explicit `dkb:results-rendered` lifecycle event;
- make badge localization idempotent;
- emit one `change` event per equipment selection;
- use one native event type per control;
- batch card enhancement work in the next animation frame;
- replace bit-shift package enumeration with deterministic dynamic programming keyed by required-equipment coverage.

## Browser validation

The exact `data-products-v1.1.0` HTML did not complete the first tested equipment click within 10 seconds in headless Chromium. The corrected release HTML completed seven consecutive equipment selections without JavaScript errors. Synchronous click handling measured approximately 8-17 ms in the final release verification environment.

## Repository validation

All 15 Pull Request workflows passed on the final six-file commit, including `Configuration Shortlist HTML`, `Configuration Selection Export`, `Versioned Data Product Release`, `Configuration Comparison Workbook` and `Quality` run 1149 across Python 3.10, 3.13, 3.14 and Windows.

## Publication

`data-products-v1.1.1` was published from exact main commit `b333f74e8426993e797a79c2e8621bd2f0f7bf4e`. Its three public assets were downloaded again and accepted by the independent release verifier. Durable identities and hashes are recorded in `project/releases/data-products-v1.1.1.md`.
