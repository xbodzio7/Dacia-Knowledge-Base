# Bigster Technical Page 20 Ambiguity Review

Authored review of `residual_gap_001`. Decisions preserve the source page and do not approve imports.

## Summary

| Measure | Value |
| --- | ---: |
| Reviewed candidates | 23 |
| Covered by selected evidence | 9 |
| Partially covered | 3 |
| Context-only non-import | 7 |
| Deferred source conflict | 2 |
| Unresolved signature mismatch | 2 |
| Selected evidence signatures | 36 |
| Selected evidence records | 143 |

## Candidate decisions

| Line | Candidate | Decision | Selected signatures | Exact text |
| ---: | --- | --- | ---: | --- |
| 63 | `ff2cfb88e41d2640552d70cb85f81f9c6e28f6e02e0965457afdb1eba5a53397` | `covered_by_selected_evidence` | 1 | Układ kierowniczy                                                   Ze wspomaganiem elektrycznym |
| 77 | `86e33e875ec789d2158604e3d0d69634b0a600856d47ca16c21be4cfeb2081cc` | `covered_by_selected_evidence` | 2 | tarcza pełna:                                                                                                      (hamulec postojowy |
| 85 | `6b16b6b892640e914634c512e720f777a5c3f4933edc34b3a8b5e308d8175e61` | `partially_covered` | 3 |                                             6.5 J17 EC32           6.5 J17 EC32         225 / 55 R18 102 H XL         6.5 J17 EC32 |
| 87 | `a022542d3659709874331b49720c37d161e084cce3a2d39aa67dd9e2fa9077dc` | `covered_by_selected_evidence` | 4 | Rozmiary opon                               6.5 J18 EC32           6.5 J18 EC32         205 / 55 R19 97 H XL          6.5 J18 EC32 |
| 107 | `cbbf198ab0ba0278ef3263c4788363c82fb922edba05a81b5cc1a6b2ae5672e3` | `context_only_non_import` | 0 |       MASY (kg) I OBJĘTOŚCI (dm³ LUB LITRY) |
| 108 | `ac026cdc5eecd20db2d922394ed239bbb74841150e942e357db6577893850210` | `covered_by_selected_evidence` | 4 | Masa własna maks.                              1478                    1439                      1515                     1487 |
| 110 | `a6264f24a5055a7253605774bc3c18e3b6f0d427d904eea7f81208bc624d67c1` | `covered_by_selected_evidence` | 4 | Dopuszczalna masa całkowita |
| 113 | `c3c6fdaa07353e7979d62aa82463cbc10f6797712ff9b4cc99363a557fbcb28b` | `unresolved_signature_mismatch` | 0 | Dopuszczalna masa całkowita |
| 118 | `39db289420d88d1ea305961ef5b59d36444fdc0df9651876d7e78d2ea4404c47` | `unresolved_signature_mismatch` | 0 | Maksymalna masa przyczepy |
| 121 | `41bbd0e6df72e4f4f833936641ab29538dfb10915f9bdf138c87087fbd19b5cc` | `covered_by_selected_evidence` | 4 | Maksymalna masa przyczepy |
| 123 | `2384fc01f5d85e3b058641ef3295f3e7f84bc37d2fbe6c1b3390533ed7851ed5` | `covered_by_selected_evidence` | 4 | bez hamulca |
| 125 | `30383e012debb4437af7e2c4dc88fde985e8f3d5411af50e41e4bf6ab4583cf4` | `deferred_source_conflict` | 0 | pod półką bagażową                                                                      444 (nie ma zestawu |
| 126 | `d29ea5d85db0649b00ea016ba88e4d520a6bf53494c109b66a1f04ea8c37b6a4` | `partially_covered` | 3 | z zestawem naprawczym /                        609**                 667 / 624          naprawczego / koła              546 / 488 |
| 127 | `003f4ab48c8a1c45688384d0098cc137bc89e34850caeea03993df39c1679f63` | `covered_by_selected_evidence` | 2 | z kołem zapasowym(5)                                                                       zapasowego) |
| 128 | `668c92578b7754ecdd1186c9a0a66335fd1633469b305c5e978c11bb807a5266` | `context_only_non_import` | 0 | (dm³ VDA) |
| 130 | `89ef9a910122c654f65f9453b2dee74e699c88262eea67e3572110c7aac57050` | `context_only_non_import` | 0 | ze złożoną tylną kanapą |
| 131 | `eec3ad011ca04ebb1e04104807172f92ea41f0ea66ec25728d7faa031128e6a6` | `partially_covered` | 3 | z zestawem naprawczym /                       1877**               1937 / 1894                   1712                  1851 / 1791 |
| 132 | `b028c365c2607cc4600a9228e914262c789177b23670891c2b46fa8149e95b7d` | `covered_by_selected_evidence` | 2 | z kołem zapasowym(5) |
| 133 | `243364b290ee41854ec36d58beb10fef48920c134de37989db231feb0ab08af0` | `context_only_non_import` | 0 | (dm³ VDA) |
| 135 | `6f5fa4070102273882f5a279cec54cf62043e1a0b9de32b9713fd638d712dab4` | `deferred_source_conflict` | 0 | pod półką bagażową                                                                      556 (nie ma zestawu |
| 137 | `34b6006dbff656d524640adc5e972d955cc8422ca34aa7feaed53031c3037c77` | `context_only_non_import` | 0 | z zestawem naprawczym /                                                                    zapasowego) |
| 140 | `9ee1a9f2d2fc72f55882adb1e9c6dfb5b032fb6b7f83b98c7b4cdd577ff2ae0d` | `context_only_non_import` | 0 | ze złożoną tylną kanapą |
| 142 | `4a8c8eeaa984895ae6b4e732dbd2ace7c4690e04e7af1b27d3234d03b290eeef` | `context_only_non_import` | 0 | z zestawem naprawczym / |

## Residual authored findings

### Line 85 — `6b16b6b892640e914634c512e720f777a5c3f4933edc34b3a8b5e308d8175e61`

Three 4x2 wheel fragments map to preserved signatures. The 4x4 tyre fragment is visible in this line but its full signature is attached to the adjacent candidate at line 87.
- `standard_tyre_specification`: `225 / 55 R18 102 H XL` — No matching 4x4 signature is attached to this exact candidate; the full 4x4 signature is preserved on the adjacent line-87 candidate.

### Line 113 — `c3c6fdaa07353e7979d62aa82463cbc10f6797712ff9b4cc99363a557fbcb28b`

The following source line completes the label as gross vehicle weight, but every attached signature is gross train weight and therefore cannot support this row.
- `gross_vehicle_weight`: `1930`, `1890`, `2045`, `1940` — The correct row meaning and values are visible on page 20, but no matching preserved evidence signature is attached to this candidate.

### Line 118 — `39db289420d88d1ea305961ef5b59d36444fdc0df9651876d7e78d2ea4404c47`

The following source line completes the label as braked trailer weight, but every attached signature is unbraked trailer weight.
- `braked_trailer_weight`: `1500`, `1500`, `1500`, `1000` — The correct braked-trailer values are visible on page 20, but no matching preserved evidence signature is attached to this candidate.

### Line 125 — `30383e012debb4437af7e2c4dc88fde985e8f3d5411af50e41e4bf6ab4583cf4`

The 444 dm³ VDA Hybrid-G 150 4x4 value belongs to the brochure column whose tyre-repair-kit wording contradicts the equipment evidence; the existing cargo review deliberately deferred that complete column.
- `boot_capacity`: `444` — Hybrid-G 150 4x4 cargo remains deferred until the tyre-repair-kit contradiction is resolved by corrected official evidence.

### Line 126 — `d29ea5d85db0649b00ea016ba88e4d520a6bf53494c109b66a1f04ea8c37b6a4`

Repair-kit values 609, 667 and 546 are attached to this candidate. Spare-wheel values 624 and 488 are preserved on the adjacent line-127 candidate; the Hybrid-G 150 equipment context remains deferred.
- `boot_capacity`: `624`, `488` — Matching spare-wheel signatures are attached to the adjacent line-127 candidate rather than this exact candidate.

### Line 131 — `eec3ad011ca04ebb1e04104807172f92ea41f0ea66ec25728d7faa031128e6a6`

Repair-kit values 1877, 1937 and 1851 are attached here. Spare-wheel values 1894 and 1791 are attached to line 132, while Hybrid-G 150 value 1712 remains in the deliberately deferred column.
- `boot_capacity`: `1894`, `1791` — Matching spare-wheel signatures are attached to the adjacent line-132 candidate.
- `boot_capacity`: `1712` — Hybrid-G 150 4x4 cargo remains deferred due to the documented equipment-context contradiction.

### Line 135 — `6f5fa4070102273882f5a279cec54cf62043e1a0b9de32b9713fd638d712dab4`

The 556 ordinary-litre Hybrid-G 150 4x4 value belongs to the same deliberately deferred cargo column with contradictory equipment context.
- `boot_capacity`: `556` — Hybrid-G 150 4x4 cargo remains deferred until corrected official evidence resolves the equipment contradiction.

## Safety boundary

- no file under `data/master` is changed;
- no approved import specification is created or changed;
- no mismatched signature is substituted across attributes;
- Hybrid-G 150 4x4 cargo remains deferred under the existing source-conflict decision.

## Next package

**Jogger Technical Page 19 Ambiguity Review** — Review the 16 ambiguous technical candidates from Jogger brochure page 19 against their 34 preserved evidence signatures without creating master-data rows or approved import specifications.
