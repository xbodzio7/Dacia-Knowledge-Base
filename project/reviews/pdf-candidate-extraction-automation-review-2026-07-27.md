# PDF Candidate Extraction Automation Review

Date: 2026-07-27  
Status: complete

## Purpose

This review selects the first automation architecture for extracting reviewable candidates from the five registered official Dacia brochures. It does not implement extraction, import data, create canonical attributes or generate approved import specifications.

The repository already has three important pieces:

1. source receipts with local paths, byte sizes, page counts and SHA-256 values;
2. deterministic page extraction through `pdftotext` and optional Python PDF readers;
3. strict declarative importers that require an explicit configuration, attribute, source page, section and exact source text.

The missing layer is a durable candidate-only artifact between PDF text extraction and semantic approval.

## Verified input

The reviewed receipt is `project/sources/official-dacia-brochures-20260725.json`.

| Measure | Verified value |
| --- | ---: |
| Registered brochures | 5 |
| Declared pages | 114 |
| Declared bytes | 40,608,101 |
| Sources with SHA-256 | 5 |
| Model families | 5 |

The source set covers Bigster, Duster, Jogger, Sandero and Sandero Stepway.

## Existing repository capabilities

`tools/import_configuration_values.py` already exposes `extract_page_candidates`. It can extract one page through:

- `pdftotext -raw`;
- `pdftotext -layout`;
- default `pdftotext`;
- `pypdf` or `PyPDF2` when installed.

`tools/configuration_gap_source_review.py` already evaluates page variants using recovered source-text anchors and prefers layout-preserving output. Approved configuration-value imports independently verify the registered file SHA-256 and require the declared section and exact source text to be found on the source page.

The current brochure gap review imported zero observations and explicitly preserves contextual boundaries such as fuel, gear, seat state, drive type, measurement standard and cargo-compartment state.

## Compared architectures

### 1. Verified PDF Page Candidate Ledger — selected, 98/100

The pipeline verifies the receipt, extracts every declared page, segments deterministic text spans and writes a canonical candidate ledger. Every candidate has stable source, page, backend, line-span and text identity. The artifact remains semantically unapproved.

This is the only option that combines reusable coverage with a hard boundary against automatic import.

### 2. Gap-scoped Candidate Probe — 94/100

This would process only pages and phrases already named by current gap reports. It is efficient and safe, but it would encode the current review queue into the extraction engine and would not become a general receipt-level foundation.

### 3. Raw Page Text Archive — 85/100

This would preserve extracted text safely, but it would not provide stable candidate identifiers, spans, kinds or a review queue. Every later package would need to invent its own candidate boundaries.

### 4. Direct Import-spec Synthesis — rejected, 65/100

This would incorrectly combine extraction with semantic approval. Brochure text often lacks exact configuration scope or requires context not represented by a simple scalar row. Direct generation could silently project model-level wording into configurations or flatten fuel, gear, seat and cargo contexts.

### 5. OCR-first Multimodal Pipeline — deferred, 49/100

OCR and visual interpretation may later help image-only pages and diagrams, but they introduce a new dependency and weaker determinism. They are not needed for the first text-backed foundation.

## Selected architecture

### Stage 1 — receipt verification

The implementation must read the versioned receipt, sort sources by `source_code` and verify before extraction:

- local file existence;
- exact byte size;
- SHA-256;
- declared page count.

Any difference is a controlled failure. Extraction must never continue with a changed source under the old identity.

### Stage 2 — canonical page extraction

Every declared page of every registered source is processed.

Canonical backend order:

1. `pdftotext-layout`;
2. `pdftotext-default`;
3. `pdftotext-raw`.

`pypdf` and `PyPDF2` may be recorded as diagnostic variants, but their installation or absence must not alter canonical candidate identifiers or canonical output.

Output uses UTF-8 and LF line endings. Exact extracted text is retained; normalized text is stored separately. Empty or unreadable text is not interpreted as `not_stated`.

### Stage 3 — deterministic candidate spans

Candidates are stable text spans rather than approved observations. A candidate identifier is the SHA-256 of:

- source SHA-256;
- page;
- extraction rule code;
- first and last source line;
- normalized candidate text.

Canonical ordering is source, page, line range, rule and candidate ID.

Initial candidate kinds are deliberately descriptive rather than semantic approvals:

- heading;
- table row;
- scalar text;
- range text;
- availability text;
- unclassified text.

### Stage 4 — candidate ledger

Each candidate must include:

- candidate ID;
- source code, file path and SHA-256;
- document date and model code;
- page;
- backend and backend version;
- rule code;
- line range;
- exact and normalized text;
- candidate kind;
- review status.

The initial review statuses are:

- `unreviewed_candidate`;
- `requires_visual_review`;
- `ambiguous_source_evidence`;
- `explicit_non_import`.

A missing text layer, diagram or image-only region must be routed to `requires_visual_review`, never converted into negative evidence.

### Stage 5 — separate review and promotion

The candidate ledger is not an import specification. Extraction must not infer or approve:

- `configuration_code`;
- canonical `attribute_code`;
- canonical units;
- source applicability to a specific gearbox, fuel, drive type or seat layout.

A later, separately authored review decision must cite `candidate_id` and exact source text. Only another controlled package may transform an approved decision into a strict import specification.

## Determinism contract

The implementation must guarantee:

- byte-identical repeated JSON and Markdown output for the same sources and backend version;
- source hash verification before any extraction;
- stable source, page and candidate ordering;
- stable candidate IDs;
- no timestamps in generated artifacts;
- no environment-specific absolute paths;
- UTF-8 with LF line endings;
- optional Python PDF readers do not change canonical output.

## Explicit boundaries

The first implementation must make no changes to `data/master` and create no files under `data/imports`.

It does not implement:

- OCR;
- visual diagram interpretation;
- canonical attribute creation;
- configuration projection;
- automatic approval;
- resolution of ambiguous evidence.

## Decision

The selected next package is **Verified PDF Candidate Ledger Foundation**.

It will implement a `pdf-candidate-ledger` command and deterministic JSON and Markdown artifacts for the five registered brochures and all 114 declared pages. The delivery will remain candidate-only and will produce zero master-data rows and zero approved import specifications.
