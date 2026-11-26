# Duster Mild Hybrid 130 4x4 Reporting Selection

## Decision status

`SELECTED`

The review selects the current mild hybrid 130 4x4 manual group as the next
explicit Duster reporting subset.

## Remaining portfolio

After the independent Eco-G, full-hybrid and mild hybrid 130 4x2 promotions,
two homogeneous groups remain outside Duster reporting scope:

| Powertrain group | Configurations | Technical slots per configuration | Technical observations | Equipment observations | Prices | Trim pairs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| mild hybrid 130 4x4 manual | 3 | 15 | 45 | 174 | 3 | 3 |
| mild hybrid 140 4x2 manual | 3 | 14 | 42 | 174 | 3 | 3 |

Both groups are source-complete within their own explicit technical denominators
and have one dated catalogue price plus 58 equipment observations per
configuration.

## Selection rationale

Mild hybrid 130 4x4 is selected because it:

- has the larger remaining technical denominator, with 15 slots per
  configuration;
- covers expression, extreme and journey without mixing powertrains;
- preserves 4x4-specific acceleration, standing-kilometre, consumption,
  emissions and cargo-volume observations;
- has complete technical, equipment, price and source evidence without a gap
  decision or an architecture change.

Extreme and Journey share the same dated catalogue price. That equality is a
source-backed comparison result and will be preserved explicitly rather than
converted into a gap. Mild hybrid 140 remains complete but its source block does
not state a standing-kilometre observation and therefore has a 14-slot technical
denominator.

## Implementation contract

The next package will:

1. select exactly the three active mild hybrid 130 4x4 manual configurations;
2. declare these 15 technical slots: acceleration, braked trailer weight, cargo
   volume, CO2 emissions, cylinder count, engine displacement, engine power,
   engine torque, fuel consumption, fuel-tank capacity, maximum-power speed,
   maximum-torque speed, standing kilometre, top speed and total valve count;
3. reuse the existing 58 source-backed Duster equipment attributes;
4. add an empty validated gap-evidence specification;
5. publish completeness, source-coverage and comparison JSON/Markdown files
   plus a flat differences CSV under a `duster-mildhybrid130-4x4` prefix;
6. preserve every existing Sandero and Duster reporting scope and artifact.

Expected completeness is 45/45 technical observations, 174/174 equipment
observations, 3/3 prices, complete source evidence and three comparable trim
pairs with zero not-comparable technical states. The expected price summary is
two differences and one equality.

## Boundary

This decision does not combine the 4x2 and 4x4 groups and does not promote mild
hybrid 140. Cross-powertrain and cross-drivetrain comparison remains outside
scope. After this promotion, the portfolio review resumes with the final
homogeneous Duster powertrain group.
