# Duster Hybrid 140 Reporting Selection

## Decision status

`SELECTED`

The review selects the current Hybrid 140 4x2 automatic group as the next
explicit Duster reporting subset.

## Remaining portfolio

After the independent Eco-G 120 and Eco-G 100 promotions, five homogeneous
powertrain groups remain outside Duster reporting scope:

| Powertrain group | Configurations | Technical slots per configuration | Technical observations | Equipment observations | Prices | Trim pairs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| mild hybrid 130 4x2 manual | 3 | 15 | 45 | 174 | 3 | 3 |
| hybrid 140 4x2 automatic | 4 | 15 | 60 | 232 | 4 | 6 |
| mild hybrid 130 4x4 manual | 3 | 15 | 45 | 174 | 3 | 3 |
| mild hybrid 140 4x2 manual | 3 | 14 | 42 | 174 | 3 | 3 |
| hybrid 155 4x2 automatic | 3 | 16 | 48 | 174 | 3 | 3 |

All five groups are source-complete within their own explicit technical
mianowniki and have one dated catalogue price plus 58 equipment observations
per configuration.

## Selection rationale

Hybrid 140 is selected because it:

- is the only remaining four-configuration group and therefore supports six
  deterministic trim comparisons;
- covers expression, extreme, journey and journey+ without mixing powertrains;
- has a complete 15-slot technical denominator for every selected
  configuration;
- preserves the source distinction between combustion-engine power,
  traction-motor power and starter-generator power;
- has complete technical, equipment, price and source evidence without a gap
  decision or an architecture change.

The three-configuration groups remain valid later candidates, but each produces
only three trim pairs. Hybrid 155 has one additional technical slot because the
source states engine torque and torque speed for that group; that difference is
another reason not to combine the two full-hybrid families.

## Implementation contract

The next package will:

1. select exactly the four active Hybrid 140 4x2 automatic configurations;
2. declare these 15 technical slots: acceleration, braked trailer weight, cargo
   volume, CO2 emissions, cylinder count, engine displacement, combustion-engine
   power, fuel consumption, fuel-tank capacity, maximum-power speed, standing
   kilometre, starter-generator power, top speed, total valve count and
   traction-motor power;
3. reuse the existing 58 source-backed Duster equipment attributes;
4. add an empty validated gap-evidence specification;
5. publish completeness, source-coverage and comparison JSON/Markdown files
   plus a flat differences CSV under a `duster-hybrid140` prefix;
6. preserve the Sandero, Eco-G 100 and Eco-G 120 scopes and artifacts unchanged.

Expected completeness is 60/60 technical observations, 232/232 equipment
observations, 4/4 prices, complete source evidence and six comparable trim pairs
with zero not-comparable technical states.

## Boundary

This decision does not combine Hybrid 140 with Hybrid 155 and does not promote
the four other groups. Cross-powertrain comparison remains outside scope. After
the Hybrid 140 promotion, the portfolio review resumes with four homogeneous
Duster powertrain groups.
