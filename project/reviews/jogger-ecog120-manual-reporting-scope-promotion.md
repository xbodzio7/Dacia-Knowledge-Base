# Jogger Eco-G 120 Manual Reporting Scope Promotion

## Status

`IMPLEMENTED`

This package promotes the six configurations selected in PR #132 into an explicit independent reporting scope. It changes no source data.

## Scope

The scope contains essential, expression and extreme, each in five- and seven-seat Eco-G 120 manual form. One registered Jogger MY26 source documents all six configurations.

## Denominator

Each configuration has 34 technical slots: 25 scalar observations and nine closed ranges. The scope therefore contains 204 technical observations, 318 equipment observations across 53 attributes and six dated catalogue prices.

The nine range slots remain intervals for LPG and petrol CO2, fuel consumption, maximum-power speed and maximum-torque speed, plus maximum payload. No endpoint, midpoint or average substitutes for a range.

## Comparison contract

Fifteen deterministic pairs produce:

- 15 price comparisons: all different;
- 510 technical comparisons: 438 equal, 72 different and zero not comparable;
- 795 equipment comparisons: 607 equal, 188 different and zero not comparable;
- 275 total differences.

Exactly 135 technical comparisons preserve range states and `range_relation` semantics: 126 identical intervals and nine disjoint intervals.

## Source and completeness contract

Completeness is 204/204 technical observations and 318/318 equipment observations. The equipment records contain 230 `standard`, 24 `optional` and 64 `not_available` states. Source coverage includes six prices, 24/24 covered areas and 162/162 covered sections. The validated gap-evidence specification is empty.

## Artifacts

The dedicated Jogger reporting workflow publishes JSON and Markdown completeness and source-coverage reports, JSON and Markdown comparison reports, a flat comparison-differences CSV and a SHA-256 manifest under the `jogger-ecog120-manual` prefix.

## Expected baseline

- 558 tests;
- 37 master CSV files and 5,155 rows;
- 1,204 scalar values and 71 scalar specifications;
- 144 range values and 19 range specifications;
- 2,977 availability records;
- 357 attributes in 30 categories.

## Next package

**Remaining Jogger Reporting Portfolio Review** will select between the TCe 110 manual and Hybrid 155 automatic groups.
