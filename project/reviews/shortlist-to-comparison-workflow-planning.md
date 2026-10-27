# Shortlist-to-Comparison Workflow Planning Review

## Decision status

`SELECTED — CONFIGURATION COMPARISON BUNDLE CLI`

The next package will add a transparent bundle command that turns explicit configuration selections into existing source-backed comparison reports. It will preserve the 13 independent reporting scopes and will never create cross-scope pairs.

## Scope mapping audit

The repository contains:

- 13 independent current comparison scopes;
- 53 active configurations mapped exactly once;
- seven Duster scopes containing 24 configurations;
- four Jogger scopes containing 22 configurations;
- two Sandero scopes containing seven configurations;
- zero unmapped configurations;
- zero configurations assigned to more than one current scope.

Every current completeness specification has a matching evidence specification. Files with `.spec` and `.json` extensions both use the same JSON evidence structure.

## Subset validation

A two-configuration subset was executed through the existing comparison engine for every independent scope.

- all seven Duster scopes succeeded;
- all four Jogger scopes succeeded;
- Sandero Stepway Eco-G 120 automatic succeeded;
- Sandero Eco-G 120 manual correctly rejected the unfiltered evidence file because it contained decisions for three configurations excluded from the temporary subset.

This is expected evidence-contract behavior. A bundle implementation must filter both the completeness configuration list and the evidence `decisions` list to the selected configuration codes. It must not weaken evidence validation or ignore extra decisions.

## Selected command contract

The first implementation will provide `configuration-comparison-bundle` with:

- repeatable exact `--configuration-code CODE` inputs;
- optional `--shortlist-json FILE` input using `results[].configuration_code` from the existing shortlist report;
- deterministic deduplication of configuration codes;
- validation that every selected code is active and mapped exactly once;
- grouping by current independent completeness scope;
- a required output directory;
- one bundle manifest plus JSON, Markdown, CSV and HTML comparison files for every group containing at least two selected configurations;
- explicit singleton groups with no generated comparison;
- deterministic filenames based on the current scope name.

Direct codes and shortlist JSON may be combined. Their union defines the selection.

## Comparison semantics

For every comparable group the command will:

1. create an in-memory or temporary completeness specification containing only the selected configurations from that scope;
2. create a matching evidence specification containing only decisions for those selected configurations;
3. invoke the existing configuration comparison engine and renderers unchanged;
4. record report counts and output files in the bundle manifest.

The command will not introduce a new comparison denominator, pair algorithm or evidence classification.

## Bundle manifest

The manifest will contain:

- requested and deduplicated configuration codes;
- input sources used;
- scope-to-configuration assignments;
- comparable groups and singleton groups;
- generated report filenames and SHA-256 digests;
- pair and difference counts per comparable group;
- an explicit `cross_scope_pairs_generated: false` guarantee;
- unknown-code and malformed-shortlist errors before any output is published.

## Scope boundary

The package will not:

- compare configurations from different independent scopes;
- merge technical or equipment denominators;
- rank or score configurations;
- infer missing values;
- silently drop evidence decisions;
- create comparisons for singleton groups;
- add direct browser-to-browser file generation.

A future browser integration may export selected codes or consume a bundle produced by this CLI, but it must reuse this contract.

## Implementation target

The next package is **Configuration Comparison Bundle CLI**, with at least eight regression tests, unified CLI integration, a reproducible example workflow, documentation and canonical project-state synchronization.
