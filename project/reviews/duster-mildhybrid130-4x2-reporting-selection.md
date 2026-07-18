# Duster Mild Hybrid 130 4x2 Reporting Selection

## Decision status

`SELECTED`

The review selects the current mild hybrid 130 4x2 manual group as the next
explicit Duster reporting subset.

## Remaining portfolio

After the independent Eco-G 120, Eco-G 100, Hybrid 140 and Hybrid 155
promotions, three homogeneous mild-hybrid groups remain outside Duster
reporting scope:

| Powertrain group | Configurations | Technical slots per configuration | Technical observations | Equipment observations | Prices | Trim pairs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| mild hybrid 130 4x2 manual | 3 | 15 | 45 | 174 | 3 | 3 |
| mild hybrid 130 4x4 manual | 3 | 15 | 45 | 174 | 3 | 3 |
| mild hybrid 140 4x2 manual | 3 | 14 | 42 | 174 | 3 | 3 |

All three groups are source-complete within their own explicit technical
denominators and have one dated catalogue price plus 58 equipment observations
per configuration.

## Selection rationale

Mild hybrid 130 4x2 is selected because it:

- ties for the largest remaining technical denominator, with 15 slots per
  configuration;
- covers expression, extreme and journey without mixing powertrains;
- includes explicit standing-kilometre performance in addition to acceleration,
  speed, engine power and torque observations;
- has three pairwise distinct dated catalogue prices;
- has complete technical, equipment, price and source evidence without a gap
  decision or an architecture change.

The 4x4 group has the same technical slot count but Extreme and Journey share
one catalogue price. Mild hybrid 140 remains complete but its source block does
not state a standing-kilometre observation and therefore has a 14-slot
technical denominator.

## Implementation contract

The next package will:

1. select exactly the three active mild hybrid 130 4x2 manual configurations;
2. declare these 15 technical slots: acceleration, braked trailer weight, cargo
   volume, CO2 emissions, cylinder count, engine displacement, engine power,
   engine torque, fuel consumption, fuel-tank capacity, maximum-power speed,
   maximum-torque speed, standing kilometre, top speed and total valve count;
3. reuse the existing 58 source-backed Duster equipment attributes;
4. add an empty validated gap-evidence specification;
5. publish completeness, source-coverage and comparison JSON/Markdown files
   plus a flat differences CSV under a `duster-mildhybrid130-4x2` prefix;
6. preserve every existing Sandero and Duster reporting scope and artifact.

Expected completeness is 45/45 technical observations, 174/174 equipment
observations, 3/3 prices, complete source evidence and three comparable trim
pairs with zero not-comparable technical states.

## Boundary

This decision does not combine the 4x2 and 4x4 groups and does not promote mild
hybrid 140. Cross-powertrain and cross-drivetrain comparison remains outside
scope. After this promotion, the portfolio review resumes with two homogeneous
Duster powertrain groups.
