# Verified PDF Candidate Ledger Review

Date: 2026-07-28  
Status: complete

## Purpose

This package performs the separately authored review required by the Verified PDF Candidate Ledger Foundation. It partitions every candidate span into a source- and page-bounded evidence decision while preserving canonical candidate IDs and exact source text. It does not promote any candidate to master data or an approved import specification.

## Complete partition

The review covers the entire canonical ledger:

| Measure | Result |
| --- | ---: |
| Registered brochures | 5 |
| Declared pages | 114 |
| Candidate spans | 4,256 |
| Evidence decision groups | 30 |
| Exact-text anchors | 60 |
| Unassigned candidates | 0 |
| Duplicate assignments | 0 |

Each brochure is divided into six authored surfaces:

1. product narrative;
2. colours, grades and accessories;
3. technical tables;
4. equipment matrices;
5. dimensions and cargo;
6. legal and navigation footer.

Every source page belongs to exactly one group. Every ledger candidate belongs to the group covering its source and page and appears exactly once in the committed review artifact.

## Controlled decisions

| Decision | Groups | Candidates | Meaning |
| --- | ---: | ---: | --- |
| `descriptive_non_import` | 5 | 1,259 | retain broad narrative as candidate-only reference |
| `requires_entity_mapping` | 5 | 1,184 | require exact colour, trim, package or accessory identity and applicability |
| `requires_existing_evidence_reconciliation` | 10 | 1,583 | compare technical and equipment candidates with current exact records before any further decision |
| `requires_visual_semantic_review` | 5 | 147 | retain dimensions and cargo behind visual/contextual mapping boundaries |
| `explicit_non_import` | 5 | 83 | exclude publication credits, legal notices, navigation and calls to action |

The decision codes deliberately describe review state rather than import outcome. A technical or equipment candidate is not declared duplicate merely because it resembles existing data; the next reconciliation package must cite both the candidate ID and the current exact evidence.

## Exact-text anchors

Every group contains two anchor candidates copied from the canonical ledger. Each anchor records:

- `candidate_id`;
- PDF page;
- extracted line span;
- candidate kind;
- exact source text.

The verifier resolves every anchor back to the ledger and rejects changed text, an unknown candidate ID or an anchor outside its group.

## Deterministic artifacts

```bash
python tools/dkb.py pdf-candidate-ledger-review
python tools/dkb.py pdf-candidate-ledger-review --verify
```

The command writes:

- `data/reporting/verified_pdf_candidate_ledger_review.json`;
- `data/reporting/verified_pdf_candidate_ledger_review.md`.

Repeated generation from the same ledger is byte-identical. The JSON contains the complete candidate-ID membership of every group; Markdown provides the human-readable decisions and exact-text anchors.

## Safety boundaries

This review:

- changes no file under `data/master`;
- creates no approved specification under `data/imports`;
- infers no configuration, attribute, unit or diagram mapping;
- does not treat missing or blank text as negative evidence;
- does not automatically classify technical or equipment text as already covered;
- does not promote a review group or anchor into an import.

## Next package

**Verified PDF Candidate Coverage Reconciliation** will compare the 1,583 reviewed technical and equipment candidates with current exact source-backed values and availability records. It will classify candidate IDs as already covered, unresolved, ambiguous or explicit non-import, still without creating imports.
