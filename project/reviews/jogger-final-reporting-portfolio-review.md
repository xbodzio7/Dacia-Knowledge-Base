# Final Jogger Reporting Portfolio Review

## Decision status

`SELECTED`

The review selects the six current Hybrid 155 automatic configurations as the next explicit Jogger reporting subset.

## Evidence baseline

The Eco-G 120 automatic and Eco-G 120 manual groups are now independently promoted. The remaining portfolio contains 12 active configurations, 306 source-backed technical observations, 636 equipment-availability records and 12 dated catalogue prices.

Every remaining configuration has exactly 53 imported equipment attributes and one price observation from `src_pl_jogger_price_my26_20260401`. Technical coverage remains evaluated against each powertrain's explicit scalar and closed-range slots. Attributes absent from the source are not treated as artificial gaps, and ranges remain first-class observations.

## Portfolio review

| Powertrain group | Configurations | Technical slots | Scalar slots | Range slots | Technical observations | Equipment observations | Prices | Pairs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Hybrid 155 automatic | 6 | 27 | 23 | 4 | 162 | 318 | 6 | 15 |
| TCe 110 manual | 6 | 24 | 19 | 5 | 144 | 318 | 6 | 15 |

Both groups are source-complete within their own denominators and support 15 deterministic pairs. They remain separate because hybrid component and total-system observations are not stated for TCe 110, while TCe-specific engine-speed ranges and single-fuel semantics must not be projected onto Hybrid 155.

## Selection

Hybrid 155 automatic is selected first because it:

- has the larger remaining technical denominator, with 27 slots and 162 observations;
- preserves the source's hybrid-specific component and total-system observations rather than reducing the powertrain to generic combustion-engine fields;
- includes four explicit range slots, including the source-stated acceleration interval, without endpoint inference;
- covers expression, extreme and journey in both five- and seven-seat form;
- is complete across technical, equipment, price and source evidence without an exception or a new architecture decision.

TCe 110 manual remains the final homogeneous Jogger reporting candidate. Its six configurations, 24 technical slots, 318 equipment observations, six prices and 15 pairs will follow after the Hybrid 155 promotion.

The selected configurations are:

- `jogger_expression_5seat_hybrid155_automatic`;
- `jogger_extreme_5seat_hybrid155_automatic`;
- `jogger_journey_5seat_hybrid155_automatic`;
- `jogger_expression_7seat_hybrid155_automatic`;
- `jogger_extreme_7seat_hybrid155_automatic`;
- `jogger_journey_7seat_hybrid155_automatic`.

## Implementation contract

The next package will:

1. add `data/reporting/jogger_hybrid155_automatic_completeness.json` selecting exactly the six configurations above;
2. declare 27 technical slots, preserving 23 scalar and four closed-range observations per configuration, and reuse the 53 source-backed Jogger equipment attributes;
3. add an empty, validated gap-evidence specification because the selected denominator has no missing technical or equipment observations;
4. publish separate completeness, source-coverage and comparison JSON and Markdown artifacts plus a flat differences CSV under a `jogger-hybrid155-automatic` prefix;
5. publish a reproducible artifact manifest through a dedicated Quality workflow;
6. preserve every existing Sandero, Duster and Jogger Eco-G reporting scope and artifact namespace unchanged.

Expected completeness is 162/162 technical observations, 318/318 equipment observations, 6/6 prices, complete source evidence and 15 comparable configuration pairs with zero not-comparable states.

## Boundary

This decision does not create cross-powertrain comparisons and does not promote TCe 110 in the same package. After the Hybrid 155 automatic promotion, TCe 110 manual becomes the final planned Jogger reporting scope.
