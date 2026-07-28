# Bigster Technical Page 20 Unresolved Review — Chunk 1

Authored review of `residual_gap_016`. Forty extraction candidates are regrouped into visual table rows; the review records source facts but does not approve imports.

## Summary

| Measure | Value |
| --- | ---: |
| Reviewed candidates | 40 |
| Logical visual groups | 18 |
| Context-only non-import | 24 |
| Unresolved signature mismatch | 16 |
| Candidates with source facts | 16 |
| Attached evidence signatures | 0 |
| Attached evidence records | 0 |

## Visual table boundary

The page contains four powertrain columns: `MILD HYBRID-G 140`, `MILD HYBRID 140`, `HYBRID-G 150 4×4` and `HYBRID 155`. Wrapped `pdftotext` lines are grouped by their visual row alignment rather than treated as independent records.

## Candidate decisions

| Line | Candidate | Logical row | Role | Decision | Exact text |
| ---: | --- | --- | --- | --- | --- |
| 5 | `fe2e4bbddf98efca3fea972cd5d62abb64bd3ea4c6e94e97448b51bdc686dbe3` | `powertrain_column_headers` | `column_header_fragment` | `context_only_non_import` |                                             MILD                    MILD                  HYBRID-G 150 |
| 6 | `78aa33f1e125355d6616770337a52eb3aff29637e92c9cb6365a8f9dfbb03c7b` | `powertrain_column_headers` | `column_header_fragment` | `context_only_non_import` |                                          HYBRID-G 140             HYBRID 140                  4×4                    HYBRID 155 |
| 10 | `fad89352b82930471c5d7d2ee0f508fddf0ab4b7f6d8de5ce3d4f43f351866ca` | `propulsion` | `logical_row_fragment` | `context_only_non_import` |                                           Benzyna / LPG /                                  Benzyna / LPG / |
| 11 | `28488d7cf41f1fcdaf317f4d473c4056fdba6ddaba04ddfd90cee41070d84e35` | `propulsion` | `logical_row_fragment` | `context_only_non_import` |                                                                Benzyna / Elektryczny                              Benzyna / Elektryczny |
| 12 | `491bb2cc55b0ac3835ce906e6895f7c8b10746634ba21a631ee53fc48865195c` | `propulsion` | `logical_row_anchor` | `unresolved_signature_mismatch` | Napęd                                     Elektryczny mild |
| 13 | `fc25db03221c0e1572499b2a41fbd2fe825191f0a7a66d2685b19716e7aafb31` | `propulsion` | `logical_row_fragment` | `context_only_non_import` |                                                                  mild hybrid 48 V |
| 14 | `22c7ab2ee31f8963bc80532bfe7ad73c0e6586e77bf9e4b8a20c7114c26eb016` | `propulsion` | `logical_row_fragment` | `context_only_non_import` |                                                                                              Elektryczny |
| 15 | `e53cfd68de999c7ac808e244d8bc80e8619f1258e8544de9916ba4044f24ea38` | `propulsion` | `logical_row_fragment` | `context_only_non_import` |                                                                                                                     full hybrid 280 V |
| 16 | `8673121d1a3b72811cab1bee6e74a4f47582a06b3ef225d6d9dc82018b163db1` | `propulsion` | `logical_row_fragment` | `context_only_non_import` |                                              hybrid 48 V                                   mild hybrid 48 V |
| 19 | `fb20adc0d224e7a1b869ec7d332a7c98dc717dec86c1f5067a00c719962246a0` | `maximum_power` | `logical_row_fragment` | `context_only_non_import` |                                            103 (140 KM)            103 (140 KM)         4500 obr./min – silnik        116 (155 KM) |
| 20 | `e03fb931711633e75e5672bfa443f95dc273dc525232d19d8c41c84b5db71c75` | `maximum_power` | `logical_row_anchor` | `unresolved_signature_mismatch` | Maks. moc kW CEE (KM)                       przy 5500               przy 5500             spalinowy / 113              przy 5300 |
| 24 | `72a73b4af30010128e25b25de74f8cfd56d674bfcc831dce3958071747530f83` | `maximum_torque` | `logical_row_anchor` | `unresolved_signature_mismatch` | Maks. moment obrotowy N.m                                                                                         172 (silnik spalinowy) |
| 25 | `24ec7dc9889ef8bd9798821724ced6b6374e068cea11e95c27f1288facdb6377` | `maximum_torque` | `logical_row_fragment` | `context_only_non_import` |                                                                                           (silnik spalinowy) |
| 26 | `6c6f693ace59115446879ebf943ea316cc3bdf80a8f9878439ae0f27af123b04` | `maximum_torque` | `logical_row_fragment` | `context_only_non_import` |                                            230 przy 2100          230 przy 2100                                    / 205 (elektryczny) |
| 27 | `21c5538b44fd6d08c5be98223b3e5a52a820091aac96b78908ddb37fb5aba602` | `maximum_torque` | `logical_row_fragment` | `context_only_non_import` | CEE (m.kg)                                                                                   87 przy 1630 |
| 28 | `d3a03e88dcea26ed303fe3c7a4d25394471b390f733df9f4e26dd8980e42513c` | `maximum_torque` | `logical_row_fragment` | `context_only_non_import` |                                                                                                                   przy 3000 / 0 – 1630* |
| 29 | `ab3fca9a8b99a6b1a47470581a87586cc45c7736ac8f96fe2fba7fca42fa5755` | `maximum_torque` | `logical_row_fragment` | `context_only_non_import` |                                                                                              (elektryczny) |
| 31 | `b2703123c87da2f621b84fca0ed33368b9bd036ab06cde3f47cae658c26566de` | `injection_type` | `logical_row_anchor` | `unresolved_signature_mismatch` | Rodzaj wtrysku                          Wtrysk bezpośredni     Wtrysk bezpośredni       Wtrysk bezpośredni        Wtrysk bezpośredni |
| 33 | `9046696317271c1f52161a388ef46b4754c24a32bdff3771a3fcf8e06d6f093a` | `engine_displacement` | `logical_row_anchor` | `unresolved_signature_mismatch` | Pojemność skokowa (cm³)                        1199                    1199                      1199                     1789 |
| 35 | `b0d187453089cb6f8d39396a90996b12eaedb73748fbacc4af6fb0f37a169ffe` | `cylinders_valves` | `logical_row_fragment` | `context_only_non_import` |                                             3 cylindry /           3 cylindry /              3 cylindry /             4 cylindry / |
| 36 | `4cb21410084333f9b77d4d8a4a23ab5ed22bb9528f2af4edd8dcba89d1596a1c` | `cylinders_valves` | `logical_row_anchor` | `unresolved_signature_mismatch` | Liczba cylindrów / zaworów                  12 zaworów             12 zaworów                12 zaworów               16 zaworów |
| 38 | `88231855b278f9d02f1ee0ed24d188631fb7d35b601418801e5c20b93537a23f` | `emissions_standard` | `logical_row_anchor` | `unresolved_signature_mismatch` | Norma emisji spalin                         Euro 6e-bis             Euro 6e-bis               Euro 6e-bis              Euro 6e-bis |
| 40 | `03df968747a867a246804c50d88b8fc1acca4a17672defd6d621c17af2598089` | `particulate_filter` | `logical_row_anchor` | `unresolved_signature_mismatch` | Filtr cząstek stałych(1)                                                            Tak |
| 43 | `ea690e6c1710e58c2a9780387d4a807e7910bfc46ae741369f9e38c24d0deea2` | `traction_battery` | `logical_row_fragment` | `context_only_non_import` |                                           Litowo-jonowy /        Litowo-jonowy /           Litowo-jonowy /          Litowo-jonowy / |
| 44 | `eab19e5c712c99e9fc939b62f30404672e293a8fee3ec6707d800d135f96f9e1` | `traction_battery` | `logical_row_anchor` | `unresolved_signature_mismatch` | Akumulator trakcyjny                      48 V / 0,84 kWh        48 V / 0,84 kWh           48 V / 0,84 kWh          280 V / 1,4 kWh |
| 47 | `8abc22effbc6ceaeb9f63e9a1b1a0f184a7416515bd9d309b4afa52e53326a86` | `maximum_speed` | `logical_row_anchor` | `unresolved_signature_mismatch` | Prędkość maksymalna (km/h)                      180                    180                        180                      180 |
| 49 | `42325454e30aae2121ca8d12da06ccc497caaa016b798cc3fa9c9c790051c31c` | `acceleration_0_100` | `logical_row_anchor` | `unresolved_signature_mismatch` | 0–100 km/h (s)                                  10,0                    9,8                      10,4                      9,7 |
| 53 | `6f8d0d060e446a4bdf6cf592fe76c0bedcbcfdcecf356c4e1f2e2eddf1883d71` | `drivetrain` | `logical_row_anchor` | `unresolved_signature_mismatch` | Napęd                                           4×2                    4×2                     silnikiem                  4×2 |
| 54 | `d46bdb8084e15d819207d3bf2fa69a614d955d974391a5a2fa9df3c938677d0e` | `drivetrain` | `logical_row_fragment` | `context_only_non_import` |                                                                                              elektrycznym |
| 56 | `130edef9be31e8febd038dc736d658a5a27793a27ed486ee52f2bba54d1d0ab0` | `gearbox` | `logical_row_anchor` | `unresolved_signature_mismatch` | Typ skrzyni biegów / liczba                                                                 Automatyczna, |
| 57 | `6f7fa9b4ff3cba6eb767f3e3ec23c4f57ce9d09e7fbb2e46cdf5b77cf2566c31` | `gearbox` | `logical_row_fragment` | `context_only_non_import` |                                              Manualna,              Manualna,                                        Automatyczna |
| 58 | `bd1d0bed3162c85600fb520e4ac8e34a8e331ac962bb06f4b498a3bd0b2c0f3d` | `gearbox` | `logical_row_fragment` | `context_only_non_import` |                                                                                            dwusprzęgłowa, |
| 59 | `352580744d0aebdbd1d7a0d0459dd4d255e6c26313fe9f50cc331ba7ef69a72c` | `gearbox` | `logical_row_fragment` | `context_only_non_import` | przełożeń                                    6-biegowa              6-biegowa                                       Multi-mode, 4+2 |
| 70 | `dfc02d5d784726ad2ac37e0dfcc2204ad624b621adb4f69021ab716bbe8e5ecd` | `front_brakes` | `logical_row_anchor` | `unresolved_signature_mismatch` |                                              Φ296x26                 Φ296x26                   Φ296x26                  Φ296x26 |
| 71 | `0e1380b9c94c35fc4da51f7bb59d2351d7f6757ed840de438990a81dc4ee5479` | `front_brakes` | `logical_row_fragment` | `context_only_non_import` | średnica (mm): |
| 74 | `9d6ea7a46f8a722846583c808a39d5654402e79d467a34b5840a3a9ba86901d1` | `rear_brakes_prior_review` | `prior_review_fragment` | `context_only_non_import` | Tył: bęben, średnica (cale) /             bęben (hamulec postojowy manualny): |
| 79 | `6923b4e538908c5b9e50bd1f5dd4c52d371ac3651411dfc24b42ebd045f1ce91` | `rear_brakes_prior_review` | `prior_review_fragment` | `context_only_non_import` |                                                                                                                      automatyczny): |
| 80 | `e77ff2bd2ab78f2643195af574507e1ce50197cc47976306a41bd3daac42d812` | `rear_brakes_prior_review` | `prior_review_fragment` | `context_only_non_import` |                                                                                                                          Φ280x9,6 |
| 93 | `5b951e167b6bb93e949111524d587b2a2ff35f05be559ee10f71ff3520d553b3` | `homologation_protocol` | `logical_row_anchor` | `unresolved_signature_mismatch` | Protokół homologacji                                                               WLTP(3) |
| 95 | `61a3ac9b52bfbf384bca8f83f522cc7cb1f8def65d3b1df001ea829a4e73d2c2` | `eco_mode` | `logical_row_anchor` | `unresolved_signature_mismatch` | Tryb Eco                                                                            Tak |

