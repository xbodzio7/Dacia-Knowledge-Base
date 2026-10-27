# Sandero Technical Page 17 Unresolved Review — Chunk 1

Authored review of `residual_gap_026`. The first 40 of 41 candidates are grouped by the visual layout of the Sandero page-17 technical table. Source findings are review-only and do not approve imports.

## Summary

- candidates: 40 of 41 (chunk 1 of 2);
- visual groups: 20;
- `unresolved_signature_mismatch`: 14;
- `context_only_non_import`: 26;
- attached evidence signatures: 0;
- attached evidence records: 0.

## Source boundary

- source: `src_pl_sandero_brochure_20260202`;
- archived file: `PDF/Broszury/DACIA SANDERO broszura 20260202.pdf`;
- SHA-256: `adee5017a405a22dffaca0555b47b84b718f2166534652c9863ba2f97f325f97`;
- page: 17;
- working columns: `100 TCe`, `120 Eco-G` LPG/benzyna and `120 Eco-G auto` LPG/benzyna.

The review preserves the printed `100 TCe` heading together with the printed `74 (120 KM)` power value. It does not normalize either literal. Fuel subcolumns, wrapped power and torque lines, manual/automatic gearbox wording and gear-specific elasticity remain distinct. The missing aligned rpm continuation for the final automatic-petrol torque value is not inferred. The English source literal `to be adjusted according to the country` is retained for CO₂ and consumption.

## Candidate decisions

