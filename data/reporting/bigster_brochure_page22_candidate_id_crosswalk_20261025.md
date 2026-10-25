# Bigster brochure page 22 — candidate-ID crosswalk

- Review date: 2026-10-25
- Source: `src_pl_bigster_brochure_20251210`, brochure dated 2025-12-10
- Source SHA-256: `76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74`
- Scope: exact candidate IDs from the authored unresolved-review chunks, reconciled to the rendered page 22 row layout.
- Status: candidate-level crosswalk only; no observation or import is approved.

## Visually aligned rows and exact candidate IDs

| Printed row / group | Candidate ID(s) | Rendered page-22 reading | Existing candidate attribute / decision boundary |
|---|---|---|---|
| YouClip mounting points | `70336206b610a44ffbea4d1449fe7b3f1cc4eba9ba28ff5054ff578a1da4729e` | 4 / 5 / 5 / 5 across Essential / Expression / Journey / Extreme | Candidate group `youclip_mounting_points`; no exact count attribute. `youclip_phone_holder` is not a count. Keep page-8 prose conflict open. |
| Folding key | `524e5967dd7f40bca44a0354dff7d503532fbc06b8ab2abdee6e39d0fed0809a` | standard / standard / unavailable / unavailable | Group `folding_key`; confirm dictionary definition before mapping. |
| Keyless Entry card | `4a4c8af29d0ba66987c78a6dc9e32ad7e32491de75df1af839c1466f3acc79a7` | unavailable / unavailable / standard / standard | Group `keyless_entry_card`; preserve the card-specific wording. |
| 7-inch digital cluster | `c6cc0d2dec8be5fedfbc4259e9c98c87875f90be230385bd4b8eb95ae5a9cd57` | standard / standard / unavailable / unavailable | Group `digital_instrument_cluster_7`; do not force into a colour-specific attribute without checking definition. |
| 10-inch digital cluster | `ff44882ec1f67c7c28bcd88a563d684c9235355dde5a4df1f8b82add175f1882` | unavailable / unavailable / standard / standard | Group `digital_instrument_cluster_10`; source says 10-inch while dictionary candidate says 10.1-inch. |
| Dual-zone climate row | `47f2b824d251f1c71c2c147edb149f4c02a2c6ba12bdfe29db305cb5f7921394` (marker row) plus context `090b4158f01b1b969e0bbc14e3c91f195157c07b4b30caf2d11d801dfd7ccf7e` | unavailable / standard / standard / standard | Group `automatic_dual_zone_hvac`; attached phrase “with rear passenger vents” needs source-scope handling. Candidate row is still marked unresolved; do not treat the text alignment alone as signature resolution. |
| Heated electric mirrors | `238ccc4a14556569503a14119a8bf823bcff88b53db94463c433d3315f802aa6` | standard in all four grades | Group `heated_power_side_mirrors`; split electric adjustment/heating only if definitions support each claim. |
| Front/rear one-touch windows | `5504649f300ace2147721b88c9213ca6eb13f10f051cb68d0a07465c0e08ef82`, `901037523e70e18a3ed92b7fbc3cbbeed90f31bfedaaf81474ed8110aefd68e1`, `e6a1efb3b466aef3d1c6f5cd6dbe38bbe04e820adcae89b59330b36424bb3cf3` | standard in all four grades; label split across fragments | Group `front_rear_impulse_windows`; row-level visual match does not remove candidate signature mismatch. |
| Electric tailgate | `736d43d00586fbe1a501306798eb212228535826c991267e1da36937bb60e371` | unavailable / unavailable / standard / optional | Group `power_tailgate`; rendered glyph is hollow circle `○`, optional per legend. |
| 12 V sockets | `e7d6b02a51e87578b4bdaf32db1b9b4006082f5d5716e9a183e4f3e7fa33217c`, `2feee8d06620a8c1199b9005e3295e3640fc109bc634e3d2dc82c1b94daf3056`, `b65c7cc2ec9b87f51bf9ea81281493fa8c7e83a26afb8d8bf6442a6c1c5e8cbe` | Essential: front; other grades: front and boot | Group `12v_sockets`; current `boot_12v_socket` covers only the boot, not front location/count. Three IDs are fragments of one printed row, not three observations. |
| USB-C ports | `3beb3a745c8fa0d7eeda03a81a6336d9bc097725699900e434d027675280926b`, `f8a3f49781d16618e4e4b319718aab7ece75f897d1b2d68898b2bb98e08e5940`, `391c54b60427afea0b2eabf9f1e0cea9b9270f8e5a3427e101f16c4a3fd4e4f8` | Essential: 2 front; other grades: 2 front and 2 rear | Group `usb_c_ports`; total count and rear presence do not encode front/rear distribution by themselves. Three IDs are fragments of one row, not three observations. |
| Media Display | `479c98d76ce6ddf9cfe2639d774dad18d025af33aab52f320d7971609021d1f1`, `969ea9c0482a755d2a951f7ca6b1f5b855fcfb8139c05e77f45739ac25ab145a`, `354c9b08a63003f1745b481a7702ef70165a6bc2a6cf4271bf2307ea4f6f2925`, `d3123a3dcc4a515387704a1097e79cb6523cabfbce716e27b278ac3e4a33380e`, `4f3b85d5b612d1c18cf46141b2292eed810e3e6e0b1a5f1cf8a438c70a3be4ab`, `54bb31f9448d9428c44eec011f826595ec09e6905f16b0b0aa31f4b7b513cf9e`, `4de666b3aa2dd0a80492d2e36548b0333469eae2378db9525e259cc5c0759229` | standard / standard / unavailable / unavailable; description includes 10.1-inch touch screen, USB or Wi-Fi replication, Bluetooth, four speakers and remote-services package | Group `media_display`; composite source row must be decomposed only into distinct facts explicitly supported by the data dictionary and source. |
| Media Nav Live | Candidate label begins with `999c86a7ab32beba542eb38ad668b2658d08ea97a5e959dcefc00e3313fc238c`; see chunk 2 for following candidates | unavailable / optional / standard / standard | Group `media_nav_live`; use exact IDs from chunk 2 for the aligned marker and continuation fragments; narrative detail is not itself a grade marker. |

## Legend and source conflict handling

The rendered page uses `•` = standard, `○` = optional, `-` = unavailable. Some extracted review chunks encode the option glyph as `¤`; this crosswalk uses the rendered reading for interpretation but does not rewrite the original candidate text. Page 8 prose says five standard YouClip mounting points, while the matrix shows 4/5/5/5; retain this as a source conflict rather than normalizing it.

## What this crosswalk resolves — and what it does not

- Resolves the relationship between several fragment IDs and their visually aligned printed rows on page 22.
- Does not establish the exact model/powertrain/trim configuration signature for any observation.
- Does not authorize merging candidate IDs or generating import specs.
- Does not use the July 2026 price list to rewrite the December 2025 brochure state.
- The next safe data step is to resolve configuration signatures and dictionary fit, then generate import specs only for fully supported facts.

No files in `data/master` or `data/imports` are changed by this crosswalk.