## Review-only source facts

### Line 12 — `propulsion`

The complete logical row is legible from the visual page layout, but this residual package contains no attached conservative evidence signature. The source fact is recorded for review only and does not approve an import.

- `mild_hybrid_g_140`: `Benzyna`; `LPG`; `Elektryczny mild hybrid 48 V`
- `mild_hybrid_140`: `Benzyna`; `Elektryczny mild hybrid 48 V`
- `hybrid_g_150_4x4`: `Benzyna`; `LPG`; `Elektryczny mild hybrid 48 V`
- `hybrid_155`: `Benzyna`; `Elektryczny full hybrid 280 V`
- Boundary: The complete multi-line propulsion row is visually legible, but this residual package has no attached conservative evidence signature.

### Line 20 — `maximum_power`

The complete logical row is legible from the visual page layout, but this residual package contains no attached conservative evidence signature. The source fact is recorded for review only and does not approve an import.

- `mild_hybrid_g_140`: `103 kW (140 KM) przy 5500 obr./min`
- `mild_hybrid_140`: `103 kW (140 KM) przy 5500 obr./min`
- `hybrid_g_150_4x4`: `103 kW (140 KM) przy 4500 obr./min – silnik spalinowy`; `113 kW (150 KM) – moc łączna`
- `hybrid_155`: `116 kW (155 KM) przy 5300 obr./min`
- Boundary: The values and combustion-versus-combined-power distinction are visible in the row, but no exact signature is attached to the package.

