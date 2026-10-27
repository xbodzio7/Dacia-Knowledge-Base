# Jogger Reporting Portfolio Completion Review

## Decision status

`COMPLETE`

The current Jogger MY26 portfolio now has an independent, source-complete reporting scope for every homogeneous powertrain and transmission group. No cross-powertrain denominator is introduced.

## Scope inventory

| Reporting scope | Configurations | Technical observations | Equipment observations | Prices | Pairs | Range comparisons | Total differences |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Eco-G 120 automatic | 4 | 136 | 212 | 4 | 6 | 54 | 74 |
| Eco-G 120 manual | 6 | 204 | 318 | 6 | 15 | 135 | 275 |
| Hybrid 155 automatic | 6 | 162 | 318 | 6 | 15 | 60 | 185 |
| TCe 110 manual | 6 | 144 | 318 | 6 | 15 | 75 | 210 |
| **Portfolio total** | **22** | **646** | **1,166** | **22** | **51** | **324** | **744** |

## Aggregate contract

All 646 technical observations and all 1,166 equipment observations are present within their source-stated group denominators. Equipment states aggregate to 920 standard, 84 optional and 162 not available, with zero unknown records.

The four independent comparison scopes contain:

- 1,479 technical comparisons: 1,258 equal, 221 different and zero not comparable;
- 2,703 equipment comparisons: 2,231 equal, 472 different and zero not comparable;
- 51 price comparisons: all different and zero not comparable;
- 744 total differences.

Exactly 324 technical comparisons preserve interval semantics: 293 identical and 31 different. Every difference is represented as a source-backed comparison state rather than a flattened midpoint or inferred scalar.

## Source coverage

The portfolio contains 22 dated catalogue prices, 88/88 covered source areas and 600/600 covered source sections. Every scope uses the registered source `src_pl_jogger_price_my26_20260401` and an empty validated gap-evidence specification.

## Isolation guarantees

The completion review confirms that:

- Eco-G dual-fuel observations remain isolated from single-fuel and hybrid groups;
- manual and automatic Eco-G configurations retain separate denominators;
- hybrid battery, motor and system-power observations remain limited to Hybrid 155;
- TCe engine-speed ranges remain limited to TCe 110;
- every scope has a distinct artifact prefix and dedicated regression workflow;
- Sandero and Duster reporting contracts remain unchanged.

## Milestone result

The Jogger reporting milestone is complete. The next package is a planning review for the next source-backed model-expansion milestone; it must not combine existing model denominators or introduce a new architecture without explicit evidence.