| # | Line | Candidate | Group | Decision | Exact text |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 5 | `64fe01e2ff8334bdcf514b1fd93c10954aec1384bb289b3e3b1a8078a2844c46` | `powertrain_headers` | `context_only_non_import` |                                           100 TCe                    120 Eco-G                        120 Eco-G auto |
| 2 | 9 | `21e0c23af8a5b2f1fff3e4fdf4665b31c64fb693ea180190507237fd57d19ef5` | `fuel_type` | `context_only_non_import` |                                           Benzyna |
| 3 | 10 | `6a4cdeae840c148680a190a0a2e159c792d2b4b05197ffc4911a1da3a3804987` | `fuel_type` | `unresolved_signature_mismatch` | Rodzaj paliwa                           bezołowiowa      Benzyna bezołowiowa (E10)/LPG       Benzyna bezołowiowa (E10)/LPG |
| 4 | 11 | `8ff1d9893b069ad7f9180ddf8998cac2cdef596e63a70784f75cb8366167bb41` | `fuel_type` | `context_only_non_import` |                                            (E10) |
| 5 | 13 | `798544cdcc5778bcc747fcd63b3fe749cee96847dfefd4e40fa8f842cf561467` | `fuel_subheaders_power` | `context_only_non_import` |                                                               LPG               Benzyna           LPG             Benzyna |
| 6 | 16 | `dd3094091d47637ab098deaf52cdc00e147ae2618a00980c7211e2acfa145891` | `maximum_power` | `unresolved_signature_mismatch` |                                  74 (120 KM) od          90 (120 KM) od     84 (114 KM) od   90 (120 KM) od   84 (114 KM) od |
| 7 | 17 | `e21a10a7b337d089ff2fc019baa2342269cf3101385789767edf2a58eb39fb5a` | `maximum_power` | `unresolved_signature_mismatch` | przy prędkości obrotowej silnika 5000 do 5250             4500 do 5000       4500 do 5750     4500 do 5000     4500 do 5750 |
| 8 | 18 | `0c6b4c077cc32c62ba5e26324478bf704a0ef09d677460e187aa9dbb07369199` | `maximum_power` | `context_only_non_import` | (obr./min) |
| 9 | 20 | `083c5877e13ab29b9f3a90cc5bfc3e375182f40268b06af50744b66e6ee550bc` | `maximum_torque` | `unresolved_signature_mismatch` |                                        200 od 2900 do    197 od 1750 do     190 od 2000 do   197 od 1750 do |
| 10 | 21 | `af0aac2083fae117dc88d135eca76b1bf3ac250b7bd442c1d2fdfeac3ac74c68` | `maximum_torque` | `unresolved_signature_mismatch` | EWG (m·kg) przy prędkości                   3500              3750               4000             3750 |
| 11 | 22 | `67ef3de1c0d67a1c870a6322af827d585dec0cc25168d35308cc471982c10343` | `maximum_torque` | `context_only_non_import` |                                                                                                                     190 |
| 12 | 23 | `57160f2733a46153339324071bb1079875b28e06a967a3bfa71269b255b3e689` | `maximum_torque` | `context_only_non_import` | obrotowej silnika (obr./min) |
| 13 | 24 | `9e0bf727737c967641c21377e3ad2ea86181b6d1a27a163ab222829dea7adec2` | `gearbox` | `context_only_non_import` |                                                                                                                Automatyczna |
| 14 | 25 | `0ea0bd411b2736c3f2150df559184d77469ef0ee404a86633d4ffa38b3e3d473` | `gearbox` | `context_only_non_import` |                                          Manualna                                              Manualna |
| 15 | 26 | `ccf14b33fb4f3f39e813adccc5deae6df49f5b7410e3ff6e076f7790bb40cdb0` | `gearbox` | `unresolved_signature_mismatch` | Typ skrzyni biegów                       6-biegowa |
| 16 | 27 | `81b4e7d90a30f407dc7f7cd16c003288e0d2bc0b80dbbaa8be2a9eff2ab1b710` | `gearbox` | `context_only_non_import` |                                                                Manualna 6-biegowa |
| 17 | 30 | `47a37ceecf885d805d50056912462f854e9a2383548725aa92566cf27c39bf97` | `gearbox` | `context_only_non_import` |                                                                                                               dwusprzęgłowa |
| 18 | 32 | `fbb172ef6cf6c7d965e4cf3b55869a26a30774cb08785a55944261ea588d2f87` | `injection_type` | `context_only_non_import` |                                          Bezpośredni |
| 19 | 33 | `5d148a8d52b44c557090f5876c35e576daf992a3ef97c9bc1cf402f4d91908c9` | `injection_type` | `unresolved_signature_mismatch` | Rodzaj wtrysku paliwa                    z turbodo-    Bezpośredni z turbodoładowaniem Bezpośredni z turbodoładowaniem |
| 20 | 34 | `ae917b78f81271cd9362db36a0bba0779aa647e6482da04d9a5c18c6295ca355` | `injection_type` | `context_only_non_import` |                                          ładowaniem |
| 21 | 38 | `3d87ecda8a05fe881f87814cc818b2fb2152167fc53ddef23aaee26128fa41f0` | `cylinders_valves` | `unresolved_signature_mismatch` | Liczba cylindrów / zaworów                                                        3/12 |
| 22 | 47 | `80a127ae1f8843cbf853f72d0b1a5722d6f74b548394bc2e42703efc940c46eb` | `turning_diameter_fragment` | `context_only_non_import` | krawężnikami |
| 23 | 55 | `61355ba9c260878678e2beaeff04b1c024026d481e3c55bef56f89bae5a8488a` | `fuel_subheaders_performance` | `context_only_non_import` |                                                               LPG               Benzyna           LPG             Benzyna |
| 24 | 59 | `2cdf98f1d00f203b91087b53e6e6b9101d04fb8b470b2236455de7e8d21adddd` | `acceleration_0_100` | `unresolved_signature_mismatch` | 0-100 km/h (s)                               9,7              10,1                11,1            9,8               10,9 |
| 25 | 61 | `67a3ec063cbb48a7d54be9b426f2835457ca78a23e789d881ecca5aad7137897` | `elasticity` | `context_only_non_import` | Elastyczność w zakresie |
| 26 | 62 | `f856e328e34e3ded36c8e2127f5962714575065313ddd1a0df4db91d5df06bdd` | `elasticity` | `context_only_non_import` | średnich prędkości: |
| 27 | 63 | `a50de7fa5b6df1932dd6d2088d8b74c47cdc6338f34449f0ad5ac30d1ef964ef` | `elasticity_fourth_gear` | `unresolved_signature_mismatch` | 80–120 km/h (s)     na 4. biegu              7,4               7,4                 8,4                8             8,9 |
| 28 | 65 | `84979556630e29bd2718cf51fcf621c2a8699447c37376ced92bae78d9886af1` | `elasticity_fifth_gear` | `unresolved_signature_mismatch` |                         na 5. biegu          10,7              11                 11,7                8             8,9 |
| 29 | 68 | `e12775121877e464096dfd995ead68cd4879591fd7342710c002be84647e84d0` | `fuel_subheaders_emissions` | `context_only_non_import` |                                                               LPG               Benzyna           LPG             Benzyna |
| 30 | 70 | `dfff614c6e18046274f01a02db7d530eb4afeb3fa6c61f3591188ca366a294d1` | `test_protocol` | `unresolved_signature_mismatch` | Protokół badania                                                                WLTP(2) |
| 31 | 74 | `c39b4ff5c8327dc9f79fc146d8541c7e39ba10862fc3b79adbff211e6ec6d36b` | `co2_emissions` | `unresolved_signature_mismatch` | Emisja CO2 (g/km)                                              to be adjusted according to the country |
| 32 | 76 | `c758db5547b80b6f6bb43662656c033bb00173ec7c3d4d4b0d1ba8e197824d9c` | `combined_consumption` | `context_only_non_import` | Zużycie paliwa w cyklu |
| 33 | 77 | `c1ad153f48a412e78e0fc3bccc00eaa63209fe1ffed1acb57a4842d45fb6fbb8` | `combined_consumption` | `unresolved_signature_mismatch` |                                                                to be adjusted according to the country |
| 34 | 78 | `2e88193b93f0f77017d616cb309f2a2b4f94e3fd7edc32cffd983abb5f270538` | `combined_consumption` | `context_only_non_import` | mieszanym (l/100 km) |
| 35 | 86 | `08d4f9f8ace3e13fd99a4a2d4919dd0729e9fd0f5de7b1feb36117356fa1ef2d` | `gross_vehicle_mass_fragment` | `context_only_non_import` | (DMC) pojazdu |
| 36 | 89 | `f9a705b1b52f006da49e60022078740d5aab8e81697ba1700f131527afa60c90` | `gross_combination_mass_fragment` | `context_only_non_import` | (DMC) zespołu pojazdów |
| 37 | 90 | `f3ed6de8debf781eefcb0fab4c194a86f72d65c06de7f899782ee9711cf519ea` | `maximum_braked_trailer_fragment` | `context_only_non_import` | Maks. masa całkowita |
| 38 | 98 | `af3e54544b2d97a65d2eed17761bd60c546cd8ce5cdcedbf59b03840c179c36c` | `wltp_footnote` | `context_only_non_import` | badania pojazdów lekkich; ang. Worldwide Harmonized Light Vehicles Test Procedures): nowy protokół, który w porównaniu |
| 39 | 99 | `0b82fb2342372b76c0dd6faa54d708c13a2ac91fb927af2c882f5576313805e1` | `wltp_footnote` | `context_only_non_import` | z protokołem NEDC umożliwia uzyskanie wyników bardziej zbliżonych do wyników obserwowanych w rzeczywistych warunkach |
| 40 | 100 | `e28ad03af279ca5fc1335e7396008bc8fbeedde60e91c54463db33075f19edbc` | `wltp_footnote` | `context_only_non_import` | eksploatacji. Wartości emisji CO2 są homologowane zgodnie ze standardową metodą pomiaru, określoną w obowiązujących |