### Line 24 — `maximum_torque`

The complete logical row is legible from the visual page layout, but this residual package contains no attached conservative evidence signature. The source fact is recorded for review only and does not approve an import.

- `mild_hybrid_g_140`: `230 N.m przy 2100 obr./min`
- `mild_hybrid_140`: `230 N.m przy 2100 obr./min`
- `hybrid_g_150_4x4`: `230 N.m przy 4000 obr./min – silnik spalinowy`; `87 N.m przy 1630 obr./min – elektryczny`
- `hybrid_155`: `172 N.m przy 3000 obr./min – silnik spalinowy`; `205 N.m przy 0–1630 obr./min – elektryczny`
- Boundary: The complete multi-line torque row is visually legible; the asterisk remains source context, and no exact signature is attached.

### Line 31 — `injection_type`

The complete logical row is legible from the visual page layout, but this residual package contains no attached conservative evidence signature. The source fact is recorded for review only and does not approve an import.

- `mild_hybrid_g_140`: `Wtrysk bezpośredni`
- `mild_hybrid_140`: `Wtrysk bezpośredni`
- `hybrid_g_150_4x4`: `Wtrysk bezpośredni`
- `hybrid_155`: `Wtrysk bezpośredni`
- Boundary: All four columns state direct injection, but the unresolved package carries no evidence signature.

