# Brochure Cargo Context Reporting Foundation Review

Date: 2026-07-25

## Scope

This package changes reporting semantics only. It does not import values from the five
registered Dacia brochures and does not migrate legacy cargo attributes.

## Collapse prevention

The former latest-observation key `(configuration, attribute, fuel)` was insufficient for
canonical `boot_capacity`: two source-backed values with different seat or compartment
conditions could collide. The reporting key now adds the exact semantic cargo-context
signature. Scalar and range observation behavior outside this attribute remains unchanged.

## Missing-context behavior

For each pair, reporting uses the union of observed cargo signatures. A missing signature
on one side becomes a missing state and the comparison is `not_comparable`. If the whole
attribute is absent, the existing evidence state is retained and annotated with the exact
counterpart context. This prevents an upright main-compartment value from being compared
with a folded maximum value.

## Exposed context

Machine-readable outputs include the exact cargo-context object. Flat surfaces include a
deterministic context string containing all seven dimensions, including blank optional
values. The workbook additionally stores deterministic JSON for each side. Browser labels
show the context-distinct rows separately, and selection exports include the complete
cargo observations.

## Compatibility

When no cargo context exists, the old key, filter context and output counts are preserved.
The production relation remains empty, and a regression test pins the existing 305
difference rows and context counts.

## Verification

Synthetic fixtures prove equal and different context-matched values, missing counterpart
contexts, exact filters, catalog contexts, shortlist exports, browser facets and selection
JSON. Full repository quality and project-state checks remain required before merge.
