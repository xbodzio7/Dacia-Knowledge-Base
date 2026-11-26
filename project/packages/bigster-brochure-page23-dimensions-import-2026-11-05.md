# Bigster Brochure Page 23 — Historical Dimensions Import

## Goal

Materialize the source-backed exterior dimensions from printed page 23 of the official Polish Bigster brochure dated 2025-12-10, without replacing later dated price-list observations.

## Source and scope

- Source: `src_pl_bigster_brochure_20251210`
- PDF: `PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf`
- SHA-256: `76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74`
- Printed page: 23 (PDF page index 22)
- Exact target scope: 14 active configurations linked to this brochure by `brochure_technical_data_for`.

The rendered diagram shows a general Bigster exterior-dimension view. Seven dimensions have one printed value without a trim or powertrain split. The only paired exterior values are ground clearance and overall height; their explicit footnote `* 4×2/4×4` maps the first value to 4×2 and the second to 4×4.

## Imported observations

Added 126 dated scalar observations across nine existing integer/mm attributes and 14 exact configurations:

| Attribute | Brochure value |
|---|---:|
| Overall width, excluding mirrors | 1813 mm |
| Overall width, including mirrors | 2069 mm |
| Front track | 1580 mm |
| Rear track | 1565 mm |
| Wheelbase | 2702 mm |
| Front overhang | 854 mm |
| Rear overhang | 1014 mm |
| Ground clearance | 220 mm (4×2) / 219 mm (4×4) |
| Overall height | 1712 mm (4×2) / 1706 mm (4×4) |

Nine declarative import specifications preserve the attribute contracts and source page. IDs: 8290–8415. The already imported 14 overall-length observations are reused; they are not duplicated.

## Reconciliation and exclusions

- The brochure's historical values remain dated 2025-12-10.
- Later 2026-07-03 and 2026-10-01 price-list observations remain separate; differences such as width (1813 vs 1812 mm), front/rear track and rear overhang are not averaged or overwritten.
- Cargo values 667/702 and 1937/2002 are excluded because page 23 does not establish the exact powertrain/configuration and full measurement context.
- Interior dimensions 1443/1432 and seatback angles 14° are not exterior vehicle dimensions and are not mapped to those attributes.
- No new attribute definitions or source relationships are created.

## Acceptance

- 9 specifications and 126 exact observations.
- All 14 target configurations are active and linked to the brochure.
- The paired 4×2/4×4 values follow the explicit page-23 footnote.
- The focused test verifies the PDF hash, import specifications, IDs, exact values, source links and preservation of later dated values.
- Full Quality must pass on the final pull-request head before merge.