### Line 33 — `engine_displacement`

The complete logical row is legible from the visual page layout, but this residual package contains no attached conservative evidence signature. The source fact is recorded for review only and does not approve an import.

- `mild_hybrid_g_140`: `1199`
- `mild_hybrid_140`: `1199`
- `hybrid_g_150_4x4`: `1199`
- `hybrid_155`: `1789`
- Boundary: The displacement row is complete but remains review-only without an attached signature.

### Line 36 — `cylinders_valves`

The complete logical row is legible from the visual page layout, but this residual package contains no attached conservative evidence signature. The source fact is recorded for review only and does not approve an import.

- `mild_hybrid_g_140`: `3 cylindry`; `12 zaworów`
- `mild_hybrid_140`: `3 cylindry`; `12 zaworów`
- `hybrid_g_150_4x4`: `3 cylindry`; `12 zaworów`
- `hybrid_155`: `4 cylindry`; `16 zaworów`
- Boundary: The two-line row is visually complete, but no exact candidate signature is attached.

### Line 38 — `emissions_standard`

The complete logical row is legible from the visual page layout, but this residual package contains no attached conservative evidence signature. The source fact is recorded for review only and does not approve an import.

- `mild_hybrid_g_140`: `Euro 6e-bis`
- `mild_hybrid_140`: `Euro 6e-bis`
- `hybrid_g_150_4x4`: `Euro 6e-bis`
- `hybrid_155`: `Euro 6e-bis`
- Boundary: The shared emissions standard is visible for all columns but has no attached signature in this package.

### Line 40 — `particulate_filter`

The complete logical row is legible from the visual page layout, but this residual package contains no attached conservative evidence signature. The source fact is recorded for review only and does not approve an import.

- `mild_hybrid_g_140`: `Tak`
- `mild_hybrid_140`: `Tak`
- `hybrid_g_150_4x4`: `Tak`
- `hybrid_155`: `Tak`
- Boundary: The visually shared yes marker spans all four powertrains; it is not converted into approved data without a signature.

### Line 44 — `traction_battery`

The complete logical row is legible from the visual page layout, but this residual package contains no attached conservative evidence signature. The source fact is recorded for review only and does not approve an import.

- `mild_hybrid_g_140`: `Litowo-jonowy`; `48 V`; `0,84 kWh`
- `mild_hybrid_140`: `Litowo-jonowy`; `48 V`; `0,84 kWh`
- `hybrid_g_150_4x4`: `Litowo-jonowy`; `48 V`; `0,84 kWh`
- `hybrid_155`: `Litowo-jonowy`; `280 V`; `1,4 kWh`
- Boundary: The type, voltage and capacity are visually joined within one row; no scalar or compound signature is attached.

### Line 47 — `maximum_speed`

The complete logical row is legible from the visual page layout, but this residual package contains no attached conservative evidence signature. The source fact is recorded for review only and does not approve an import.

