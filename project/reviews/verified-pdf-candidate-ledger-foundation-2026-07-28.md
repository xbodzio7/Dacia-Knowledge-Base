# Verified PDF Candidate Ledger Foundation

Date: 2026-07-28  
Status: complete

## Purpose

This package implements the candidate-only layer selected by the PDF Candidate Extraction Automation Review. It turns the five pinned official brochure receipts into deterministic, reviewable text-span artifacts without approving any configuration, attribute, unit or import specification.

## Delivered command

```bash
python tools/dkb.py pdf-candidate-ledger
python tools/dkb.py pdf-candidate-ledger --verify
```

The command verifies each receipt entry before extraction:

- repository-relative file path;
- exact byte size;
- SHA-256;
- declared PDF page count.

Any integrity difference stops the command before candidate extraction.

## Canonical extraction

The command processes all 114 declared pages in stable `source_code` order. Canonical backend preference is:

1. `pdftotext-layout`;
2. `pdftotext-default`;
3. `pdftotext-raw`.

All three canonical outputs are produced once per document. The first non-empty page text in that order is selected. Optional Python PDF readers are not consulted by canonical generation and therefore cannot change candidate IDs or artifact bytes.

`backend_version` records the exact first-line version reported by the installed `pdftotext` executable. Verification therefore fails closed when the approved extraction backend changes, even if the source PDFs remain unchanged.

## Candidate span model

Every non-empty extracted line becomes one candidate with:

- source code, relative file path and source SHA-256;
- document date and model code;
- one-based PDF page and extracted line span;
- selected backend and extraction contract version;
- exact text and separately normalized text;
- deterministic surface rule and descriptive candidate kind;
- review status.

Candidate IDs are SHA-256 values over source SHA-256, page, rule code, line span and normalized text. Candidate ordering is source, page, line span, rule and candidate ID.

The initial surface kinds are deliberately non-approving:

- heading;
- table row;
- scalar text;
- range text;
- availability text;
- unclassified text.

A page with no canonical text layer receives one `empty_page_text` candidate with `requires_visual_review`; it is never translated to `not_stated` or other negative evidence.

## Materialized coverage

| Measure | Result |
| --- | ---: |
| Registered brochures | 5 |
| Declared pages | 114 |
| Candidate spans | 4,256 |
| Table rows | 1,451 |
| Headings | 661 |
| Availability text | 89 |
| Range text | 9 |
| Scalar text | 57 |
| Unclassified text | 1,989 |
| Pages requiring visual review | 0 |

The approved runner extracted all 114 pages with `pdftotext-layout` (`pdftotext version 24.02.0`); no fallback backend was selected.

## Artifacts

- `data/reporting/official_dacia_pdf_candidate_ledger.json` — canonical candidate ledger;
- `data/reporting/official_dacia_pdf_candidate_ledger.md` — deterministic extraction and review summary.

Repeated generation is byte-identical for the same sources and extraction contract. Both artifacts use UTF-8, LF line endings, stable ordering and no timestamps or absolute paths.

## Safety boundaries

This package:

- changes no file under `data/master`;
- creates no file under `data/imports`;
- performs no OCR or diagram interpretation;
- infers no configuration code;
- approves no canonical attribute or unit;
- performs no automatic promotion.

A later, separately authored review must cite `candidate_id` and exact source text before any controlled import package can be considered.

## Validation

The package adds tests for receipt ordering and integrity, page-count drift, candidate-ID stability, optional-backend independence, empty-page handling, byte-identical JSON and Markdown, initial surface rules, required fields and restricted output paths. The committed artifacts are regenerated from the five real PDFs during the Poppler-enabled quality job.

The next package is **Verified PDF Candidate Ledger Review**.
