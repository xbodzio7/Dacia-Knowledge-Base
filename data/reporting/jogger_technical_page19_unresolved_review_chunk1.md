# Jogger Technical Page 19 Unresolved Review — Chunk 1

Authored review of `residual_gap_024`. The first 40 of 43 candidates are grouped by the visual layout of the Jogger page-19 technical table. Source findings are review-only and do not approve imports.

## Summary

- candidates: 40 of 43 (chunk 1 of 2);
- visual groups: 22;
- `unresolved_signature_mismatch`: 10;
- `context_only_non_import`: 30;
- attached evidence signatures: 0;
- attached evidence records: 0.

## Source boundary

- source: `src_pl_jogger_brochure_20251217`;
- archived file: `PDF/Broszury/DACIA JOGGER broszura 20251217.pdf`;
- SHA-256: `eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6`;
- page: 19;
- working columns: TCe 110; Eco-G 120 LPG/benzyna; Eco-G 120 auto LPG/benzyna; hybrid 155 benzyna/elektryczność.

Fuel and energy subcolumns, hybrid combustion/electric values and wrapped rows remain distinct. Candidates whose numeric value lines are absent from this chunk remain context-only. The three visually distinct DMC-labelled blocks are preserved exactly as printed and are not corrected by expected value magnitude.

## Candidate decisions