- `mild_hybrid_g_140`: `180`
- `mild_hybrid_140`: `180`
- `hybrid_g_150_4x4`: `180`
- `hybrid_155`: `180`
- Boundary: The complete row is visible but remains unresolved because no evidence signature is attached.

### Line 49 — `acceleration_0_100`

The complete logical row is legible from the visual page layout, but this residual package contains no attached conservative evidence signature. The source fact is recorded for review only and does not approve an import.

- `mild_hybrid_g_140`: `10,0`
- `mild_hybrid_140`: `9,8`
- `hybrid_g_150_4x4`: `10,4`
- `hybrid_155`: `9,7`
- Boundary: The complete acceleration row is visible but is not approved for import without an exact signature.

### Line 53 — `drivetrain`

The complete logical row is legible from the visual page layout, but this residual package contains no attached conservative evidence signature. The source fact is recorded for review only and does not approve an import.

- `mild_hybrid_g_140`: `4×2`
- `mild_hybrid_140`: `4×2`
- `hybrid_g_150_4x4`: `4×4 z tylnym silnikiem elektrycznym`
- `hybrid_155`: `4×2`
- Boundary: The third-column continuation is visually part of the drivetrain row; no signature is attached and no projection is created.

### Line 56 — `gearbox`

The complete logical row is legible from the visual page layout, but this residual package contains no attached conservative evidence signature. The source fact is recorded for review only and does not approve an import.

- `mild_hybrid_g_140`: `Manualna`; `6-biegowa`
- `mild_hybrid_140`: `Manualna`; `6-biegowa`
- `hybrid_g_150_4x4`: `Automatyczna`; `dwusprzęgłowa`; `6-biegowa`
- `hybrid_155`: `Automatyczna`; `Multi-mode`; `4+2`
- Boundary: The multi-line gearbox row is visually complete, but no exact compound signature is attached.

### Line 70 — `front_brakes`

The complete logical row is legible from the visual page layout, but this residual package contains no attached conservative evidence signature. The source fact is recorded for review only and does not approve an import.

- `mild_hybrid_g_140`: `Φ296x26`
- `mild_hybrid_140`: `Φ296x26`
- `hybrid_g_150_4x4`: `Φ296x26`
- `hybrid_155`: `Φ296x26`
- Boundary: The diameter and thickness values are visible across all columns, but no attached signature supports approval.

### Line 93 — `homologation_protocol`

The complete logical row is legible from the visual page layout, but this residual package contains no attached conservative evidence signature. The source fact is recorded for review only and does not approve an import.

- `mild_hybrid_g_140`: `WLTP(3)`
- `mild_hybrid_140`: `WLTP(3)`
- `hybrid_g_150_4x4`: `WLTP(3)`
- `hybrid_155`: `WLTP(3)`
- Boundary: The shared protocol label and footnote marker are source context; no signature is attached.

### Line 95 — `eco_mode`

The complete logical row is legible from the visual page layout, but this residual package contains no attached conservative evidence signature. The source fact is recorded for review only and does not approve an import.

- `mild_hybrid_g_140`: `Tak`
- `mild_hybrid_140`: `Tak`
- `hybrid_g_150_4x4`: `Tak`
- `hybrid_155`: `Tak`
- Boundary: The visually shared yes marker spans all four columns but remains review-only without evidence signatures.

## Prior rear-brake decision

Lines 74, 79 and 80 remain context-only fragments. The exact rear-brake evidence decision is preserved in `data/reporting/bigster_technical_page20_ambiguity_review.json` at line 77 (`86e33e875ec789d2158604e3d0d69634b0a600856d47ca16c21be4cfeb2081cc`), with status `covered_by_selected_evidence`.

## Five-package milestone review

The five-package review confirms that the existing authored-review vocabulary, evidence boundaries and no-import policy remain sufficient; the residual queue continues without a separate review-only package.

## Safety boundary

- no file under `data/master` is changed;
- no approved import specification is created or changed;
- all 40 exact candidate IDs, texts, pages and line ranges are preserved;
- zero attached evidence signatures and records remain zero;
- visually legible values are source findings only, not approved observations;
- column headers and wrapped fragments are not promoted to standalone data;
- the prior rear-brake evidence decision is referenced rather than duplicated.

## Next package

**Bigster Technical Page 20 Unresolved Review — Chunk 2** — Review chunk 2 of the remaining 29 unresolved technical candidates from Bigster brochure page 20 without creating master-data rows or approved import specifications.
