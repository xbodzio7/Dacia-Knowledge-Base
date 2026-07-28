# Verified PDF Candidate Coverage Reconciliation

Candidate-level reconciliation against existing active source-backed records. Coverage is not import approval.

## Summary

| Measure | Value |
| --- | ---: |
| Reconciled review groups | 10 |
| Reconciled candidates | 1583 |
| Already covered | 122 |
| Ambiguous | 108 |
| Unresolved | 1158 |
| Explicit non-import | 195 |

## Domains

| Domain | Candidates | Covered | Ambiguous | Unresolved | Non-import |
| --- | ---: | ---: | ---: | ---: | ---: |
| `equipment_matrix` | 1042 | 70 | 54 | 835 | 83 |
| `technical_tables` | 541 | 52 | 54 | 323 | 112 |

## Groups

| Group | Source | Domain | Pages | Candidates | Covered | Ambiguous | Unresolved | Non-import |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `bigster_equipment_matrix` | `src_pl_bigster_brochure_20251210` | `equipment_matrix` | 21–22 | 209 | 4 | 8 | 176 | 21 |
| `bigster_technical_tables` | `src_pl_bigster_brochure_20251210` | `technical_tables` | 20 | 130 | 12 | 23 | 69 | 26 |
| `duster_equipment_matrix` | `src_pl_duster_mini_brochure_20251020` | `equipment_matrix` | 22–23 | 280 | 47 | 37 | 175 | 21 |
| `duster_technical_tables` | `src_pl_duster_mini_brochure_20251020` | `technical_tables` | 20–21 | 183 | 13 | 6 | 121 | 43 |
| `jogger_equipment_matrix` | `src_pl_jogger_brochure_20251217` | `equipment_matrix` | 20–21 | 197 | 3 | 6 | 175 | 13 |
| `jogger_technical_tables` | `src_pl_jogger_brochure_20251217` | `technical_tables` | 19 | 82 | 9 | 16 | 43 | 14 |
| `sandero_equipment_matrix` | `src_pl_sandero_brochure_20260202` | `equipment_matrix` | 18–19 | 164 | 7 | 2 | 142 | 13 |
| `sandero_stepway_equipment_matrix` | `src_pl_sandero_stepway_brochure_20260202` | `equipment_matrix` | 18–19 | 192 | 9 | 1 | 167 | 15 |
| `sandero_stepway_technical_tables` | `src_pl_sandero_stepway_brochure_20260202` | `technical_tables` | 17 | 74 | 6 | 4 | 49 | 15 |
| `sandero_technical_tables` | `src_pl_sandero_brochure_20260202` | `technical_tables` | 17 | 72 | 12 | 5 | 41 | 14 |

## Classification contract

- Technical candidates match only active exact records from the same registered source and PDF page.
- Equipment candidates match only active availability records for the same model family.
- Ordered text matching requires at least two meaningful tokens; one semantic signature is `already_covered`, several are `ambiguous`.
- No conservative match is `unresolved`; it is never interpreted as `not_stated` or another negative value.
- Structural headings, column labels and numbered footnotes are `explicit_non_import`.

## Safety boundary

This artifact changes no master data, creates no approved import specification and performs no automatic promotion. A later authored decision must cite the candidate ID, exact text and selected evidence signature.

Next package: **Verified PDF Candidate Residual Gap Prioritization**.
