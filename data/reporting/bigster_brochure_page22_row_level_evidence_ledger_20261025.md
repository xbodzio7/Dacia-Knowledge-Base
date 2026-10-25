# Bigster brochure page 22 — row-level evidence ledger

Reviewed: 2026-10-25  
Source: `src_pl_bigster_brochure_20251210`, dated 2025-12-10  
Archived PDF SHA-256: `76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74`  
Page: 22; grade columns in the source review: Essential, Expression, Journey, Extreme.

This ledger organizes candidate mappings from the existing unresolved-review chunk and has now been checked against the rendered page image (PDF page index 21, printed page 22). The page's printed legend defines `•` as standard, `○` as optional, and `-` as unavailable. Nothing in this file approves a data import.

| Row | Extracted values / text | Existing attribute candidates | Reconciliation decision |
|---|---|---|---|
| Folding key | •, •, -, - | Existing key attributes require definition check | Visually confirmed: standard in Essential/Expression; unavailable in Journey/Extreme. Check attribute semantics before mapping. |
| Keyless Entry card | -, -, •, • | `keyless_entry`, if its definition matches card-based access | Visually confirmed: unavailable in Essential/Expression; standard in Journey/Extreme. Preserve the source term “card” when checking semantics. |
| 7-inch digital cluster | •, •, -, - | `instrument_cluster_colour_7` (314) | Visually confirmed: standard in Essential/Expression only. The row names screen size, not colour; attribute definition is not an exact semantic match. |
| 10-inch digital cluster | -, -, •, • | `instrument_cluster_colour_10_1` (383) | Visually confirmed: standard in Journey/Extreme only. Not an exact size match: source says 10-inch, dictionary says 10.1-inch; do not map until resolved. |
| Dual-zone automatic HVAC | -, •, •, • | `dual_zone_climate_control` (295), `automatic_climate_control` (294) | Visually confirmed: unavailable in Essential; standard in Expression/Journey/Extreme. Label and markers align on the rendered row. |
| Electric heated mirrors | •, •, •, • | `side_mirrors_electric_adjustment` (242), `side_mirrors_heated` (243) | Visually confirmed standard in all four grades; source row explicitly combines electric adjustment and heating. Split only if both dictionary definitions and source evidence support it. |
| Power windows with one-touch | •, •, •, • | `front_windows_power` (231), `rear_windows_power` (232), `one_touch_windows` (233) | Visually confirmed standard in all four grades; the row explicitly covers front and rear windows with impulse/one-touch function. |
| Electric tailgate | -, -, •, ○ | `power_tailgate` (197) | Visually confirmed: unavailable in Essential/Expression, standard in Journey, optional in Extreme. The mark is `○` (not `¤`); page legend defines it as optional. |
| YouClip mounting points | 4, 5, 5, 5 | No exact count attribute; `youclip_phone_holder` (377) is not a count | Visually confirmed values. Page 8 prose says five standard points generally, so the Essential value of 4 remains a documented source conflict; do not normalize it away. |
| 12 V sockets | Essential: front; Expression/Journey/Extreme: front and boot | `boot_12v_socket` (379) | Visually confirmed. Existing attribute covers boot only, not front location/count; do not map the whole row to it. |
| USB-C ports | Essential: 2 front; Expression/Journey/Extreme: 2 front and 2 rear | `usb_ports_count` (289), `rear_usb_c_ports` (380) | Visually confirmed. Total count and rear-port presence do not fully encode front/rear distribution; preserve front/rear split. |
| Media Display | •, •, -, - | `media_display_system` (311), screen (279), touchscreen (280), wireless replication (313), speakers (421), Bluetooth (288), connected services (292) | Visually confirmed: standard in Essential/Expression; unavailable in Journey/Extreme. Description specifies a 10.1-inch touchscreen, USB or wireless Wi-Fi smartphone replication, Bluetooth, four speakers and remote-services package; split only into facts supported by the data contract. |

## Visual verification result

The rendered page image confirms the grade order (Essential, Expression, Journey, Extreme), the standard/optional/unavailable legend, and the values and markers recorded above. The electric-tailgate marker in Extreme is a hollow circle (`○`, optional), not the `¤` glyph suggested by the extracted text. The 12 V and USB-C row values are now read directly from their aligned table cells. This is page-level verification only; exact model/powertrain applicability and import signatures remain unresolved.

## Evidence boundary

The existing unresolved-review chunk lists 69 candidates on page 22; its first chunk contains 40 candidates, with 27 unresolved signature mismatches and 13 context-only fragments. It reports zero attached evidence signatures and zero attached evidence records. The existing ambiguity review's 126 selected records are from the 2026-07-03 price list and cannot establish grade applicability in the 2025-12-10 brochure.

## Next actions

1. Rendered page 22 has been inspected; row geometry, grade columns and symbol legend are visually confirmed.
2. Resolve exact candidate IDs for each row and marker; visual row confirmation does not resolve repository candidate signatures or authorize merging.
3. Join confirmed cells to exact model/powertrain/trim configuration signatures and the 2025-12-10 source receipt.
4. Generate imports only for fully resolved, source-backed facts. Keep ambiguous symbols, composite rows and dictionary gaps out of approved imports.

No files under `data/master` or `data/imports` are changed by this ledger.
