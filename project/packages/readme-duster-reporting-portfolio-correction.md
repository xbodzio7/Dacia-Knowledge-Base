# README Duster Reporting Portfolio Correction

Date: 2026-07-20
Issue: #173

## Purpose

Correct two stale README statements that still described Duster as waiting for reporting-scope promotion after the complete registered-source reporting portfolio had already been delivered.

## Source of truth

Merged PR #142 closed the active registered-source portfolio with:

- 53 of 53 active configurations assigned exactly once;
- 13 independent homogeneous reporting scopes;
- 2 Sandero, 7 Duster and 4 Jogger scopes;
- 24 Duster configurations;
- a Duster technical denominator of 392;
- a Duster equipment denominator of 1,392;
- 30 deterministic Duster comparison pairs.

## Corrected statements

The README no longer says that Duster entities remain outside the reporting subset pending a future promotion decision.

It now states that all 24 Duster configurations belong to seven independent homogeneous Duster reporting scopes inside the completed thirteen-scope portfolio.

The README also no longer presents the first four-configuration Eco-G 120 promotion as the current Duster reporting boundary. It now summarizes the complete Duster portfolio with its configuration, denominator and pair counts.

## Preserved context

The correction preserves:

- the official Polish catalogue date of 6 February 2026;
- five active Duster versions and 24 source-backed configurations;
- 392 dated technical observations across 17 canonical attributes;
- 1,392 dated equipment-availability records across 58 canonical attributes;
- the distinction between dated catalogue prices and non-catalogue promotional or financing benefits;
- source-linked, dated value and evidence semantics.

## Unchanged scope

This package does not change:

- source data or master CSV files;
- product code or tests;
- reporting specifications or generated products;
- workflow behavior;
- the immutable `data-products-v1.0.0` release;
- the verified 667-test baseline.

## Validation contract

1. Each stale README block exists exactly once before replacement.
2. Neither stale block remains afterward.
3. Each corrected block exists exactly once.
4. The final diff contains README, this package record and canonical state files only.
5. Normal Quality and product workflow checks pass.

## Implementation evidence

A branch-only deterministic generator matched both stale blocks exactly once, applied exactly two replacements, rejected any remaining stale wording and produced the corrected README blob `677c7051baeb28e2a832f0e5f1687a548cf0e8d2`. The generator was removed in the same atomic tree update that installed that blob.

## Result

The public repository description now matches the completed reporting portfolio already represented by the data, reporting specifications and verified products.
