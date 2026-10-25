# Bigster brochure page 22 — row-level evidence ledger

Reviewed: 2026-10-25  
Source: `src_pl_bigster_brochure_20251210`, dated 2025-12-10  
Archived PDF SHA-256: `76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74`  
Page: 22; grade columns in the source review: Essential, Expression, Journey, Extreme.

This ledger organizes candidate mappings from the existing unresolved-review chunk. The symbols are transcribed from that review and have not been independently pixel-verified here. Nothing in this file approves a data import.

| Row | Extracted values / text | Existing attribute candidates | Reconciliation decision |
|---|---|---|---|
| Folding key | •, •, -, - | Existing key attributes require definition check | Verify row and markers in rendered page. |
| Keyless Entry card | -, -, •, • | `keyless_entry`, if its definition matches card-based access | Verify semantics and matrix cells. |
| 7-inch digital cluster | •, •, -, - | `instrument_cluster_colour_7` (314) | Check whether the source specifically means colour. |
| 10-inch digital cluster | -, -, •, • | `instrument_cluster_colour_10_1` (383) | Not an exact size match: source says 10-inch, dictionary says 10.1-inch. Resolve before mapping. |
| Dual-zone automatic HVAC | -, •, •, • | `dual_zone_climate_control` (295), `automatic_climate_control` (294) | Label and markers are separate candidates; confirm their visual association. |
| Electric heated mirrors | •, •, •, • | `side_mirrors_electric_adjustment` (242), `side_mirrors_heated` (243) | Split into separate facts only after verifying source wording and grade cells. |
| Power windows with one-touch | •, •, •, • | `front_windows_power` (231), `rear_windows_power` (232), `one_touch_windows` (233) | The label is split across text and marker fragments; resolve the row boundary first. |
| Electric tailgate | -, -, •, ¤ | `power_tailgate` (197) | Interpret `¤` only using the source legend/footnote. |
| YouClip mounting points | 4, 5, 5, 5 | No exact count attribute; `youclip_phone_holder` (377) is not a count | Preserve as a dictionary gap and check against the brochure prose. |
| 12 V sockets | Fragments: front / “Gniazda 12 V” / “and boot” with aligned values | `boot_12v_socket` (379) | Existing attribute covers boot only, not front location/count. Do not map whole row to it. |
| USB-C ports | Fragments: “2 front” / “Porty USB-C” / “and 2 rear” with aligned values | `usb_ports_count` (289), `rear_usb_c_ports` (380) | Total count and rear-port presence do not fully encode front/rear distribution. Resolve exact columns and roles. |
| Media Display | Marker fragment •, •, -, -; description spans neighbouring candidates | `media_display_system` (311), screen (279), touchscreen (280), wireless replication (313), speakers (421), Bluetooth (288), connected services (292) | Composite row; split into separately supported facts only after attaching the label and cells. |

## Evidence boundary

The existing unresolved-review chunk lists 69 candidates on page 22; its first chunk contains 40 candidates, with 27 unresolved signature mismatches and 13 context-only fragments. It reports zero attached evidence signatures and zero attached evidence records. The existing ambiguity review's 126 selected records are from the 2026-07-03 price list and cannot establish grade applicability in the 2025-12-10 brochure.

## Next actions

1. Inspect the rendered page 22, confirm row geometry, grade columns and symbol legend.
2. Resolve exact candidate IDs for each row and marker; do not merge candidates merely because extracted text looks similar.
3. Join confirmed cells to exact model/powertrain/trim configuration signatures and the 2025-12-10 source receipt.
4. Generate imports only for fully resolved, source-backed facts. Keep ambiguous symbols, composite rows and dictionary gaps out of approved imports.

No files under `data/master` or `data/imports` are changed by this ledger.
