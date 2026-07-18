# Duster Hybrid 155 Reporting Selection

## Decision status

`SELECTED`

The review selects the current Hybrid 155 4x2 automatic group as the next
explicit Duster reporting subset.

## Remaining portfolio

After the independent Eco-G 120, Eco-G 100 and Hybrid 140 promotions, four
homogeneous powertrain groups remain outside Duster reporting scope:

| Powertrain group | Configurations | Technical slots per configuration | Technical observations | Equipment observations | Prices | Trim pairs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| mild hybrid 130 4x2 manual | 3 | 15 | 45 | 174 | 3 | 3 |
| mild hybrid 130 4x4 manual | 3 | 15 | 45 | 174 | 3 | 3 |
| mild hybrid 140 4x2 manual | 3 | 14 | 42 | 174 | 3 | 3 |
| hybrid 155 4x2 automatic | 3 | 16 | 48 | 174 | 3 | 3 |

All four groups are source-complete within their own explicit technical
denominators and have one dated catalogue price plus 58 equipment observations
per configuration.

## Selection rationale

Hybrid 155 is selected because it:

- has the largest remaining technical denominator, with 16 slots per
  configuration;
- covers expression, extreme and journey without mixing powertrains;
- preserves explicit combustion-engine torque and maximum-torque speed in
  addition to combustion-engine, traction-motor and starter-generator powers;
- has three pairwise distinct dated catalogue prices;
- has complete technical, equipment, price and source evidence without a gap
  decision or an architecture change.

The mild-hybrid groups remain valid later candidates. They have smaller
technical denominators and do not contain the separate traction-motor and HSG
power observations stated for Hybrid 155.

## Implementation contract

The next package will:

1. select exactly the three active Hybrid 155 4x2 automatic configurations;
2. declare these 16 technical slots: acceleration, braked trailer weight, cargo
   volume, CO2 emissions, cylinder count, engine displacement, combustion-engine
   power, combustion-engine torque, fuel consumption, fuel-tank capacity,
   maximum-power speed, maximum-torque speed, starter-generator power, top speed,
   total valve count and traction-motor power;
3. reuse the existing 58 source-backed Duster equipment attributes;
4. add an empty validated gap-evidence specification;
5. publish completeness, source-coverage and comparison JSON/Markdown files
   plus a flat differences CSV under a `duster-hybrid155` prefix;
6. preserve the Sandero, Eco-G 100, Eco-G 120 and Hybrid 140 scopes and artifacts
   unchanged.

Expected completeness is 48/48 technical observations, 174/174 equipment
observations, 3/3 prices, complete source evidence and three comparable trim
pairs with zero not-comparable technical states.

## Boundary

This decision does not combine Hybrid 155 with Hybrid 140 and does not promote
the three remaining mild-hybrid groups. Cross-powertrain comparison remains
outside scope. After the Hybrid 155 promotion, the portfolio review resumes with
three homogeneous Duster powertrain groups.
