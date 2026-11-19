# Bigster MY26 2026-10-01 HDC Applicability Evidence Review

Report ID: bigster_my26_20261001_hdc_applicability_evidence_review_20261119_001
Generated: 2026-11-19T18:56:00Z
Analysed commit: c18f5e704a27edee2e55615fc7138e3e4038bcf3
Status: current
Scope: Bigster MY26 Polish cennik effective 2026-10-01, printed page 4; HDC applicability across the six exact source-linked configurations and comparison with the grade-level equipment matrix.

## Scope and provenance

- Official Polish Bigster MY26 cennik effective 2026-10-01, printed page 4.
- Source code: `src_pl_bigster_price_my26_20261001`.
- Archived source: `owner_supplied/2026-10-01/d477c604e8.pdf`.
- SHA-256: `0964b3a3311708698ef3cee6bd28244f76c1db36d0d9452e128e5113384dac97`.
- Six exact configurations and 94 equipment attributes per configuration were already reconciled; 93 attribute groups agree with the grade-level matrix.

## Source evidence

The printed HDC row reads:

> HDC - system kontroli zjazdu ze wzniesienia (wyłącznie dla wersji Extreme oraz 4x4)

The grade-level matrix displays:

| Grade | Essential | Expression | Extreme | Journey |
|---|---|---|---|---|
| HDC | not available | standard | standard | standard |

The qualifier does not define whether the conditions “Extreme” and “4x4” are conjunctive or independent. The matrix is grade-level, not powertrain-specific, so it cannot supply a complete truth table for the six exact configurations.

## Existing configuration-level observations

| Configuration | Existing status |
|---|---|
| Expression mild hybrid-G 140 4x2 automatic | not_available |
| Extreme mild hybrid-G 140 4x2 automatic | not_available |
| Journey mild hybrid-G 140 4x2 automatic | not_available |
| Expression tribrid 150 4x4 automatic | not_available |
| Extreme tribrid 150 4x4 automatic | standard |
| Journey tribrid 150 4x4 automatic | not_available |

These six values currently implement the strict “Extreme AND 4x4” interpretation. That interpretation is plausible but not proven by the printed cennik. A disjunctive interpretation would produce a different truth table; the grade-level matrix also conflicts with the restrictive qualifier.

Review disposition: complete evidence assessment; underlying HDC applicability remains unresolved and marked Do sprawdzenia.

## Decision

**No master-data change.** Preserve all six existing values and the exact source wording. Keep the HDC applicability finding explicitly marked **Do sprawdzenia**. Do not infer a Boolean operator, expand grade-level markers across powertrains, or change statuses based on an assumed meaning of “oraz”.

- Rows added/updated: 0
- Availability statuses changed: 0
- Import specification rows changed: 0
- Source binary changed: no

## Verification

The existing focused tests already enforce this evidence boundary:

- `test_hill_descent_control_qualifier_remains_explicitly_unresolved` checks the exact qualifier, grade matrix, six existing statuses, explicit deferral and zero status changes.
- `test_master_equipment_evidence_matches_all_564_source_spec_rows` checks the archived source SHA-256 and all 564 source-linked equipment observations.

The review is complete as an evidence assessment, while the HDC fact itself remains unresolved.
