# Sandero Stepway Eco-G 120 Automatic Reporting Scope Promotion

## Status

`IMPLEMENTED`

This package promotes the two source-backed Sandero Stepway Eco-G 120 automatic configurations into an independent reporting scope. It changes no master data and preserves all verified source-gap decisions.

## Scope

The reporting scope contains Sandero Stepway expression and extreme Eco-G 120 automatic. Each configuration retains its own registered Polish configuration PDF dated 2026-06-26.

## Denominator and evidence contract

The scope contains 45 technical slots and 69 equipment attributes per configuration:

- 90 technical observations: 89 present and one missing;
- 138 equipment observations: 121 recorded and 17 missing;
- two dated catalogue prices;
- one deterministic within-transmission pair.

The full denominator is preserved. The filtered evidence specification contains 18 reviewed decisions: ten `not_stated` and eight `out_of_scope`. Missing records are not inferred, converted to `not_available`, or removed from comparison.

## Comparison contract

The one `different_version_same_transmission` pair produces:

- 45 technical comparisons: 37 equal, seven different and one not comparable;
- 69 equipment comparisons: 55 equal, one different and 13 not comparable;
- one price comparison: different;
- nine total differences.

Sandero technical observations in this scope are scalar; no interval comparison is introduced.

## Source coverage

Both required sources are registered and metadata-complete. Source coverage records:

- five covered and three partial areas out of eight;
- 58 covered, eight partial and two missing sections out of 68;
- 89 technical records, 121 equipment records and two prices.

The 18 source-coverage gaps correspond to the preserved evidence decisions.

## Artifacts

The dedicated workflow publishes JSON and Markdown completeness and source-coverage reports, JSON and Markdown comparison reports, a flat comparison-differences CSV and a SHA-256 manifest under the `sandero-stepway-ecog120-automatic` prefix.

## Expected baseline

- 586 tests;
- 37 master CSV files and 5,155 rows;
- 1,204 scalar configuration values and 71 scalar import specifications;
- 144 range values and 19 range import specifications;
- 2,977 equipment-availability records;
- 357 attributes in 30 categories.

## Next package

**Sandero Reporting Portfolio Completion Review** will verify that all seven current Sandero configurations have isolated evidence-aware reporting scopes.
