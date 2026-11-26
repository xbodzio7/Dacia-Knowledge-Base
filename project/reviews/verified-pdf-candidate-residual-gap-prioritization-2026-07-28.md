# Verified PDF Candidate Residual Gap Prioritization

Date: 2026-07-28
Status: complete

## Purpose

This package converts the ambiguous and unresolved remainder of the verified PDF candidate coverage reconciliation into a deterministic authored-review queue. It changes ordering and package boundaries only; it does not reinterpret candidate text or approve any import.

## Scope

| Measure | Result |
| --- | ---: |
| Residual candidate IDs | 1,266 |
| Ambiguous | 108 |
| Unresolved | 1,158 |
| Source/domain/page/status boundary groups | 31 |
| Review packages | 52 |
| Maximum candidates per package | 40 |
| Duplicate assignments | 0 |
| Unassigned residual candidates | 0 |

The queue covers all five registered brochure sources represented by the reconciliation. The 122 `already_covered` and 195 `explicit_non_import` candidates remain governed by the completed reconciliation and are not added to this queue.

## Deterministic ordering

Packages are ordered by these explicit rules:

1. `ambiguous` before `unresolved`;
2. `technical_tables` before `equipment_matrix` within a status;
3. larger source/domain/page/status groups before smaller groups;
4. source code and page as deterministic tie-breakers;
5. groups larger than 40 candidates split by source line span and `candidate_id`.

Every package therefore has one source, one domain, one PDF page and one coverage status. Package order does not alter the semantics of the preserved reconciliation.

## Highest-priority package

`residual_gap_001` contains the 23 ambiguous technical candidates from page 20 of `src_pl_bigster_brochure_20251210`. Those candidates retain 190 evidence-signature references and 703 evidence-record references. The next package must make authored decisions against those exact references rather than infer table-column meaning.

## Delivered command

```bash
python tools/dkb.py pdf-candidate-residual-gap-prioritization
python tools/dkb.py pdf-candidate-residual-gap-prioritization --verify
```

## Artifacts

- `data/reporting/verified_pdf_candidate_residual_gap_prioritization.json` — all 52 ordered packages with full candidate identity, exact text and evidence provenance;
- `data/reporting/verified_pdf_candidate_residual_gap_prioritization.md` — deterministic queue summary.

## Safety boundary

This package:

- changes no file under `data/master`;
- creates no file under `data/imports`;
- performs no automatic promotion;
- does not convert `unresolved` into negative evidence;
- does not choose among ambiguous evidence signatures;
- requires later authored review to cite the candidate ID, exact source text, page and selected evidence.

## Next package

**Bigster Technical Page 20 Ambiguity Review** will review the 23 candidates in `residual_gap_001` without creating master-data rows or approved import specifications.
