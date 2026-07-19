# Jogger Hybrid 155 Automatic Reporting Scope Promotion

## Status

`IMPLEMENTED`

This package promotes the six configurations selected in PR #134 into an explicit independent reporting scope. It changes no source data.

## Scope

The scope contains expression, extreme and journey, each in five- and seven-seat Hybrid 155 automatic form. One registered Jogger MY26 source documents all six configurations.

## Denominator

Each configuration has 27 technical slots: 23 scalar observations and four closed ranges. The scope therefore contains 162 technical observations, 318 equipment observations across 53 attributes and six dated catalogue prices.

The four range slots preserve the source-stated acceleration interval, petrol WLTP CO2 and fuel-consumption intervals, and maximum-payload interval. No endpoint, midpoint or average substitutes for a range.

Hybrid-specific scalar observations preserve battery type and voltage, total system power, starter-generator power, traction-motor power and traction-motor torque without projecting Eco-G or TCe semantics onto the group.

## Comparison contract

Fifteen deterministic pairs produce:

- 15 price comparisons: all different;
- 405 technical comparisons: 351 equal, 54 different and zero not comparable;
- 795 equipment comparisons: 679 equal, 116 different and zero not comparable;
- 185 total differences.

Exactly 60 technical comparisons preserve range states: 51 identical and nine disjoint.

## Source and completeness contract

Completeness is 162/162 technical observations and 318/318 equipment observations: 258 standard, 22 optional and 38 not available. Source coverage includes six prices, 24/24 covered areas and 168/168 covered sections. The validated gap-evidence specification is empty.

## Artifacts

The dedicated Jogger reporting workflow publishes JSON and Markdown completeness and source-coverage reports, JSON and Markdown comparison reports, a flat comparison-differences CSV and a SHA-256 manifest under the `jogger-hybrid155-automatic` prefix.

## Expected baseline

- 565 tests;
- 37 master CSV files and 5,155 rows;
- 1,204 scalar values and 71 scalar specifications;
- 144 range values and 19 range specifications;
- 2,977 availability records;
- 357 attributes in 30 categories.

## Next package

**Jogger TCe 110 Manual Reporting Scope Promotion** will publish the final homogeneous Jogger powertrain group.
