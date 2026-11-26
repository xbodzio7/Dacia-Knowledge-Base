# Verified PDF Candidate Coverage Reconciliation

Date: 2026-07-28  
Status: complete

## Purpose

This package reconciles only the ten technical-table and equipment-matrix groups selected by the completed Verified PDF Candidate Ledger Review. It compares candidate IDs with existing active source-backed records and classifies coverage without approving an import or changing canonical data.

## Scope

| Measure | Result |
| --- | ---: |
| Review groups | 10 |
| Candidate IDs | 1,583 |
| Technical-table candidates | 541 |
| Equipment-matrix candidates | 1,042 |
| Already covered | 122 |
| Ambiguous | 108 |
| Unresolved | 1,158 |
| Explicit non-import | 195 |

The other 2,673 candidates remain governed by their existing review decisions and are not reclassified by this package.

## Conservative evidence contract

Technical candidates are compared only with active scalar or closed-range records that:

- cite the same registered brochure source;
- cite the same PDF page in `notes`;
- contain the candidate's ordered meaningful text tokens.

Equipment candidates are compared only with active availability records that:

- belong to the same model family;
- contain the candidate's ordered meaningful text tokens.

At least two meaningful tokens are required. Numbers, source boilerplate and common unit tokens do not create a match by themselves.

## Status meanings

- `already_covered` — all conservative matches resolve to one existing semantic evidence signature; multiple configuration records may share it.
- `ambiguous` — conservative matches resolve to more than one value, range or availability signature; the extracted line does not safely preserve enough column context to choose one.
- `unresolved` — no conservative exact-evidence match exists. This is not `not_stated`, `not_available` or another negative fact.
- `explicit_non_import` — headings, version-column labels, calls to action and numbered footnotes are structural source content rather than vehicle observations.

Each covered or ambiguous assignment stores the matching table, record code, configuration, source, page and semantic signature. Candidate IDs and exact text remain unchanged.

## Delivered command

```bash
python tools/dkb.py pdf-candidate-coverage-reconciliation
python tools/dkb.py pdf-candidate-coverage-reconciliation --verify
```

## Artifacts

- `data/reporting/verified_pdf_candidate_coverage_reconciliation.json` — deterministic candidate assignments and evidence signatures;
- `data/reporting/verified_pdf_candidate_coverage_reconciliation.md` — deterministic coverage summary.

## Safety boundary

This package:

- changes no file under `data/master`;
- creates no file under `data/imports`;
- does not infer missing configurations, attributes, units or table columns;
- performs no automatic candidate promotion;
- preserves ambiguous and unresolved evidence for authored follow-up.

## Next package

**Verified PDF Candidate Residual Gap Prioritization** will partition unresolved and ambiguous candidate IDs into small source- and page-bounded review packages, without creating imports.
