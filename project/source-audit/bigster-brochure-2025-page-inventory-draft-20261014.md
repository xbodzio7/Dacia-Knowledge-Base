# Bigster official brochure — page inventory (web-source pre-audit)

**Package:** `official_bigster_brochure_full_assimilation_20261014_001`  
**Status:** `source_page_inventory_draft` — not closed  
**Market:** Poland  
**Official URL:** https://cdn.group.renault.com/dac/pl/pdf/broszury/bigster-brochure.pdf.asset.pdf/cf001ec254.pdf  
**Observed document length:** 24 PDF pages  
**Source text review:** completed from the official PDF endpoint on 2026-10-14. Selected visual page renders were inspected for the colour page, accessories, technical table, both equipment-matrix pages, dimensions and legal page.  
**Identity boundary:** exact binary SHA-256 and byte-for-byte equivalence with the repository-registered PDF have not yet been verified. This draft is not evidence that the registered source hash is unchanged.

## Page-by-page inventory

| PDF page | Content | Classification / follow-up |
| ---: | --- | --- |
| 1 | Bigster cover; model identity. | Context only. |
| 2 | Marketing overview, electrified powertrains and prominent exterior/interior features. | Marketing claims; do not convert into configuration facts without bounded evidence. |
| 3 | Interactive contents. | Navigation only. |
| 4 | Exterior design, Starkle protection, panoramic roof and two-tone styling. | Descriptive; exact trim applicability belongs to matrix pages. |
| 5 | Interior layout, 10-inch cluster, 10.1-inch central screen, materials and finish. | Candidate facts; trim-specific applicability requires equipment matrix. |
| 6 | Hybrid-G 150 4×4 powertrain narrative; petrol/LPG, dual-clutch transmission and electric rear axle claims. | Narrative claims with powertrain boundary; compare to exact technical table. |
| 7 | Mild hybrid 140, mild hybrid-G 140 and full hybrid 155 overview; up-to-80% city EV driving / up-to-40% fuel saving claim. | Marketing claim; retain its stated comparison/context, do not treat as measured configuration value. |
| 8 | Five-seat cabin, storage, seat-folding layout, dual-zone climate, powered tailgate and up-to-702 L luggage claim. | Candidate capacity/feature facts; verify measurement basis and grade/powertrain applicability. |
| 9 | YouClip system, InNature Sleep Pack, roof storage and accessory descriptions. | Accessory-only; do not add as factory standard equipment. |
| 10 | Media Nav Live, 10-inch/10.1-inch screens, navigation/map updates, audio and My Dacia services. | Candidate features; exact grade availability from matrix. |
| 11 | Driver assistance descriptions including adaptive cruise, driver-attention monitoring, sign recognition, Multiview camera, lane support and blind-spot monitoring. | Descriptive; exact standard/optional status from matrix. |
| 12 | Business/TCO, fleet support and financing narrative. | Commercial context; no vehicle master observations. |
| 13 | Equipment section index: colours, accessories, technical data, equipment/options, dimensions and trim descriptions. | Navigation only. |
| 14 | Six exterior paint names and metallic/non-metallic/two-tone footnotes. | Colour-domain evidence; images alone do not prove trim availability. |
| 15 | Essential equipment description: wheels, exterior/interior, comfort, safety, optional spare wheel and paint. | Grade-bound candidate equipment; reconcile against dated price list and matrix. |
| 16 | Expression = Essential +; additional styling/interior/comfort equipment and optional Media Nav Live. | Grade-bound candidate equipment; preserve optional status. |
| 17 | Journey equipment, including higher-grade interior, multimedia, driver-assistance and option/package details. | Grade-bound candidate equipment; preserve powertrain-specific footnotes. |
| 18 | Extreme equipment, including panoramic roof, modular roof bars, Media Nav Live, wireless charging, hybrid-155 centre console, optional powered tailgate and packages. | Grade-bound candidate equipment; preserve powertrain and package boundaries. |
| 19 | Accessory catalogue: Aero Cargo Box, illuminated door sills, mats, portable rear armrest, seat-back organiser, YouClip accessories and roof box. | Accessory-only; no configuration equipment import. |
| 20 | Technical table for Mild Hybrid-G 140, Mild Hybrid 140, Hybrid-G 150 4×4 and Hybrid 155: engines, battery, performance, transmission, steering, brakes, tyres, consumption/emissions, masses, payload, towing and luggage. | Primary technical evidence. Extract exact column mapping and footnotes; do not flatten combined petrol/LPG values or alternate tyre/boot values. |
| 21 | Equipment matrix: exterior design, seats/interior, safety and driver assistance across Essential, Expression, Journey and Extreme. Legend distinguishes standard, optional and unavailable. | Primary trim-availability evidence. Preserve legend and all footnotes; check OCR against rendered cells. |
| 22 | Equipment matrix: controls, comfort, multimedia, online services and packages. | Primary trim-availability evidence. Preserve optional package state and Hybrid 155-specific console/ACC details. |
| 23 | Dimension drawings and luggage capacities: maximum 667 dm³ / 702 L with rear bench upright, and 1937 dm³ / 2002 L with rear bench folded, under stated conditions; dimensions include 4570 mm length and 2702 mm wheelbase. | Primary dimension/capacity evidence; retain VDA/litre distinction, wheel/drive footnotes and stated measurement conditions. |
| 24 | Legal/source disclaimer and publication credit dated 10.12.2025. | Source boundary: brochure says equipment/availability may vary by market and change; not a sales offer. |

## Initial evidence boundaries

1. The brochure identifies four technical powertrain columns: Mild Hybrid-G 140, Mild Hybrid 140, Hybrid-G 150 4×4, Hybrid 155. These must not be collapsed into fewer configurations or mapped by column order without checking the current configuration registry.
2. The technical table includes materially different traction-battery statements: 48 V / 0.84 kWh for the three mild-hybrid columns and 280 V / 1.4 kWh for Hybrid 155. Preserve source qualifiers and exact configuration mapping.
3. The equipment matrix uses explicit standard/optional/unavailable markers. Marketing-page presence does not override that matrix.
4. The luggage table differentiates dm³ (VDA) and litres and qualifies values by parcel shelf, double floor and spare-wheel state. Do not store a single unqualified luggage value.
5. Accessory pages are not factory equipment evidence.
6. The final disclaimer explicitly warns that market availability and specifications may change. This is a dated document, not timeless evidence.

## Remaining work before closure

- Verify the exact downloaded binary SHA-256 and compare with the registered source record; the endpoint filename token is not a SHA-256 substitute.
- Complete visual review of every page, especially table cells and footnotes.
- Compare each candidate fact against the official 2026-10-01 Bigster price list, source registry, existing import specs, master observations, availability records and attribute definitions.
- Record existing/duplicate, superseded, conflict, non-importable and exact-gap outcomes separately.
- Import only exact unsuperseded gaps with source pages, applicability and import/check tests.
- Update canonical state, reports and generated documentation only after the package gates pass.

## Completion statement

This is a preliminary inventory based on the currently linked official PDF's text and selected rendered pages. It does **not** claim complete rendered-page review, source-hash verification, source-to-master reconciliation, import completion or quality-gate success.
