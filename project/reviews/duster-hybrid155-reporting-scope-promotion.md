# Duster Hybrid 155 Reporting Scope Promotion

## Selection

The portfolio review selected the current Hybrid 155 4x2 automatic group as the
fourth explicit Duster reporting subset. Expression, extreme and journey share
one source-backed technical denominator and provide three comparison pairs
without mixing powertrains.

## Explicit scope

`data/reporting/duster_hybrid155_completeness.json` selects exactly three active
configurations and one registered source. Its denominator contains 16 technical
attribute/context slots, 58 equipment attributes and one dated gross catalogue
price per configuration.

The technical denominator keeps combustion-engine power and torque,
traction-motor power and starter-generator power as separate canonical
attributes. The companion evidence specification contains no decisions because
the promoted scope has no technical or equipment gaps.

## Verified result

- 3 reporting configurations,
- 48/48 technical observations,
- 174/174 equipment observations,
- 3/3 dated catalogue prices,
- complete source registration, area, section and record coverage,
- 3 deterministic trim-pair comparisons,
- 48 equal technical comparisons,
- 28 equipment differences and 146 equipment equalities,
- 3 price differences,
- 31 total differences,
- zero not-comparable states.

## Artifact contract

Quality publishes separate completeness, source-coverage and comparison JSON
and Markdown files plus a flat comparison-differences CSV under the
`duster-hybrid155` prefix. All seven files are included in the existing Quality
artifact manifest.

Existing Sandero, Eco-G 100, Eco-G 120 and Hybrid 140 artifact names and
denominators remain unchanged.

## Boundary

This package does not combine Hybrid 155 and Hybrid 140 into one denominator and
does not infer standing-kilometre observations that the Hybrid 155 source block
does not state. Cross-powertrain comparison remains outside scope. The next
package resumes the portfolio review with three homogeneous mild-hybrid Duster
powertrain groups.
