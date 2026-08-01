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
- Added source-code and observation-date provenance to technical and equipment comparison cells.

## Evidence boundary

No value, availability state or price is projected across models, grades, powertrains, transmissions or sources. Blank source prices remain blank rather than being converted into zero or an estimate.

The existing exact-scope completeness analysis still contains 97 missing technical slots and 36 missing equipment slots. Its seven remaining source candidates are formally exhausted and its eligible-candidate count is zero. These counts do not prove that every registered document has been exhaustively mapped to every active comparison field; they only describe the currently declared exact-source scopes.

## Remaining work

The next bounded package, `registered_source_completeness_reconciliation_001`, audits every remaining active comparison and optional-price gap against all registered exact sources. Each gap will be classified as:

- importable from an exact source;
- not stated by the source;
- conflicting between sources;
- blocked by an unmodeled context.

The review will not add models or domains and will not infer values from sibling configurations.
