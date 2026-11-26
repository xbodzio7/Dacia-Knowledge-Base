# Official Dacia PDF Candidate Ledger

Candidate-only extraction summary. This artifact does not approve imports, infer configurations or canonicalize attributes and units.

## Coverage

| Measure | Value |
| --- | ---: |
| Registered sources | 5 |
| Declared pages | 114 |
| Candidates | 4256 |
| Backend version | `pdftotext version 24.02.0` |

## Sources

| Source | Model | Pages | Candidates | Layout | Default | Raw | Visual review pages |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| src_pl_bigster_brochure_20251210 | bigster | 24 | 920 | 24 | 0 | 0 | — |
| src_pl_duster_mini_brochure_20251020 | duster_iii | 25 | 1047 | 25 | 0 | 0 | — |
| src_pl_jogger_brochure_20251217 | jogger | 23 | 817 | 23 | 0 | 0 | — |
| src_pl_sandero_brochure_20260202 | sandero_iii | 21 | 766 | 21 | 0 | 0 | — |
| src_pl_sandero_stepway_brochure_20260202 | sandero_stepway_iii | 21 | 706 | 21 | 0 | 0 | — |

## Candidate kinds

| Kind | Count |
| --- | ---: |
| `availability_text` | 89 |
| `heading` | 661 |
| `range_text` | 9 |
| `scalar_text` | 57 |
| `table_row` | 1451 |
| `unclassified_text` | 1989 |

## Review statuses

| Status | Count |
| --- | ---: |
| `ambiguous_source_evidence` | 0 |
| `explicit_non_import` | 0 |
| `requires_visual_review` | 0 |
| `unreviewed_candidate` | 4256 |

## Promotion boundary

A later, separately authored review decision must cite `candidate_id` and exact source text. Direct candidate-to-master import and direct generation of approved import specifications are forbidden.

Pages with no canonical text layer are classified as `requires_visual_review`; they are never interpreted as `not_stated` or other negative evidence.
