# Duster Mini Technical Page 20 Ambiguity Review

Date: 2026-07-28
Package: `residual_gap_003`
Source: `src_pl_duster_mini_brochure_20251020`, page 20

## Scope

The package reviews all five candidates classified as `ambiguous` in the
page-20 technical table. The source PDF, registry row, SHA-256, exact candidate
IDs, extracted text, line positions and all 26 attached signatures are checked
before authored decisions are produced.

No master-data row or approved import specification is created or changed.

## Result

- 3 candidates are covered by selected evidence;
- 2 candidates are partially covered;
- 9 evidence signatures and 34 exact records are selected;
- all five candidates retain an authored decision;
- all selected records retain source code and page 20.

The steering fragment selects only the common electric steering signature.
The split ready-to-drive mass label selects 1350 and 1376 kg. Payload pairs
`455/487` and `454/528` remain closed numeric intervals while the source order
and its `Maks./min.` wording are preserved without endpoint relabeling.

## Cargo boundary

The line-103 unit fragment completes the upright VDA row and selects only
`453`, `517` and `474` dm3. Values `430`, `349` and `1415` belong to the page-21
Hybrid 155 table and are not selected for this page-20 candidate.

The line-106 fragment selects the attached `1566` dm3 spare-wheel value.
Visible repair-kit values `1545` and `1609` are not copied from the adjacent
line-103 candidate; they remain explicit source facts in this review.

## Validation

- deterministic JSON and Markdown generation;
- deterministic `--verify` mode;
- source registry, archived file hash and page boundary checks;
- exact five-candidate partition and attached-signature validation;
- 26 focused tests;
- project-state and documentation synchronization;
- no changes under `data/master` or `data/imports`.

## Next package

**Sandero Technical Page 17 Ambiguity Review** — review five ambiguous
technical candidates against ten preserved evidence signatures without
creating master-data rows or approved imports.
