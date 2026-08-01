# Existing Configuration Missing-Data Analysis

## Summary

- Active configurations: 81
- Completeness scopes: 23
- Scoped configurations: 88
- Missing technical slots: 125
- Missing equipment slots: 44
- Explicitly classified not applicable: 0
- Candidates excluded from selection after an exhausted-source review: 3
- Eligible candidates: 6

## Ranked source-backed candidates

1. `sandero` / `src_pl_sandero_official_web_configurations_20260723` — technical 48, equipment 32, weighted impact 176 — excluded from selection by `sandero_official_web_source_gap_review.json`.
2. `sandero` / `src_pl_sandero_stepway_extreme_ecog120_mt_20260626` — technical 18, equipment 2, weighted impact 56 — eligible.
3. `sandero` / `src_pl_sandero_stepway_expression_ecog120_at_20260626` — technical 16, equipment 4, weighted impact 52 — eligible.
4. `sandero` / `src_pl_sandero_stepway_extreme_ecog120_at_20260626` — technical 14, equipment 4, weighted impact 46 — eligible.
5. `sandero` / `src_pl_sandero_stepway_catalog_tce_slice_20260703` — technical 9, equipment 0, weighted impact 27 — eligible.
6. `sandero` / `src_pl_sandero_stepway_essential_ecog120_mt_20260626` — technical 8, equipment 0, weighted impact 24 — excluded from selection by `sandero_stepway_essential_source_gap_review.json`.
7. `sandero` / `src_pl_sandero_stepway_expression_ecog120_mt_20260626` — technical 8, equipment 0, weighted impact 24 — excluded from selection by `sandero_stepway_expression_source_gap_review.json`.
8. `sandero` / `src_pl_sandero_journey_ecog120_mt_20260626` — technical 2, equipment 2, weighted impact 8 — eligible.
9. `sandero` / `src_pl_sandero_expression_ecog120_mt_20260626` — technical 2, equipment 0, weighted impact 6 — eligible.

## Selection

Selected `sandero` with source `src_pl_sandero_stepway_extreme_ecog120_mt_20260626` as the highest-impact eligible follow-up. Candidates documented as `source_exhausted_not_stated` remain visible in the ranking but cannot be selected again. The next sprint must verify exact source rows before importing values and must not infer missing data.
