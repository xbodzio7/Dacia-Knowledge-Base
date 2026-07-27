# Post-Cross-Model Workspace Priority Selection Review

Date: 2026-07-27

Status: complete

## Purpose

This review selects the next highest-value package after the public `data-products-v1.8.1` release, the cross-model navigation review and the verified local workspace entry point. It does not modify source data, schema, release assets or comparison semantics.

## Completed delivery baseline

The repository now has a complete consumer path:

- public immutable release `data-products-v1.8.1`;
- 85 verified archive members;
- 72 active configurations across five model families;
- 19 independent comparison scopes;
- 114 pairs generated only inside those scopes;
- 1,695 recorded differences;
- a local offline index with five primary cards and 84 safe local links;
- byte-identical generated `index.html` on Linux and Windows.

The previously selected release and cross-model usability work is therefore complete rather than merely planned.

## Selection method

Candidates use the stable weighted policy:

| Criterion | Weight |
| --- | ---: |
| Consumer value | 30% |
| Evidence readiness | 25% |
| Existing tooling reuse | 20% |
| Low implementation risk | 15% |
| Dependency clearance | 10% |

The selected package must advance the source-backed knowledge base without relying on ambiguous evidence, an unavailable exact source relationship or a destructive operation.

## Candidate ranking

| Rank | Candidate | Score | Status |
| ---: | --- | ---: | --- |
| 1 | PDF Candidate Extraction Automation Review | 81 | selected |
| 2 | Workflow Maintainability Review | 78 | follow-up |
| 3 | External Data Product Format Review | 76 | follow-up |
| 4 | Exact Configuration Expansion Review | 57 | blocked by evidence |
| 5 | Spring Source Foundation Review | 46 | blocked by source |

## Selected package

`PDF Candidate Extraction Automation Review`

The repository is ready for this review because it already contains:

- five registered official Polish brochures for Bigster, Jogger, Sandero, Sandero Stepway and Duster;
- 114 pages and 40,608,101 bytes of pinned local PDF evidence;
- a source receipt with exact document dates, local paths, page counts and SHA-256 values;
- `pdftotext` installed in the full quality job;
- page-aware `configuration-gap-source-review` tooling;
- declarative scalar and range importers;
- mature rules for duplicate evidence, missing statements, context-dependent values, visual diagrams, explicit non-imports and ambiguous source evidence.

What remains missing is a deterministic layer that produces reviewable extraction candidates without treating them as approved observations.

## Contract for the next review

The next package will compare candidate-only architectures, including:

1. deterministic page-text inventory;
2. rule-based scalar and range candidate extraction;
3. explicit table-region candidates;
4. a hybrid queue that keeps text pages separate from diagrams requiring visual review.

Every proposed candidate must retain source code, page, source SHA-256, a verbatim fragment, candidate kind and review status.

The review must preserve explicit statuses for:

- candidate only;
- duplicate existing evidence;
- missing exact configuration;
- missing context model;
- required visual review;
- ambiguous source evidence;
- explicit non-import.

## Non-goals

The selected review will not:

- implement OCR;
- change master data;
- create or approve import specifications;
- register new sources;
- add configurations;
- flatten fuel, gear, seat, measurement, drive or cargo context;
- infer facts from missing text;
- resolve the Jogger mass-table ambiguity or other blocked evidence.

## Deferred candidates

Workflow maintainability remains a useful follow-up, especially for reducing duplicated CI effort and improving diagnostics, but all fifteen standard workflows are currently green.

An external-format review remains valid, but users already have JSON, Markdown, CSV, HTML and XLSX plus a verified offline workspace.

Exact configuration expansion and Spring remain blocked until exact current sources and approved relationships exist.

## Decision

Proceed with `PDF Candidate Extraction Automation Review` as the next package. The review will choose the smallest deterministic and reversible candidate-only design. Implementation, imports and any architecture-changing work remain separate later packages.