| # | Line | Candidate | Group | Decision | Exact text |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 5 | `e933c1027e224c482b4fdab447f1b9b70af91b4dc333dfc22feb7fd2ea069411` | `powertrain_headers` | `context_only_non_import` |                                            TCe 110            Eco-G 120                 Eco-G 120 auto              hybrid 155 |
| 2 | 9 | `95d90aec8d995dfd59401a3fbb71ca85f0673ede84eef7de9e640413d73af55e` | `energy_source` | `unresolved_signature_mismatch` | Źródło energii                              Benzyna         LPG           Benzyna        LPG           Benzyna    Benzyna Elektryczność |
| 3 | 13 | `e3cffd30430d5552f0c066200536b494f39846930eb377dac56a91d4a51a3422` | `maximum_power_incomplete` | `context_only_non_import` |                                             od 5000       od 4500         od 4500      od 4500         od 4500 |
| 4 | 14 | `7be654c13ae3318c11ced57245e85ceb0a8b6c86de4c778777ceca249d9a710a` | `maximum_power_incomplete` | `context_only_non_import` | prędkości obrotowej silnika (obr./min)                                                                              przy 5600; łącznie |
| 5 | 15 | `1259c3c58b9fa1ec799c766aea779a32acaf867dcb5c90db805da6a6c28007cf` | `maximum_power_incomplete` | `context_only_non_import` |                                             do 5250       do 5000         do 5000      do 5000         do 5000 |
| 6 | 17 | `4d77081fc4ea0fc2abc53ab436dc65d4f71372ae161c8f6fbdc9463c8a4ee158` | `maximum_torque` | `unresolved_signature_mismatch` | Maks. moment obrotowy w Nm EWG                200           197             190          197             190      172 (silnik spalinowy) |
| 7 | 18 | `d6a2ec4ae615fbd67b1bb83048a45a23a10f081abd56e0e19bceb04cf8ae9ef0` | `maximum_torque` | `context_only_non_import` | (m·kg) przy prędkości obrotowej             od 2900       od 1750         od 2000      od 1750         od 2000    od 3000 do 4000 + 205 |
| 8 | 19 | `cf0b407531fecb4617a7e952aead8d814cab42736323d0f2a27ae8aa9c7074aa` | `maximum_torque` | `context_only_non_import` | silnika (obr./min.)                         do 3500       do 3750         do 4000      do 3750         do 4000     (silnik elektryczny) |
| 9 | 21 | `d99ff5a70d93d1a8e10e344e9bcaefd84f1a30d7c55d99f21ef1f39381c2c3fc` | `gearbox` | `context_only_non_import` |                                                                                          Dwusprzęgłowa               Automatyczna |
| 10 | 22 | `0098f9f1a06a745a5867378566389b5f59ad68a2c2f0fdcf1ba8d41123c5cfc0` | `gearbox` | `unresolved_signature_mismatch` | Typ skrzyni biegów                         Manualna            Manualna |
| 11 | 23 | `4e219b9474ab7db78d143e5d42cd2f830743ebdd483dfe303c7a3e0c948cd32a` | `gearbox` | `context_only_non_import` |                                                                                           automatyczna                Multimode |
| 12 | 25 | `04ae192a99332b8afb9b36fb3a5f9f2b6d6168c60f307ec8042d0d50bb7261ca` | `injection_type` | `context_only_non_import` |                                           Bezpośredni |
| 13 | 26 | `f00e0fd2b0340be59ff080d9b4b7edbb8656ac83450bc7470ecf56486875ac1f` | `injection_type` | `context_only_non_import` |                                                                             Bez-                         Bez- |
| 14 | 27 | `19c5c28fec4597e5fa7854490ab154e902093214010135090ce6a7424f22e84e` | `injection_type` | `unresolved_signature_mismatch` | Rodzaj wtrysku paliwa                     z turbodoła-    Pośredni                     Pośredni                   Pośredni          - |
| 15 | 28 | `7daa210a847c43ac9c5c71dfba491e68880e50d77b47976b9d0e3604eecb8619` | `injection_type` | `context_only_non_import` |                                                                           pośredni                     pośredni |
| 16 | 29 | `bd34f4195b9d0f16fd5c34ee8f0d989e5c92ef762641d8c4007f4a5cb070cc6f` | `injection_type` | `context_only_non_import` |                                            dowaniem |
| 17 | 31 | `4b00db3ce29d823c561e8e35d3a748d46e97d422fc1a65826b65889fce57c0d1` | `engine_displacement` | `unresolved_signature_mismatch` | Pojemność skokowa (cm3)                       999                    1199                         1199             1789             - |
| 18 | 33 | `e8ef1f3568a4bcf65b33bf378dd42e6b2027c7d529edf5cb28751591801d2795` | `cylinders_valves` | `unresolved_signature_mismatch` | Liczba cylindrów / zaworów                    3/12                   3/12                         3/12              4/16            - |
| 19 | 35 | `ba75ef9804b84ed34dfd015a80e62eae458a43f9289b66b16947850349e3acd9` | `emissions_standard` | `unresolved_signature_mismatch` | Norma emisji spalin                                                                Euro 6e bis |
| 20 | 55 | `54353ff5bd094740b35b704abdd1275bfce14ec0dde561a7a95f5e5f4bffd7ce` | `rear_suspension_continuation` | `context_only_non_import` |                                                                            i stabilizatorem |
| 21 | 58 | `b6cc35d701c59a36b722304a845da4c8788452ed8b43d861c11120ae870a6918` | `maximum_speed` | `unresolved_signature_mismatch` | Prędkość maksymalna (km/h)                                                            180 |
| 22 | 64 | `68b565410f123cf8f6c0c10b5edbdffe7005eb3deca524ce772982ed7b395483` | `elasticity_incomplete` | `context_only_non_import` | Elastyczność w zakresie średnich |
| 23 | 65 | `c01b0a806af674cb8d2ac37c8408eafa5b9722fa9d83e55f2bf0ad8211494f34` | `elasticity_incomplete` | `context_only_non_import` | prędkości: od 80 do 120 km/h (s) na |
| 24 | 66 | `a0cbb98f25343b869652c76e194350f7ee9bfb6cd2c5bcf0830e9cdc0d0fa411` | `elasticity_incomplete` | `context_only_non_import` | IV biegu |
| 25 | 71 | `4a4d1197a7bb872329e208979656163b8c363b27aa2168e2715caedc4f92a715` | `test_protocol` | `unresolved_signature_mismatch` | Protokół badania                                                                     WLTP(2) |
| 26 | 73 | `449ebef1f7e48ab9cf921cfbe57e7ff89db25e4e6573c6bd9047ee2ec455756f` | `fuel_tank_capacity` | `unresolved_signature_mismatch` | Pojemność zbiornika paliwa (l)                 50         50/40(3)          50         50/40(3)          50                  50 |
| 27 | 75 | `18a08a000ceb2a5a97d73c0d4b4cc62b2bad87d42e502bc9635cd3066f85a032` | `co2_label_without_values` | `context_only_non_import` | Emisja CO2 (g/km) |
| 28 | 77 | `7656253675128314b32f3529748a6a29350d5fad73e096df3ccba956615e35cb` | `combined_consumption_without_values` | `context_only_non_import` | Zużycie paliwa w cyklu mieszanym |
| 29 | 78 | `b2a67f10837685761f2681fc78e316b7469af319b48b4ee4d682e65c1d3bd178` | `combined_consumption_without_values` | `context_only_non_import` | (l/100 km) |
| 30 | 81 | `2123bad9ab4724915736cafdbe56f76e2f26a097af5f7ef862fe4206cbc506d9` | `minimum_mass_label_without_values` | `context_only_non_import` | Minimalna masa własna |
| 31 | 85 | `1eb0230e8dc766eb55a75a574cbb68d410deefe870b091e2e9a16800c438173f` | `first_dmc_label_without_values` | `context_only_non_import` | Dopuszczalna masa całkowita (DMC) |
| 32 | 86 | `9af058b71b256f7d5e4e1a17e6c63fca1fe4cedfb678026d23b3191012f75d2e` | `first_dmc_label_without_values` | `context_only_non_import` | zespołu pojazdów |
| 33 | 90 | `39f3a7664edffcbc874e3b3267b8a72a8a0d43f1d15aec33c0cc34454fec3c7c` | `second_dmc_label_without_values` | `context_only_non_import` | Dopuszczalna masa całkowita (DMC) |
| 34 | 91 | `bd5e9fa30dce1c9abec159d54d032e8e6e83738fbecbd90966fd6ca453c0bc88` | `second_dmc_label_without_values` | `context_only_non_import` | pojazdu |
| 35 | 95 | `51215c0872640938ac68872bd126cdca1972411105ae11a310b4849659d15ac1` | `third_dmc_label_without_values` | `context_only_non_import` | Dopuszczalna masa całkowita (DMC) |
| 36 | 96 | `c68ad49c6ed593ece31c5e31405ad3be416b692990b001a8fc7909c67a585c2e` | `third_dmc_label_without_values` | `context_only_non_import` | pojazdu |
| 37 | 100 | `eb65fa5a7b33603a6826795ab8803fd7d41558a60a8c51b108d9907319f81b31` | `maximum_braked_trailer_label_without_values` | `context_only_non_import` | Maks. masa całkowita przyczepy |
| 38 | 101 | `7becbe1a9a7966350a8fb8e497fc942862caff0a7bc7e3cb8a84c696400988c8` | `maximum_braked_trailer_label_without_values` | `context_only_non_import` | hamowanej |
| 39 | 109 | `3393d228038e184e79985c92f7fc5493cb0b4c9de002d60bed9bf7f6e0499426` | `wltp_footnote_continuation` | `context_only_non_import` | badania pojazdów lekkich; ang. Worldwide Harmonized Light Vehicles Test Procedures): nowy protokół, który w porównaniu |
| 40 | 110 | `d49cd07f64d84d450fc779908a635088e7e73130ce4d257c4ca461d4a2585718` | `wltp_footnote_continuation` | `context_only_non_import` | z protokołem NEDC umożliwia uzyskanie wyników bardziej zbliżonych do wyników obserwowanych w rzeczywistych warunkach |

