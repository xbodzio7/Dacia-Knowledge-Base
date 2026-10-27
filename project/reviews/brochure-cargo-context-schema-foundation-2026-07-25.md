# Brochure Cargo Context Schema Foundation Review

Date: 2026-07-25

## Scope

This package implements the storage and integrity foundation chosen by D-023. It does
not import Sandero, Sandero Stepway, Jogger, Bigster or Duster brochure cargo values.

## Relation

`configuration_cargo_volume_contexts.csv` is optional and one-to-one with
`configuration_attribute_values.code`. Its required fields are the referenced value,
measurement basis and compartment. Seat-row and equipment qualifiers remain optional;
an empty optional field means that the source did not state that dimension.

## Controlled vocabularies

Measurement basis distinguishes VDA/ISO 3832 from ordinary source-stated litres. Seat
states preserve upright, folded, removed and explicitly grouped folded-or-removed
wording. Compartment types distinguish main, underfloor and source-stated total volume.
Presence states contain only explicit present and absent meanings.

## Semantic boundary

The semantic validator rejects:

- more than one context row for the same value code;
- a context row attached to any attribute other than `boot_capacity`.

Foreign-key validation separately rejects missing values and invalid dictionary codes.
No inference is made between spare wheel, repair kit and double floor.

## Tooling coverage

The generic SQLite builder and data-dictionary generator discover all five new CSVs
without special cases. Regression tests prove the empty production relation, exact
vocabularies, references, statuses, semantic failures, SQLite tables and dictionary
sections.

## Follow-up

The next package must make reporting and comparison outputs context-aware. No brochure
cargo values should be imported until reports expose all context-distinct observations
instead of collapsing them into one scalar.
