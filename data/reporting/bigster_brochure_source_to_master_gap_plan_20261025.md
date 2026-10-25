# Bigster brochure page 21–22 source-to-master reconciliation plan

- Review date: 2026-10-25
- Source: `src_pl_bigster_brochure_20251210`, official Bigster brochure dated 2025-12-10, SHA-256 `76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74`
- Scope: equipment matrix pages 21–22 and descriptive equipment pages 7–8, 9, 14–18.
- Status: diagnostic reconciliation plan; no master observations or import specs are approved by this document.

## Evidence boundary

The page 21–22 crosswalk contains 176 candidate fragments: 107 on page 21 and 69 on page 22. Current unresolved chunks report 90 candidates with signature mismatches (56 + 34) and zero attached evidence signatures/records. The ambiguity-review artifacts contain 140 selected records (14 + 126) from the 2026-07-03 price list. Those records are useful only as later-period comparison context and cannot prove grade applicability in the 2025-12-10 brochure.

The 2026-10-01 price list is a current commercial comparator, not a substitute for the brochure's historical equipment state. Preserve source date, exact model/engine/trim qualifiers, and source wording for each observation.

## Candidate row-to-attribute reconciliation

| Source row / evidence group | Existing dictionary candidates | Assessment and next action |
|---|---|---|
| 12 V sockets: front and luggage compartment | `boot_12v_socket` (379) | Partial semantic coverage only. The existing boolean represents the boot socket; it does not encode front socket presence or count/location. Do not map the entire row to this field. Resolve candidate fragments and determine whether a front-socket attribute is needed. |
| USB-C ports: two front and two rear | `usb_ports_count` (289), `rear_usb_c_ports` (380) | These represent total count and rear-port presence separately, but do not prove the front/rear distribution or charging/data role. Confirm the visual row's markers and exact grade columns before recording independent values. |
| Media Display composite row | `media_display_system` (311), `infotainment_screen_size` (279), `touchscreen` (280), `wireless_smartphone_replication` (313), `speaker_count` (421), `connected_services` (292), `bluetooth_connectivity` (288) | Do not collapse into one boolean. Split only facts explicitly stated by the dated source; keep system identity distinct from screen, replication, speakers, Bluetooth and service package. Page 14 Essential prose can support the described feature scope, but does not independently establish all matrix grade markers. |
| Media Nav Live composite row | `infotainment_screen_size` (279), `touchscreen` (280), `navigation_system` (283), `live_traffic_information` (284), `wireless_smartphone_replication` (313), `speaker_count` (421), `connected_services` (292) | Multiple attributes, not one feature. Keep onboard navigation distinct from smartphone replication; preserve the stated live-traffic/map-update duration as its own source-scoped fact if the schema supports it. Do not infer the trim matrix from the narrative description alone. |
| Remote services / vehicle location / FOTA | `connected_services` (292), `remote_firmware_updates` (382) | Conceptual matches only. Separate remote vehicle functions from firmware updates and from any service term/duration. Confirm wording and matrix markers against the actual 2025 brochure before creating observations. |
| Dual-zone climate control | `dual_zone_climate_control` (295), `automatic_climate_control` (294) | Potential direct semantic match, but grade applicability must be read from the 2025 matrix. Do not transfer July 2026 price-list evidence to the earlier brochure. |
| Centre console variants / wireless charging | `centre_console_variant` (414), `wireless_charging` (290) | Keep physical console type and wireless charging as separate observations. Page 7 narrative may explain a configuration but does not replace matrix-level grade evidence. |
| Power windows / one-touch operation | `front_windows_power` (231), `rear_windows_power` (232), `one_touch_windows` (233) | Existing dictionary can represent the distinct claims; extract separate facts only where the source wording and matrix cells establish them. |
| Mirrors | `side_mirrors_electric_adjustment` (242), `side_mirrors_heated` (243), `side_mirrors_folding` (244) | Existing dictionary covers several functions separately. Confirm whether the brochure's composite wording asserts each function and preserve trim applicability independently. |
| YouClip mounting points | `youclip_phone_holder` (377) is not a count attribute | A boolean phone-holder field does not represent the number of mounting points. Brochure narrative and matrix appear to differ (narrative says five standard points; matrix row shows 4/5/5/5). Preserve as an explicit source conflict until visual/source context resolves it; do not normalize by inference. |

## Required resolution sequence

1. Re-open the rendered page 21 and page 22 images and capture the exact row boundaries, column headings, markers and footnotes for each unresolved signature group.
2. For every candidate, record its exact candidate ID, row label, column/trim, marker, and evidence source/page. Do not merge candidates solely because extracted text is similar.
3. Join each resolved row to the correct model/powertrain/trim configuration and source-period receipt. Later price-list observations may be used only for a separately dated comparison.
4. Reuse an existing attribute only when its definition exactly matches the fact's scope. Record dictionary gaps for counts, locations, roles or service duration rather than forcing composite rows into narrower booleans.
5. Generate import specifications only for fully resolved, source-backed observations. Keep unresolved, contradictory and context-only items out of approved imports.
6. Run the repository's normal validation and quality workflow against the resulting commit before proposing any merge.

## Decision

No data-master values, configuration import specifications, or attribute definitions are changed by this plan. The next data-changing step remains blocked on exact candidate signature and grade-cell resolution, not on the existence of superficially similar attribute names.