## Key review-only source findings

- Energy columns remain separate for TCe petrol, Eco-G LPG/petrol, Eco-G auto LPG/petrol and hybrid petrol/electricity.
- Maximum power is visually complete on the page, but its anchor/value line is outside this residual chunk; candidates 3–5 remain context-only.
- Maximum torque preserves combustion and electric hybrid values separately: `172` at `3000–4000` plus `205` electric.
- Gearboxes remain manual, dual-clutch automatic and automatic Multi-mode as printed.
- Injection retains direct turbo, LPG indirect, petrol direct, hybrid petrol indirect and electric `-` states.
- Displacement and cylinder rows retain the electric `-` column rather than copying combustion values.
- Maximum speed is a common `180` row.
- Elasticity values and five-/seven-seat subrows are visible on the source page but their numeric lines are outside this candidate chunk, so all three label fragments remain context-only.
- The CO₂ and combined-consumption rows contain no printed numeric values in the reviewed page table; labels are not converted into empty or inferred observations.
- Mass values are printed in five- and seven-seat subrows. Because candidate value lines are absent, the label fragments remain context-only. Three visually separate DMC-labelled blocks are preserved literally, including the repeated `DMC pojazdu` wording, without semantic correction based on magnitude.
- Maximum braked-trailer values and WLTP footnote continuations remain review context only.

## Safety boundary

- no change under `data/master` or `data/imports`;
- no selected evidence and no automatic promotion;
- no collapse of fuel, energy, combustion or electric columns;
- no promotion of source-page values whose candidate value lines are absent;
- no inferred CO₂ or consumption values;
- no correction or relabeling of printed DMC rows;
- explanatory footnotes remain context only.

## Next package

**Jogger Technical Page 19 Unresolved Review — Chunk 2** (`residual_gap_025`), covering the remaining 3 candidates.