## Key review-only source findings

- The heading `100 TCe` and power value `74 (120 KM)` are preserved exactly as printed; the review does not reconcile them.
- Fuel: petrol E10 for 100 TCe; petrol E10/LPG for both Eco-G powertrains.
- Maximum power: `74 (120 KM) od 5000 do 5250`; Eco-G LPG `90 (120 KM) od 4500 do 5000`; Eco-G petrol `84 (114 KM) od 4500 do 5750`, with the same LPG/petrol values for automatic.
- Maximum torque: `200 od 2900 do 3500`; LPG `197 od 1750 do 3750`; petrol `190 od 2000 do 4000`; automatic LPG `197 od 1750 do 3750`; automatic petrol prints `190` without an aligned rpm continuation in the reviewed extraction.
- Gearboxes: manual 6-speed for 100 TCe and Eco-G manual; automatic 6-speed dual-clutch for Eco-G auto.
- Injection: direct turbocharging for all three powertrain headings.
- Cylinders/valves: common `3/12`.
- 0–100 km/h: `9,7`, `10,1`, `11,1`, `9,8`, `10,9`.
- 80–120 km/h on 4th: `7,4`, `7,4`, `8,4`, `8`, `8,9`; on 5th: `10,7`, `11`, `11,7`, `8`, `8,9`.
- Protocol: `WLTP(2)`.
- CO₂ and combined consumption retain the literal English source value `to be adjusted according to the country`; no numeric value or translation is substituted.
- Mass value lines and the full trailer label are outside this candidate chunk, so their fragments remain context-only.
- WLTP explanatory text remains source context.

## Safety boundary

- no change under `data/master` or `data/imports`;
- no selected evidence and no automatic promotion;
- no normalization of `100 TCe` or `74 (120 KM)`;
- no inference of the missing automatic-petrol torque rpm;
- no collapse of LPG and petrol subcolumns;
- no numeric substitution for country-dependent CO₂ or consumption;
- incomplete mass rows and explanatory footnotes remain context-only.

## Next package

**Sandero Technical Page 17 Unresolved Review — Chunk 2** (`residual_gap_027`), covering the remaining 1 candidate.
