# Sandero Reporting Portfolio Completion Review

## Decision status

`COMPLETE`

All seven current Sandero configurations now have independent reporting scopes separated by transmission. The historical mixed reporting specification remains available for backward-compatible tooling, but current promotion, regression and artifact contracts use the manual and automatic scopes independently.

## Scope inventory

| Reporting scope | Configurations | Sources | Technical denominator | Present technical | Equipment denominator | Recorded equipment | Prices | Pairs | Evidence decisions | Total differences |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Eco-G 120 manual | 5 | 5 | 225 | 221 | 345 | 298 | 5 | 10 | 51 | 146 |
| Stepway Eco-G 120 automatic | 2 | 2 | 90 | 89 | 138 | 121 | 2 | 1 | 18 | 9 |
| **Portfolio total** | **7** | **7** | **315** | **310** | **483** | **419** | **7** | **11** | **69** | **155** |

## Aggregate denominator

The Sandero portfolio preserves:

- 315 technical observations: 310 present and five explicit gaps;
- 483 equipment observations: 419 recorded and 64 explicit gaps;
- 389 standard, zero optional, 30 not-available and zero unknown equipment states;
- seven dated catalogue prices;
- 11 deterministic within-transmission pairs.

The denominator is not reduced to observed records. No missing source statement is converted into an inferred technical value or equipment availability state.

## Aggregate evidence contract

The two filtered evidence specifications contain 69 reviewed decisions:

- 44 `not_stated`;
- 25 `out_of_scope`;
- 64 equipment decisions;
- five technical decisions.

All evidence decisions originate from the registered configuration-specific PDFs dated 2026-06-26.

## Aggregate comparison contract

The isolated manual and automatic scopes contain:

- 495 technical comparisons: 355 equal, 129 different and 11 not comparable;
- 759 equipment comparisons: 583 equal, 15 different and 161 not comparable;
- 11 price comparisons: all different and zero not comparable;
- 155 total differences.

No Sandero technical observation is stored as a range, so the portfolio has no interval comparisons.

## Source coverage

All seven required sources are registered and metadata-complete. Aggregate source coverage contains:

- 16 covered and 12 partial areas out of 28;
- 192 covered, 37 partial and nine missing sections out of 238;
- 310 technical records, 419 equipment records and seven prices.

The 69 source-coverage gaps correspond exactly to the preserved evidence decisions.

## Isolation guarantees

The completion review confirms that:

- manual and automatic transmissions use separate configuration and pair denominators;
- automatic Stepway comparisons do not include Sandero hatchback or manual Stepway configurations;
- each scope has a distinct artifact prefix and dedicated regression workflow;
- source-specific `not_stated` and `out_of_scope` decisions remain visible;
- Duster and Jogger reporting contracts remain unchanged.

## Milestone result

The Sandero reporting milestone is complete. All current Sandero, Duster and Jogger configurations now have source-backed reporting coverage. The next package is a registered-source portfolio completion review to verify the whole 53-configuration repository and identify whether any further expansion can proceed without new source material.
