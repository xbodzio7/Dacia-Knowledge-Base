# Spring complete-source evidence ledger

Audit scope: `src_pl_spring_brochure_20260219` and `src_pl_spring_price_my25_stock_20260708`.

Status vocabulary:

- `represented` — already represented in master with an accepted source/context;
- `candidate` — source-supported fact requiring a bounded comparison or migration;
- `conflict` — must not be imported without preserving the conflicting dated context;
- `deferred` — valid fact whose required configuration, measurement or accessory context is not yet safely modelled;
- `out_of_scope` — marketing, navigation or legal material that produces no master observation.

| Evidence area | Source pages | Key facts | Status | Boundary / next action |
| --- | --- | --- | --- | --- |
| Document identity | Brochure 1, 22; price list 1, 6 | Publication/effective dates, Polish market and legal limitations. | represented | Source registry already contains exact files, hashes and dates. |
| Stock prices | Price list 1 | Expression Electric 70: 81,500 PLN; Extreme Electric 100: 85,900 PLN; MY2025 dealer stock. | represented | Keep stock/MY2025 boundary; do not generalise to MY2026. |
| Charging cables | Brochure 13, 14, 15, 20; price list 2, 4 | Brochure: domestic standard, Type 2 optional. July matrix: domestic optional 1500, Type 2 standard. | conflict | Preserve all dated states; see conflict C-001/C-002. |
| DC charging | Brochure 2, 6, 14, 15, 20; price list 2, 4, 5 | DC 40 kW option/package states; 20–80% in 29 minutes. | candidate | Compare exact configuration availability and technical-time representation; keep package dependencies. |
| V2L | Brochure 6, 15, 20; price list 4 | Brochure Extreme standard narrative/matrix; July price list Extreme through Power package, Expression unavailable. | conflict | Treat as range/date evolution; no timeless availability record. |
| Multimedia | Brochure 5, 7, 13–15, 19–20; price list 4 | Media Control, Media Display/Nav Live, 10.1-inch screen, two USB-C, remote services and packages. | candidate | Compare current multimedia attributes and package memberships by grade/date. |
| Exterior colours | Brochure 12; price list 3 | Six named colours; metallic status; Lichen Khaki 2300 PLN in July stock list. | candidate | Colour names/domain may be represented; audit exact grade availability and dated prices separately. |
| Grade trims | Brochure 13–15, 19–20; price list 3–4 | Essential, Expression, Extreme equipment and trim differences. | candidate | Generate bounded equipment-delta comparisons rather than bulk importing prose. |
| Safety/ADAS | Brochure 9, 13, 16, 19; price list 4 | AEBS, LKA/LDW, driver attention, TSR/ISA, My Safety, airbags, eCall, ISOFIX and related systems. | candidate | Compare canonical equipment attributes; avoid duplicates caused by naming variants. |
| Parking | Brochure 13–15, 19–20; price list 3–4 | Rear sensors standard; camera and front-sensor states vary by grade/package. | candidate | Exact grade/package migration after current-master comparison. |
| Powertrain | Brochure 6, 19; price list 2, 5 | Electric 70/100; 52/75 kW; 137 Nm; permanent-magnet synchronous motor. | candidate | Verify exact MY/configuration applicability and current scalar observations. |
| Battery | Price list 2, 5; brochure 19 | 24.3 kWh LFP, 354 V, 204 kg. | candidate | Import only if missing and configuration context is explicit. |
| Charging times | Price list 5; brochure 6, 19 | 2.3 kW: 10h11; 3.7 kW: 6h47; 7.4 kW: 3h20; DC: 29 min. | candidate | Preserve start/end SOC and charger-power basis. |
| Range/energy | Brochure 2, 6, 19; price list 5–6 | 222/225 km variants, 225 mixed, 315 urban and energy-use values with footnotes. | deferred | Footnote/configuration mapping must be resolved before import. |
| Performance | Price list 5; brochure 19 | 0–100: 12.3/9.6 s; top-speed values; one-speed reduction. | candidate | Compare against exact saved MY26 observations; do not assume unchanged range. |
| Passenger dimensions | Brochure 21; price list 6 | 3701 length, 2423 wheelbase, widths/heights, clearance and related dimensions. | candidate | Preserve wheel-size/load basis and resolve differing clearance presentations. |
| Passenger luggage | Brochure 2, 8, 21; price list 6 | 308 L ISO 3832, 288 dm3 VDA, 1004 L folded. | candidate | Store measurement standard and seat-state explicitly. |
| Interior storage | Brochure 8 | 32.7 L cabin storage; optional 35 L under-bonnet accessory. | deferred | Separate intrinsic capacity from accessory capacity. |
| Cargo derivative | Brochure 10, 16, 21 | Two seats, 341 kg payload, 1085 L / 1170 mm cargo area. | deferred | Requires separate Cargo configuration; never populate passenger grades. |
| Accessories/YouClip | Brochure 8, 17–18 | Under-bonnet box, boot protection, mats and YouClip accessories. | deferred | Accessory catalogue domain; not factory-equipment availability. |
| Marketing/design | Brochure 1, 3–5, 11; price list 1–2 | Styling descriptions, navigation and promotional copy. | out_of_scope | Retained in page inventory; no master facts. |
| Legal disclaimers | Brochure 22; price list 1, 6 | Specifications may change; images non-binding; stock limitation. | represented | Used as evidence-boundary rules, not vehicle attributes. |

## Audit conclusion

Every material page fact is classified above. The audit confirms the July FlexiCharger correction, but also proves that the February brochure contains a different earlier commercial state. Therefore this package is documentation and evidence governance only; it does not mutate master data to manufacture consistency.

The next bounded package should compare the non-conflicting technical candidates (battery, charging times, performance, dimensions and luggage measurement contexts) against current master records and import only demonstrably missing observations.
