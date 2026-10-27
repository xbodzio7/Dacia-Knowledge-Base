# Duster Eco-G 120 Reporting Scope Promotion

## Selection

The reporting-readiness review selected the current Eco-G 120 4x2 manual
powertrain as the first promoted Duster reporting subset. It is the widest
current homogeneous group in the registered MY26/PY25 catalogue: essential,
expression, extreme and journey share the same source-backed technical
denominator while retaining meaningful price and equipment differences.

## Explicit scope

`data/reporting/duster_ecog120_completeness.json` selects exactly four active
configurations and one registered source. Its denominator contains 17
technical attribute/context slots, 58 equipment attributes and one dated
gross catalogue price per configuration.

The companion evidence specification contains no decisions because the
promoted scope has no technical or equipment gaps. Empty evidence is therefore
a checked result rather than a substitute for missing data.

## Verified result

- 4 reporting configurations,
- 68/68 technical observations,
- 232/232 equipment observations,
- 4/4 dated catalogue prices,
- complete source registration, area, section and record coverage,
- 6 deterministic trim-pair comparisons,
- 102 equal technical comparisons,
- 81 equipment differences,
- 6 price differences,
- 87 total differences,
- zero not-comparable states.

## Artifact contract

Quality publishes separate completeness, source-coverage and comparison JSON
and Markdown files plus a flat comparison-differences CSV. All seven files are
included in the existing Quality artifact manifest.

Existing Sandero artifact names, default specifications, seven-configuration
denominator, 21 pairs and 305 differences remain unchanged.

## Boundary

This package does not claim that one technical denominator is valid across all
Duster powertrains. The remaining Eco-G 100, mild-hybrid and full-hybrid groups
retain their own observed slot sets and require separate explicit promotion.
