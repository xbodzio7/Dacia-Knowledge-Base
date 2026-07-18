# Duster Hybrid 140 Reporting Scope Promotion

## Selection

The portfolio review selected the current Hybrid 140 4x2 automatic group as the
third explicit Duster reporting subset. Expression, extreme, journey and
journey+ share one source-backed technical denominator and provide six
comparison pairs without mixing powertrains.

## Explicit scope

`data/reporting/duster_hybrid140_completeness.json` selects exactly four active
configurations and one registered source. Its denominator contains 15 technical
attribute/context slots, 58 equipment attributes and one dated gross catalogue
price per configuration.

The technical denominator keeps combustion-engine power, traction-motor power
and starter-generator power as separate canonical attributes. The companion
evidence specification contains no decisions because the promoted scope has no
technical or equipment gaps.

## Verified completeness contract

- 4 reporting configurations,
- 60/60 technical observations,
- 232/232 equipment observations,
- 4/4 dated catalogue prices,
- complete source registration, area, section and record coverage,
- 6 deterministic trim-pair comparisons,
- 90 equal technical comparisons,
- zero not-comparable technical states.

The generated comparison artifact is the source of truth for the exact
trim-equipment difference count. Prices are pairwise distinct in the selected
catalogue observations.

## Artifact contract

Quality publishes separate completeness, source-coverage and comparison JSON
and Markdown files plus a flat comparison-differences CSV under the
`duster-hybrid140` prefix. All seven files are included in the existing Quality
artifact manifest.

Existing Sandero, Eco-G 100 and Eco-G 120 artifact names and denominators remain
unchanged.

## Boundary

This package does not combine Hybrid 140 and Hybrid 155 into one denominator and
does not infer engine-torque observations that the Hybrid 140 source block does
not state. Cross-powertrain comparison remains outside scope. The next package
resumes the portfolio review with four homogeneous Duster powertrain groups.
