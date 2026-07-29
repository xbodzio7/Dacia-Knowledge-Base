# Duster Mini Technical Page 21 Unresolved Review — Chunk 1

Date: 2026-07-29  
Package: `residual_gap_018`  
Source: `src_pl_duster_mini_brochure_20251020`  
Page: 21  
Status: complete

## Scope

This package reviews the first 40 of 61 unresolved extraction candidates from the Duster mini-brochure page-21 technical table. The page has two powertrain columns: `hybrid-G 150 4×4*` and `hybrid 155`.

The review preserves:

- all 40 exact candidate IDs, texts and line ranges;
- zero attached evidence signatures and zero attached evidence records;
- visual grouping of wrapped labels and values;
- separate combustion and electric power/torque wording;
- 48 V versus 260 V traction-battery data;
- 4×4 with a rear electric motor versus 4×2;
- dual-clutch 6-speed versus Multi-mode 4+2 gearbox wording;
- front and rear brake distinctions;
- both printed tyre sizes and seasonal types;
- country-dependent Hybrid-G CO₂ and fuel-consumption wording;
- mass-label fragments whose aligned values fall outside this chunk.

## Authored result

The 40 candidates are partitioned exactly once into 30 visual groups:

- 26 logical-row anchors remain `unresolved_signature_mismatch`;
- 14 headers, continuations and incomplete label fragments are `context_only_non_import`;
- no candidate receives selected evidence;
- no master-data or approved-import file changes.

The printed maximum-power row is preserved literally rather than normalized because its extracted wording and unit association are not sufficiently safe for an import decision.

The Hybrid-G CO₂ and combined-consumption cells remain `do określenia w zależności od kraju`. No numeric value is inferred from another source or another powertrain.

The fragments `do jazdy`, `Dopuszczalna masa całkowita (DMC) zespołu` and `pojazdów` remain context-only because the corresponding aligned label beginnings or numeric value lines are not candidates in this chunk.

## Artifacts

- `data/reporting/duster_mini_technical_page21_unresolved_review_chunk1.json`
- `data/reporting/duster_mini_technical_page21_unresolved_review_chunk1.md`

## Safety boundary

This review records source findings but does not approve an import. It does not create or modify records under `data/master` or `data/imports`, does not project values between configurations and does not replace missing extraction fragments with inferred facts.

## Next package

**Duster Mini Technical Page 21 Unresolved Review — Chunk 2** (`residual_gap_019`), covering the remaining 21 candidates.
