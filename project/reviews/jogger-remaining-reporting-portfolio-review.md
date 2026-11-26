# Remaining Jogger Reporting Portfolio Review

## Decision status

`SELECTED`

The review selects the six current Eco-G 120 manual configurations as the next explicit Jogger reporting subset.

## Evidence baseline

The registered Jogger catalogue contains four homogeneous powertrain groups. Eco-G 120 automatic has already been promoted as an independent four-configuration reporting subset. The remaining portfolio contains 18 active configurations, 510 source-backed technical observations, 954 equipment-availability records and 18 dated catalogue prices.

Every remaining configuration has exactly 53 imported equipment attributes and one price observation from `src_pl_jogger_price_my26_20260401`. Technical coverage is evaluated against the exact scalar and closed-range slots stated for each powertrain. Attributes not stated by the source are not converted into artificial gaps, and range observations are not flattened to representative values.

## Portfolio review

| Powertrain group | Configurations | Technical slots | Scalar slots | Range slots | Technical observations | Equipment observations | Prices | Pairs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Eco-G 120 manual | 6 | 34 | 25 | 9 | 204 | 318 | 6 | 15 |
| TCe 110 manual | 6 | 24 | 19 | 5 | 144 | 318 | 6 | 15 |
| Hybrid 155 automatic | 6 | 27 | 23 | 4 | 162 | 318 | 6 | 15 |

All three groups are source-complete within their own explicit denominators. They must remain separate because the source does not state one common technical slot set across the three powertrains. Dual-fuel observations, hybrid component values and powertrain-specific ranges remain limited to the groups for which the source states them.

## Selection

Eco-G 120 manual is selected before the other groups because it:

- ties for the widest remaining portfolio with six configurations and 15 deterministic pairs;
- has the largest remaining technical denominator, with 34 slots and 204 observations;
- reuses the exact 25-scalar and nine-range dual-fuel semantics already verified by the Eco-G 120 automatic reporting package;
- adds `essential` and `expression` coverage in both five- and seven-seat form while retaining `extreme`;
- has complete technical, equipment, price and source coverage without an evidence exception or a new architecture decision.

Hybrid 155 automatic and TCe 110 manual remain complete candidates. Hybrid 155 carries the richer of those two technical denominators, while TCe 110 is the simplest single-fuel group. Both remain for the next portfolio review after the Eco-G 120 manual promotion.

The selected configurations are:

- `jogger_essential_5seat_ecog120_manual`;
- `jogger_expression_5seat_ecog120_manual`;
- `jogger_extreme_5seat_ecog120_manual`;
- `jogger_essential_7seat_ecog120_manual`;
- `jogger_expression_7seat_ecog120_manual`;
- `jogger_extreme_7seat_ecog120_manual`.

## Implementation contract

The next package will:

1. add `data/reporting/jogger_ecog120_manual_completeness.json` selecting exactly the six configurations above;
2. declare the same 34 mixed scalar/range technical slots used by the Eco-G 120 automatic scope and reuse the 53 source-backed Jogger equipment attributes;
3. add an empty, validated gap-evidence specification because the selected denominator has no missing technical or equipment observations;
4. publish separate completeness, source-coverage and comparison JSON and Markdown artifacts plus a flat differences CSV under a `jogger-ecog120-manual` prefix;
5. publish a reproducible artifact manifest through a dedicated Quality workflow;
6. preserve the default Sandero scope, every Duster reporting scope and the Jogger Eco-G 120 automatic artifacts and denominators unchanged.

Expected completeness is 204/204 technical observations, 318/318 equipment observations, 6/6 prices, complete source evidence and 15 comparable configuration pairs with zero not-comparable states.

## Boundary

This decision does not combine manual and automatic Eco-G configurations into one reporting denominator and does not promote TCe 110 or Hybrid 155. Cross-powertrain comparison remains outside the package. After the Eco-G 120 manual promotion, the portfolio review resumes with the two remaining homogeneous groups.
