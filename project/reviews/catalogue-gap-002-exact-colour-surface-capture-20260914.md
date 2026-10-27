# CAT-GAP-002 — exact colour surface capture

Date: 2026-09-14

## Scope

CAT-GAP-002 covers 81 active exact colour compatibility surfaces. The target is the exact compatibility relation between colour choices and active configuration states, not a generic grade-level list of colours.

## Current official evidence

The current official Dacia configurator exposes colour choices for an observed default state.

### Jogger 5-seat

Source: https://www.dacia.pl/samochody/jogger-hybydowy/konfigurator.html

Observed default state: `essential Eco-G 120 5-miejsc`.

Observed colours:

- `biel alpejska`
- `szary schiste`
- `czarna perła`

### Jogger 7-seat

Source: https://www.dacia.pl/samochody/jogger-ri1-ph2-7seats/konfigurator.html

Observed default state: `essential Eco-G 120 7-miejsc`.

Observed colours:

- `biel alpejska`
- `szary schiste`
- `czarna perła`

## Evidence boundary

These pages establish the colours exposed for the observed exact default states. They do **not** establish the complete compatibility graph across all active grades, powertrains, transmissions and other state-defining selectors.

In particular, a colour visible in one state must not be projected into another state without direct evidence from that state.

## Repository action

No canonical observations, configuration values, import specifications, availability rows, master-data values or attributes are added by this package.

The package records the evidence boundary so that future exact-state capture can proceed without treating static page lists as compatibility evidence.

## Blocker

The current session can retrieve the official configurator pages but cannot reproduce interactive selector changes and capture the resulting exact state for each target surface. Therefore CAT-GAP-002 remains blocked for exact-state capture.

## Explicit exclusions

- no inference from grade-level colour lists;
- no cross-configuration projection;
- no schema/master-data expansion;
- no reopening of the closed Sandero Stepway full-modal evidence boundary;
- no changes to historical PR #634, #637 or #639.
