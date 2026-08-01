# Interface and Source Coverage Repair

**Status:** complete  
**Date:** 2026-08-01

## Delivered

- Registered an official current Spring model image for the interactive browser.
- Made the selection panel non-sticky while comparison is open, so it cannot cover the comparison headers.
- Kept the model headers sticky inside the comparison table's own scroll viewport.
- Made every parameter group collapsible, added global show/hide controls and remembered the state for the current browser session.
- Retained Sandero TCe 100 `direct_injection`; the exact registered Polish MY26 source dated 2026-07-03 states direct injection for this powertrain.
- Added 19 exact Sandero and Sandero Stepway option/package price mappings from the same official price matrix.
- Replaced the ambiguous generic missing label with separate states for an absent database record, a missing commercial mapping and a price not stated by the source.
- Added source-code and observation-date provenance to comparison cells.

## Evidence boundary

No value, availability state or price is projected across models, grades, powertrains, transmissions or sources. Blank source prices remain blank rather than being converted into zero or an estimate.

## Remaining work

The next bounded package audits every remaining active comparison and optional-price gap against the registered exact sources and classifies it as importable, source-not-stated, source-conflict or context-unmodeled.
