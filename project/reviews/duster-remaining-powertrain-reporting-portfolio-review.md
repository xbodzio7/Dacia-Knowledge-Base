# Remaining Duster Powertrain Reporting Portfolio Review

## Decision status

`SELECTED`

The review selects the current Eco-G 100 4x2 manual group as the next explicit
Duster reporting subset.

## Evidence baseline

The registered Duster catalogue contains seven homogeneous powertrain groups.
Eco-G 120 has already been promoted as an independent four-configuration
reporting subset. The remaining portfolio contains 20 active configurations,
324 source-backed technical observations, 1,160 equipment-availability records
and 20 dated catalogue prices.

Every remaining configuration has exactly 58 imported equipment attributes and
one price observation from `src_pl_duster_price_my26_py25_20260206`. Technical
coverage is evaluated against the exact attribute and fuel-context slots stated
for each powertrain in `tools/duster_technical_specifications.py`; attributes not
stated by the source are not converted into artificial gaps.

## Portfolio review

| Powertrain group | Configurations | Technical slots per configuration | Technical observations | Equipment observations | Prices | Trim pairs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Eco-G 100 4x2 manual | 4 | 21 | 84 | 232 | 4 | 6 |
| mild hybrid 130 4x2 manual | 3 | 15 | 45 | 174 | 3 | 3 |
| hybrid 140 4x2 automatic | 4 | 15 | 60 | 232 | 4 | 6 |
| mild hybrid 130 4x4 manual | 3 | 15 | 45 | 174 | 3 | 3 |
| mild hybrid 140 4x2 manual | 3 | 14 | 42 | 174 | 3 | 3 |
| hybrid 155 4x2 automatic | 3 | 16 | 48 | 174 | 3 | 3 |

All six groups are source-complete within their own explicit denominators.
They must remain separate because the source does not state one common set of
technical fields for every powertrain. In particular, hybrid component powers,
fuel-specific observations and standing-kilometre observations occur only in
the groups for which the source states them.

## Selection

Eco-G 100 is selected before the other groups because it:

- ties for the widest remaining portfolio with four configurations and six
  deterministic trim pairs;
- has the largest technical denominator, with 21 slots per configuration;
- preserves six explicit petrol/LPG context pairs for speed, acceleration,
  standing kilometre, tank capacity, CO2 emissions and fuel consumption;
- uses the same `essential`, `expression`, `extreme` and `journey` trim set as
  the already promoted Eco-G 120 subset;
- has complete technical, equipment, price and source coverage without an
  evidence exception or a new architecture decision.

Hybrid 140 is also a complete four-configuration candidate, but its technical
denominator is smaller and its trim set replaces `essential` with
`journey_plus`. It remains the strongest candidate for a later promotion after
the Eco-G 100 package.

## Implementation contract

The next package will:

1. add `data/reporting/duster_ecog100_completeness.json` selecting exactly the
   four active Eco-G 100 4x2 manual configurations;
2. declare the 21 shared technical attribute/context slots and the existing 58
   Duster equipment attributes;
3. add an empty, validated gap-evidence specification because the selected
   denominator has no missing technical or equipment observations;
4. generate separate completeness, source-coverage and comparison JSON and
   Markdown artifacts plus a flat differences CSV under a `duster-ecog100`
   prefix;
5. include those seven files in the existing Quality artifact manifest;
6. preserve the default Sandero scope and every Eco-G 120 artifact and
   denominator unchanged.

Expected completeness is 84/84 technical observations, 232/232 equipment
observations, 4/4 prices, complete source evidence and six comparable trim
pairs with zero not-comparable states.

## Boundary

This decision does not combine Eco-G 100 and Eco-G 120 into one technical
reporting denominator and does not promote the five other groups. Cross-
powertrain comparison remains outside the package. After the Eco-G 100
promotion, the portfolio review resumes with five homogeneous groups.
