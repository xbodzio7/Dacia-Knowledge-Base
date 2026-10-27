# Configuration Discovery and Shortlist Planning Review

## Decision status

`SELECTED — CONFIGURATION SHORTLIST CLI`

The next user-facing package will be a deterministic `configuration-shortlist` command. It will search the completed 53-configuration portfolio using stable configuration metadata, current catalogue prices and evidence-aware equipment availability without changing the master-data model.

## Portfolio audit

The active portfolio contains:

- 53 configurations across four model codes: 24 Duster III, 22 Jogger, five Sandero Stepway III and two Sandero III;
- 34 manual and 19 automatic configurations;
- ten source-backed powertrain labels;
- 53 current Polish catalogue gross prices, ranging from 68,000 PLN to 123,600 PLN;
- price observations dated 2026-02-06, 2026-04-01 or 2026-06-26;
- 29 recorded seat-count values: 18 five-seat and 11 seven-seat configurations;
- 24 configurations without a recorded `number_of_seats` value.

Model, version, powertrain, transmission and current catalogue price criteria have complete 53/53 coverage. Seat count is useful but partial and therefore requires an explicit unknown count in every filtered result.

## Equipment audit

The current availability dataset contains 77 equipment attributes with at least one record:

- 30 attributes have a recorded state for all 53 configurations;
- 47 attributes have partial cross-model coverage;
- 27 attributes discriminate between available (`standard` or `optional`) and `not_available` configurations.

Examples with full coverage and useful variation include `heated_steering_wheel`, `keyless_entry`, `rear_windows_power` and `side_mirrors_electric_adjustment`. Other useful criteria such as `automatic_climate_control`, `heated_front_seats`, `navigation_system` and `rear_view_camera` have partial coverage and must retain missing-statement semantics.

## Selected command contract

The first implementation will provide:

- repeatable exact model and version filters;
- repeatable exact transmission filters;
- case-insensitive powertrain-label matching;
- minimum and maximum current catalogue price filters in PLN;
- an optional exact seat-count filter;
- repeatable `required equipment` filters accepting `standard` or `optional`;
- repeatable `required standard equipment` filters accepting only `standard`;
- deterministic ordering by price, model, version and configuration code;
- JSON, Markdown and CSV outputs suitable for automation and spreadsheet use;
- a concise terminal summary.

## Evidence semantics

The shortlist must not turn missing source statements into inferred values:

- a missing price excludes the configuration from price-constrained results and is counted;
- a missing seat count excludes the configuration from a seat-constrained result and is counted;
- a missing equipment statement does not satisfy either equipment requirement and is counted separately from `not_available`;
- `optional` satisfies a general required-equipment filter but not a required-standard-equipment filter;
- all matched equipment states, source codes and observation dates remain available in structured output.

## Scope boundary

The package will not introduce preference scoring, financing assumptions, inferred total-cost calculations, fuzzy equipment synonym resolution or cross-market currency conversion. Those features require separate product decisions. The first command is a transparent filter and shortlist generator over existing verified records.

## Implementation target

The next package is **Configuration Shortlist CLI**, with seven or more regression tests, unified CLI integration, documentation and canonical project-state synchronization.
