# Jogger TCe 110 Manual Reporting Scope Promotion

## Status

`IMPLEMENTED`

This package promotes the final six homogeneous current Jogger configurations into an explicit independent reporting scope. It changes no source data.

## Scope

The scope contains expression, extreme and journey, each in five- and seven-seat TCe 110 manual form. One registered Jogger MY26 source documents all six configurations.

## Denominator

Each configuration has 24 technical slots: 19 scalar observations and five closed ranges. The scope therefore contains 144 technical observations, 318 equipment observations across 53 attributes and six dated catalogue prices.

The five range slots preserve petrol WLTP CO2 and fuel-consumption intervals, maximum-power and maximum-torque speed intervals, and maximum-payload interval. No endpoint, midpoint or average substitutes for a range.

## Comparison contract

Fifteen deterministic pairs produce:

- 15 price comparisons: all different;
- 360 technical comparisons: 297 equal, 63 different and zero not comparable;
- 795 equipment comparisons: 663 equal, 132 different and zero not comparable;
- 210 total differences.

Exactly 75 technical comparisons preserve range states: 66 identical and nine disjoint.

## Source and completeness contract

Completeness is 144/144 technical observations and 318/318 equipment observations: 254 standard, 24 optional and 40 not available. Source coverage includes six prices, 24/24 covered areas and 162/162 covered sections. The validated gap-evidence specification is empty.

## Artifacts

The dedicated Jogger reporting workflow publishes JSON and Markdown completeness and source-coverage reports, JSON and Markdown comparison reports, a flat comparison-differences CSV and a SHA-256 manifest under the `jogger-tce110-manual` prefix.

## Expected baseline

- 572 tests;
- 37 master CSV files and 5,155 rows;
- 1,204 scalar values and 71 scalar specifications;
- 144 range values and 19 range specifications;
- 2,977 availability records;
- 357 attributes in 30 categories.

## Next package

**Jogger Reporting Portfolio Completion Review** will verify and close the current Jogger reporting milestone.
