# Sandero Eco-G 120 Manual Reporting Scope Promotion

## Status

`IMPLEMENTED`

This package promotes the five source-backed Sandero Eco-G 120 manual configurations into an independent reporting scope. It changes no master data and preserves all verified source-gap decisions.

## Scope

The reporting scope contains:

- Sandero expression Eco-G 120 manual;
- Sandero journey Eco-G 120 manual;
- Sandero Stepway essential Eco-G 120 manual;
- Sandero Stepway expression Eco-G 120 manual;
- Sandero Stepway extreme Eco-G 120 manual.

Each configuration retains its own registered Polish configuration PDF dated 2026-06-26.

## Denominator and evidence contract

The scope contains 45 technical slots per configuration and 69 equipment attributes per configuration:

- 225 technical observations: 221 present and four missing;
- 345 equipment observations: 298 recorded and 47 missing;
- five dated catalogue prices;
- ten deterministic within-transmission pairs.

The full denominator is preserved. The filtered evidence specification contains 51 reviewed decisions: 34 `not_stated` and 17 `out_of_scope`. Missing records are not inferred, converted to `not_available`, or removed from comparison.

## Comparison contract

The ten `different_version_same_transmission` pairs produce:

- 450 technical comparisons: 318 equal, 122 different and ten not comparable;
- 690 equipment comparisons: 528 equal, 14 different and 148 not comparable;
- ten price comparisons: all different;
- 146 total differences.

Sandero technical observations in this scope are scalar; no interval comparison is introduced.

## Source coverage

All five required sources are registered and metadata-complete. Source coverage records:

- 11 covered and nine partial areas out of 20;
- 134 covered, 29 partial and seven missing sections out of 170;
- 221 technical records, 298 equipment records and five prices.

The 51 source-coverage gaps correspond to the preserved evidence decisions.

## Artifacts

The dedicated workflow publishes JSON and Markdown completeness and source-coverage reports, JSON and Markdown comparison reports, a flat comparison-differences CSV and a SHA-256 manifest under the `sandero-ecog120-manual` prefix.

## Expected baseline

- 579 tests;
- 37 master CSV files and 5,155 rows;
- 1,204 scalar configuration values and 71 scalar import specifications;
- 144 range values and 19 range import specifications;
- 2,977 equipment-availability records;
- 357 attributes in 30 categories.

## Next package

**Sandero Stepway Eco-G 120 Automatic Reporting Scope Promotion** will promote the separate two-configuration automatic group with its own filtered evidence contract.
