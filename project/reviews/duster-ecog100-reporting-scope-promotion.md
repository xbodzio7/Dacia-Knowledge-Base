# Duster Eco-G 100 Reporting Scope Promotion

## Selection

The portfolio review selected the current Eco-G 100 4x2 manual powertrain as
the second explicit Duster reporting subset. Essential, expression, extreme and
journey share one source-backed technical denominator while retaining meaningful
price and equipment differences.

The group ties for the widest remaining portfolio and has the richest technical
denominator: 21 attribute/context slots per configuration, including separate
petrol and LPG observations for top speed, acceleration, standing kilometre,
fuel-tank capacity, CO2 emissions and combined fuel consumption.

## Explicit scope

`data/reporting/duster_ecog100_completeness.json` selects exactly four active
configurations and one registered source. Its denominator contains 21 technical
attribute/context slots, 58 equipment attributes and one dated gross catalogue
price per configuration.

The companion evidence specification contains no decisions because the promoted
scope has no technical or equipment gaps. Empty evidence is therefore a checked
result rather than a substitute for missing data.

## Verified result

- 4 reporting configurations,
- 84/84 technical observations,
- 232/232 equipment observations,
- 4/4 dated catalogue prices,
- complete source registration, area, section and record coverage,
- 6 deterministic trim-pair comparisons,
- 126 equal technical comparisons,
- 81 equipment differences,
- 6 price differences,
- 87 total differences,
- zero not-comparable states.

## Artifact contract

Quality publishes separate completeness, source-coverage and comparison JSON
and Markdown files plus a flat comparison-differences CSV under the
`duster-ecog100` prefix. All seven files are included in the existing Quality
artifact manifest.

Existing Sandero artifact names, the default seven-configuration denominator,
21 Sandero pairs and 305 Sandero differences remain unchanged. The Eco-G 120
scope also remains an independent four-configuration portfolio with its own
artifact namespace and 17-slot technical denominator.

## Boundary

This package does not combine Eco-G 100 and Eco-G 120 into one technical
reporting denominator and does not claim a common slot set for the remaining
mild-hybrid or full-hybrid groups. Cross-powertrain comparison remains outside
scope. The next package resumes the portfolio review with five homogeneous
Duster powertrain groups.
