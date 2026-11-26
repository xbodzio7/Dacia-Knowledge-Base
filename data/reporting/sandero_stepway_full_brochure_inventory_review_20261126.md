# Sandero Stepway — full brochure inventory review

- **Source:** Dacia Poland, 2026-02-02, 21 pages
- **SHA-256:** `800e6e6df78e55e9fd3ac270dd5df26447c82830c92ced112ee83c3b44595d48`
- **Extraction:** GitHub Actions run [45892086102](https://github.com/xbodzio7/Dacia-Knowledge-Base/actions/runs/45892086102), Poppler 24.02.0
- **Artifact:** 21 extracted pages, 21 rendered images, 42,437 text characters, 706 candidates

## Inventory result

All 21 pages have non-empty extracted text and a rendered image. The candidate ledger contains 117 headings, 240 table rows, 6 scalar candidates, 1 range candidate, 10 availability candidates and 332 unclassified text candidates. All 706 candidates remain unreviewed in the mechanical ledger; this is intentional and does not imply that all are importable.

Pages 17–19 contain 266 candidates and are explicitly handled by existing Stepway technical/equipment reviews. The distinct new review surface is pages 1–16 and 20–21 (440 candidates). Existing reports and imports are reused, not repeated.

## Page-by-page disposition

| Page | Content | Disposition |
|---:|---|---|
| 1 | Cover | Visual/non-import |
| 2 | Positioning and headline highlights | Descriptive; cargo highlight already covered |
| 3 | Interactive menu | Navigation only |
| 4 | Styling, Starkle® | Descriptive; no inferred technical attributes |
| 5 | Engine narrative | Cross-reference page 17 |
| 6 | Comfort, e-shifter, displays | Descriptive; preserve Eco-G 120 auto footnote |
| 7 | Interior, seat folding, roof rails | Descriptive; verify applicability separately |
| 8 | YouClip | Distinguish standard mounts from accessories |
| 9 | Multimedia systems | Keep Media Control, Display and Nav Live distinct |
| 10 | Driver assistance | Descriptive; no inferred trim availability |
| 11 | Interactive equipment menu | Navigation only |
| 12 | Paint palette | Preserve seven colour names and footnotes; no surcharge inference |
| 13 | Essential equipment summary | Cross-reference matrix; roof-rail wording conflict recorded |
| 14 | Expression summary | Cross-reference pages 18–19 |
| 15 | Extreme summary | Cross-reference pages 18–19; preserve option/package distinction |
| 16 | Accessories | Descriptive; 310-litre cargo box and 80-kg roof-crossbar claims retained as source statements |
| 17 | Technical table | Reuse existing technical review and max-power RPM closure |
| 18 | Equipment matrix | Reuse existing ambiguity and unresolved chunks |
| 19 | Equipment matrix continuation | Reuse existing unresolved chunks |
| 20 | Dimensions and cargo | Cargo already imported; Stepway exterior dimensions require focused semantic crosswalk |
| 21 | Disclaimer | Legal/publication caveat, non-import |

## Findings requiring care

1. **Roof rails conflict (pages 13 and 18).** Page 13's Essential summary says “black modular roof rails”. The detailed page-18 matrix separates two rows: plain roof rails are standard only in Essential; modular grey Megalith roof rails are standard in Expression and Extreme. The detailed matrix preserves distinct row layout. The conflicting page-13 phrase is not silently normalized or imported.
2. **Cargo is already covered (page 20).** `sandero_stepway_brochure_cargo_import.json` records 45 cargo values/context rows across nine Sandero and Stepway configurations. No duplicate cargo import is authorized.
3. **Stepway exterior dimensions (page 20).** Visual reading identifies roof height with rails 1586 mm, body height 1535 mm, front track 1520 mm, body width 1853 mm, width with mirrors 2012 mm, rear track 1509 mm, front overhang 833 mm, wheelbase 2604 mm, rear overhang 665 mm, overall length 4102 mm and ground clearance 200 mm. These are candidates for a separate semantic crosswalk and duplicate check, not yet imported.
4. **Top-view values and angles (page 20).** Interior measurements (1408, 1406, 1026 mm) and 14° seatback angles are not treated as exterior dimensions or approach/departure angles.
5. **Paint palette (page 12).** The starred colours are marked unavailable in Essential. The brochure does not provide a commercial surcharge matrix; no price is inferred.
6. **Page 17 technical scope.** The existing max-power RPM closure covers ten Eco-G 120 fuel-specific ranges. It does not close all remaining technical gaps.

## Existing evidence reused

- `sandero_stepway_page17_max_power_rpm_import_closure_20261104.json`
- `sandero_stepway_technical_page17_ambiguity_review.json`
- `sandero_stepway_equipment_page18_ambiguity_review.json`
- `sandero_stepway_equipment_page18_unresolved_review_chunk1.json`
- `sandero_stepway_equipment_page18_unresolved_review_chunk2.json`
- `sandero_stepway_equipment_page18_unresolved_review_chunk3.json`
- `sandero_stepway_equipment_page19_unresolved_review_chunk1.json`
- `sandero_stepway_equipment_page19_unresolved_review_chunk2.json`
- `sandero_stepway_brochure_cargo_import.json`

## Result and next package

- 21/21 pages extracted and visually rendered.
- 706 mechanical candidates; 440 in the new page scope; 266 belong to already reviewed pages 17–19.
- No master-data changes, import specs or imports in this inventory package.
- Next: **Sandero Stepway Page 20 Exterior Dimension Semantic Crosswalk and Import**. Validate exact attribute semantics, source-linked configuration scope and duplicate keys before any append-only historical import.

The candidate ledger and rendered page images are reproducible from the archived PDF using `.github/workflows/sandero-stepway-brochure-inventory.yml`; the run artifact is retained temporarily by GitHub Actions.

## Report metadata

- Report ID: sandero_stepway_full_brochure_inventory_review_20261126
- Generated: 2026-11-26T21:12:00Z
- Analysed commit: c5cc38f5c1b244c646019eba6c510847c95ad9e4
- Status: current
- Scope: Full 21-page visual and text inventory of the official Polish Sandero Stepway brochure, with existing page 17-19 evidence and page-20 cargo import reused; no master-data import.
