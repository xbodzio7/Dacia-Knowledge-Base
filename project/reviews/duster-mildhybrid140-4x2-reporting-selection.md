# Duster Mild Hybrid 140 4x2 Reporting Selection

## Decision status

`SELECTED`

The final portfolio review selects the current mild hybrid 140 4x2 manual group
as the seventh and final homogeneous Duster reporting subset.

## Remaining portfolio

After six independent Duster promotions, only one source-complete homogeneous
powertrain group remains outside reporting scope:

| Powertrain group | Configurations | Technical slots per configuration | Technical observations | Equipment observations | Prices | Trim pairs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| mild hybrid 140 4x2 manual | 3 | 14 | 42 | 174 | 3 | 3 |

The group contains expression, extreme and journey. Every configuration has one
dated catalogue price and 58 imported equipment observations.

## Source boundary

The technical source block states 14 common slots: acceleration, braked trailer
weight, cargo volume, CO2 emissions, cylinder count, engine displacement,
engine power, engine torque, combined fuel consumption, fuel-tank capacity,
maximum-power speed, maximum-torque speed, top speed and total valve count.

It does not state a standing-kilometre observation for this group. That field is
therefore excluded from the denominator rather than converted into an artificial
gap. All three dated catalogue prices are pairwise distinct.

## Implementation contract

The next package will:

1. select exactly the three active mild hybrid 140 4x2 manual configurations;
2. declare the 14 source-stated technical slots;
3. reuse the existing 58 source-backed Duster equipment attributes;
4. add an empty validated gap-evidence specification;
5. publish completeness, source-coverage and comparison JSON/Markdown files
   plus a flat differences CSV under a `duster-mildhybrid140-4x2` prefix;
6. preserve every existing Sandero and Duster reporting scope and artifact.

Expected completeness is 42/42 technical observations, 174/174 equipment
observations, 3/3 prices, complete source evidence and three comparable trim
pairs with zero not-comparable technical states.

## Portfolio consequence

After this promotion, all seven homogeneous Duster powertrain groups and all 24
source-supported Duster configurations will belong to an explicit independent
reporting portfolio. The groups will remain separate because their source-stated
technical denominators are not identical. Cross-powertrain aggregation remains
outside scope and requires a separate future decision.
