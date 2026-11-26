# Source-Backed Model Expansion Planning Review

## Decision status

`COMPLETE`

All 53 active configurations are present in at least one reporting specification. Duster and Jogger already use independent homogeneous powertrain/transmission scopes. Sandero remains the only model whose seven configurations are grouped in the historical mixed `configuration_completeness.json` scope.

## Existing source boundary

The repository contains seven active Polish Sandero configuration PDFs dated 2026-06-26. Each configuration is linked to its own registered source, dated price, technical observations and equipment observations. No new source or reporting architecture is required.

The historical Sandero scope contains 45 technical slots and 69 equipment attributes across five Eco-G 120 manual configurations and two Eco-G 120 automatic Stepway configurations. Splitting that scope by transmission preserves the existing denominator and evidence decisions while removing cross-transmission comparisons.

## Candidate inventory

| Candidate | Configurations | Sources | Technical denominator | Present technical | Equipment denominator | Recorded equipment | Prices | Pairs | Evidence decisions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sandero Eco-G 120 manual | 5 | 5 | 225 | 221 | 345 | 298 | 5 | 10 | 51 |
| Sandero Stepway Eco-G 120 automatic | 2 | 2 | 90 | 89 | 138 | 121 | 2 | 1 | 18 |

The manual group has 98.22% technical record coverage and 86.38% equipment record coverage. Its 51 verified evidence decisions classify 34 gaps as `not_stated` and 17 as `out_of_scope`.

The automatic group has 98.89% technical record coverage and 87.68% equipment record coverage. Its 18 verified evidence decisions classify 10 gaps as `not_stated` and eight as `out_of_scope`.

## Comparison feasibility

Both filtered scopes are accepted by the current completeness, source-coverage and comparison tools when the corresponding subset of `configuration_gap_evidence.json` is retained.

The manual scope produces ten `different_version_same_transmission` pairs:

- 450 technical comparisons: 318 equal, 122 different and 10 not comparable;
- 690 equipment comparisons: 528 equal, 14 different and 148 not comparable;
- ten price comparisons: all different;
- 146 total differences.

The automatic scope produces one `different_version_same_transmission` pair:

- 45 technical comparisons: 37 equal, seven different and one not comparable;
- 69 equipment comparisons: 55 equal, one different and 13 not comparable;
- one price comparison: different;
- nine total differences.

No Sandero technical value is stored as a range, so neither candidate introduces interval comparisons.

## Decision

Promote **Sandero Eco-G 120 Manual Reporting Scope** first because it has the wider source-backed denominator: five configurations, five sources, 225 technical observations, 345 equipment observations, five prices and ten deterministic comparisons.

Promote **Sandero Stepway Eco-G 120 Automatic Reporting Scope** second. It is a separate two-configuration transmission group and must not be merged into the manual comparison denominator.

## Evidence policy

The implementation packages must preserve the filtered verified evidence decisions. Missing records must remain explicit `not_stated` or `out_of_scope` comparison states; they must not be converted to inferred values, `not_available`, or removed from the denominator.

## Next package

**Sandero Eco-G 120 Manual Reporting Scope Promotion** is the active implementation package. **Sandero Stepway Eco-G 120 Automatic Reporting Scope Promotion** follows directly.
