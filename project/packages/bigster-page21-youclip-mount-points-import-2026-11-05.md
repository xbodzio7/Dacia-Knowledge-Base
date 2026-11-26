# Bigster Page 21 — YouClip Mount Points Import

## Goal

Capture the exact YouClip mounting-point count printed in the official Bigster brochure page 21 for every active configuration linked to that brochure.

## Source boundary

The equipment matrix has four grade columns and explicitly states 4 mounting points for Essential and 5 for Expression, Journey and Extreme. The brochure registry links 14 active configurations: 2 Essential and 4 for each other grade. No powertrain-specific exception is printed for this row.

## Implementation

- Add the canonical integer attribute `youclip_mount_points` in the existing Infotainment category.
- Import 14 scalar observations from source `src_pl_bigster_brochure_20251210`, PDF page 22 (printed page 21).
- Preserve the exact source date and source row in observation notes.
- Do not overwrite any existing observation or infer values for configurations not linked to the brochure.

## Acceptance

- All 14 target configurations are active and source-linked.
- Values are 4 for Essential and 5 for Expression, Journey and Extreme.
- Source PDF hash and exact text on PDF page 22 are verified by the focused test.
- Full Quality workflow passes.
