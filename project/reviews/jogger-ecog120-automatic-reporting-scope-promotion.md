# Jogger Eco-G 120 Automatic Reporting Scope Promotion

## Status

`IMPLEMENTING`

This package promotes the four configurations selected in PR #130 into an explicit independent reporting scope. It changes no source data.

## Scope

The scope contains extreme and journey, each in five- and seven-seat Eco-G 120 automatic form. One registered Jogger MY26 source documents all four configurations.

## Denominator

Each configuration has 34 technical slots: 25 scalar observations and nine closed ranges. The scope therefore contains 136 technical observations, 212 equipment observations across 53 attributes and four dated catalogue prices.

The nine range slots remain intervals for LPG and petrol CO2, fuel consumption, maximum-power speed and maximum-torque speed, plus maximum payload. No endpoint, midpoint or average substitutes for a range.

## Comparison contract

Six deterministic pairs produce:

- 6 price comparisons: all different;
- 204 technical comparisons: 172 equal, 32 different and zero not comparable;
- 318 equipment comparisons: 282 equal, 36 different and zero not comparable;
- 74 total differences.

Exactly 54 technical comparisons preserve range states and `range_relation` semantics.

## Source and completeness contract

Completeness is 136/136 technical observations and 212/212 equipment observations. Source coverage includes four prices, 16/16 covered areas and 108/108 covered sections. The validated gap-evidence specification is empty.

## Artifacts

Quality publishes JSON and Markdown completeness and source-coverage reports, JSON and Markdown comparison reports and a flat comparison-differences CSV under the `jogger-ecog120-automatic` prefix.

## Expected baseline

- 551 tests;
- 37 master CSV files and 5,155 rows;
- 1,204 scalar values and 71 scalar specifications;
- 144 range values and 19 range specifications;
- 2,977 availability records;
- 357 attributes in 30 categories.

## Next package

**Remaining Jogger Reporting Portfolio Review** will select the next homogeneous Jogger powertrain group.
