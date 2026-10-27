# Sandero Stepway Technical Page 17 Unresolved Review — Chunk 1

Authored review of `residual_gap_022`. The first 40 of 49 candidates are grouped by the visual layout of the Sandero Stepway page-17 technical table. Source findings are review-only and do not approve imports.

## Summary

- candidates: 40 of 49 (chunk 1 of 2);
- visual groups: 24;
- `unresolved_signature_mismatch`: 20;
- `context_only_non_import`: 20;
- attached evidence signatures: 0;
- attached evidence records: 0.

## Source boundary

- source: `src_pl_sandero_stepway_brochure_20260202`;
- archived file: `PDF/Broszury/DACIA SANDERO STEPWAY broszura 20260202.pdf`;
- SHA-256: `800e6e6df78e55e9fd3ac270dd5df26447c82830c92ced112ee83c3b44595d48`;
- page: 17;
- columns: `TCe 110`, `120 Eco-G` LPG/benzyna and `120 Eco-G auto` LPG/benzyna.

Fuel subcolumns, wrapped power/torque rows and gear-specific elasticity rows remain distinct. Incomplete steering and mass labels are not promoted.

## Candidate decisions

| # | Line | Candidate | Group | Decision | Exact text |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 5 | `e9c62f8d913414a0fcff9a8e43bb3a68cf61143ea38ea9c9c7d0e76044cb79e5` | `powertrain_headers` | `context_only_non_import` |                                                TCe 110                      120 Eco-G                120 Eco-G auto |
| 2 | 9 | `6dcd007a991c635afa33bf3c282ed5d30dee8cbc435c57ae7be2bafc7fd5ab31` | `fuel_type` | `context_only_non_import` |                                                 Benzyna                   Benzyna                        Benzyna |
| 3 | 10 | `799453d566258519ec38b9830602dadda23ba34248b4f07def543cab0abcb8f3` | `fuel_type` | `unresolved_signature_mismatch` | Rodzaj paliwa                              bezołowiowa (E10)        bezołowiowa (E10)/LPG          bezołowiowa (E10)/LPG |
| 4 | 12 | `4a21dbe7c396b7dc960fcfd8d407043ee43828cdb2c9af3a613fada57d47d2c7` | `fuel_subheaders_power` | `context_only_non_import` |                                                                       LPG              Benzyna       LPG             Benzyna |
| 5 | 14 | `f502e045fa5e378cab6da3f99130ed50cf182a8d790ae73c8b478e9265b41688` | `maximum_power` | `context_only_non_import` | Maks. moc kW EWG (KM) przy |
| 6 | 15 | `db3f3866c114c98b9d0b38eb3e5befaec724ae8d7c056098ad44ed24d41397b9` | `maximum_power` | `unresolved_signature_mismatch` |                                                                   90 od 4500 do 84 od 4500 do 90 od 4500 do 84 od 4500 do |
| 7 | 16 | `931620e2c09c2a86b5ca0afd051e9d729e1d625ff0d6c98fe6cdff0daff89873` | `maximum_power` | `unresolved_signature_mismatch` | prędkości obrotowej silnika                81 od 5000 do 5250 |
| 8 | 18 | `f8b4c05251791557118a4e476b14b71d6188fea3f82f251b9adc3bd7c892172a` | `maximum_power` | `context_only_non_import` | (obr./min) |
| 9 | 19 | `dee835f22970256f5c577cffd529822dc8636dfd0f6f57430490bf6460f9a299` | `maximum_torque` | `unresolved_signature_mismatch` | Maks. moment obrotowy w Nm                                             197                 190        197              190 |
| 10 | 20 | `2261ebc0800f495abbc865c084f1c285e4ffb976c91dcc1deeb01c6dc2557a81` | `maximum_torque` | `unresolved_signature_mismatch` |                                                   200 |
| 11 | 21 | `2f320abecd0598c7b0b278e297dcb9d4c5cc7e43c1beff8d3aa5114f6a471d1b` | `maximum_torque` | `context_only_non_import` | EWG (m·kg) przy prędkości                   od 2900 do 3500 |
| 12 | 22 | `4f993f305a0a0f8b963486301cbdb4572c06601b350563f2a7a304ed0f1799d8` | `maximum_torque` | `context_only_non_import` |                                                                      od 1750             od 2000    od 1750          od 2000 |
| 13 | 23 | `00cfefd8f29920b7339933c216da1ba6bedfd3fa285c7ba196a257209630a315` | `maximum_torque` | `context_only_non_import` | obrotowej silnika (obr./min)                                         do 3750             do 4000    do 3750          do 4000 |
| 14 | 25 | `0273734922840055217f4af55f90541d11309df9ed8cffc2f56c6c63e2d1f4b7` | `gearbox` | `context_only_non_import` |                                                                                                    Automatyczna 6-biegowa |
| 15 | 26 | `52bc438cbae5790a51d6f7f861eef2a6c8a9a7d910afeb30167ed21c5cfb1b69` | `gearbox` | `unresolved_signature_mismatch` | Typ skrzyni biegów                        Manualna 6-biegowa            Manual 6-speed |
| 16 | 27 | `73424a98f687bd81aef0108299d3148eb02722e978ec4e507def84e00c656e48` | `gearbox` | `context_only_non_import` |                                                                                                        dwusprzęgłowa |
| 17 | 29 | `2eb8273647dee9c2871bda837eb59ed82440ea8adc6d593786ffa97ea1829c82` | `injection_type` | `context_only_non_import` |                                                Bezpośredni |
| 18 | 30 | `dd4a902ade7202fca8f9ebd69299970e5f8aef0755de23ce689cc6201ca77027` | `injection_type` | `unresolved_signature_mismatch` | Rodzaj wtrysku paliwa                     z turbodoładowaniem |
| 19 | 31 | `87406586fce74b615f827facc15054d0be6ed2fdf0df8ebca0a093ac019ec124` | `injection_type` | `unresolved_signature_mismatch` |                                                                     Pośredni       Bezpośredni     Pośredni      Bezpośredni |
| 20 | 33 | `b892bc195d6021a5b4f03b52ef8213c0c624a7b489a4e322e4a1e7e5323dd0b6` | `engine_displacement` | `unresolved_signature_mismatch` | Pojemność skokowa (cm3)                           999                          1199                           1199 |
| 21 | 35 | `fa541d69f6221c0bafa52bf2a672dbb114d71b38653f1843e0401715a2f5ed21` | `cylinders_valves` | `unresolved_signature_mismatch` | Liczba cylindrów / zaworów                                                      3/12 |
| 22 | 37 | `376a35a7afe33fb53894ae27708c50d42af44c39a3e753330eb035efb1b58c59` | `emissions_standard` | `unresolved_signature_mismatch` | Norma emisji spalin                                                          Euro 6e bis |
| 23 | 44 | `24f0180ffb7db87cf67d4b386b297aa8039d895eb0e99ff16edcabccb5991732` | `turning_diameter_fragment` | `context_only_non_import` | krawężnikami (m) |
| 24 | 52 | `361e62c276742d03f18dfeb3ca4014753f4094c618dd9c8d84a318264370bc02` | `fuel_subheaders_performance` | `context_only_non_import` |                                                                       LPG              Benzyna       LPG             Benzyna |
| 25 | 54 | `d381ebdd2b4ef7f961b8f79ab810bd12075b25eb0697725b2c0410fa2461020f` | `maximum_speed` | `unresolved_signature_mismatch` | Prędkość maksymalna (km/h)                        180                  180                180        180               180 |
| 26 | 56 | `81107e1204768a98d26d7fd79715646400aa1a2fd450cb310921d0f98a3b846a` | `acceleration_0_100` | `unresolved_signature_mismatch` | 0–100 km/h (s)                                     10                 10,4                11,4        10               11 |
| 27 | 58 | `f1dfd7be22671a0da5b6731650e512204bbb138c37b67ead920b00c4699fe1fc` | `elasticity_fourth_gear` | `context_only_non_import` | Elastyczność w zakresie |
| 28 | 59 | `5feaabe7633da4c858cc239ec6932563310cf4f6c9c66b1f5b22dddd103b3903` | `elasticity_fourth_gear` | `unresolved_signature_mismatch` | średnich prędkości:                               7,7                   8                  9          8,3              9,1 |
| 29 | 60 | `6ae74e0fa2ac524929217b5d575751cc3da44588163489b1792d75a92fa6b72f` | `elasticity_fourth_gear` | `context_only_non_import` | 80–120 km/h (s)     na 4. biegu |
| 30 | 61 | `15d4fe098ac1bbc01000556e2695eba277ca7efa8ef8ee9b18627942226277f9` | `elasticity_fifth_gear` | `unresolved_signature_mismatch` |                          na 5. biegu              10,7                 12                 12,6 |
| 31 | 63 | `62b288f08bbfa685193b8dda9b2034800ff1ceb82c98e18b995285a852304a9e` | `elasticity_sixth_gear` | `unresolved_signature_mismatch` |                          na 6. biegu              17,1                 18                  19 |
| 32 | 66 | `44a19ab833ffad0e9a60a6407eb312a5e96948f98c359b014458e11057c3da88` | `fuel_subheaders_emissions` | `context_only_non_import` |                                                                       LPG              Benzyna       LPG             Benzyna |
| 33 | 68 | `c1f72118dcc32e4ae17d3e6b54e9b3a1a4defa8f7fb7fda0fc266c888b040790` | `test_protocol` | `unresolved_signature_mismatch` | Protokół badania                                                               WLTP(2) |
| 34 | 70 | `a7c9083b48d7efd392a753269153e5e1764ed9232c148da761595ff0ae9813c2` | `fuel_tank_capacity` | `unresolved_signature_mismatch` | Pojemność zbiornika paliwa (l)                                                   50 |
| 35 | 72 | `78480a2f780b1b1e1123d2a7772193522d28d7a1433817352c29d32be0c1d922` | `co2_emissions` | `unresolved_signature_mismatch` | Emisja CO2 (g/km)                               125/125                      131/140                108/109          122/122 |
| 36 | 74 | `1b60cd38687c58c2da1b2c3fc8053045e3ab126aabe7a62e24eb4a4d2679d936` | `combined_consumption` | `context_only_non_import` | Zużycie paliwa w cyklu |
| 37 | 75 | `93c0a746c86e29ae5a15e650212a3babf9011fc4a5d06c0e0445cc50703bff65` | `combined_consumption` | `unresolved_signature_mismatch` |                                                  5,5/5,5                       5,8/6,2              6,7/6,7          5,4/5,4 |
| 38 | 76 | `bd28ef8b14248ae28d295cc800fa81576674953136da490421890b159361e3c2` | `combined_consumption` | `context_only_non_import` | mieszanym (l/100 km) |
| 39 | 78 | `99ce09ff86dc0832166666aa32742e0b68a5264c3abaaa72b59d8886bad49841` | `minimum_ready_mass_fragment` | `context_only_non_import` | Minimalna masa pojazdu |
| 40 | 84 | `d7ef81bbfcea775f31f3e329cee92e1f47b87a6eeb85a123eb8dc0854d02dccd` | `gross_combination_mass_fragment` | `context_only_non_import` | Dopuszczalna masa całkowita |

## Review-only source findings

- Fuel: TCe 110 petrol E10; Eco-G manual and automatic petrol E10/LPG with separate LPG and petrol columns.
- Maximum power: `81 od 5000 do 5250`; Eco-G manual and automatic `90` on LPG and `84` on petrol, all `od 4500 do 5000`.
- Maximum torque: TCe `200 od 2900 do 3500`; Eco-G LPG `197 od 1750 do 3750`; Eco-G petrol `190 od 2000 do 4000`, for both gearboxes.
- Gearboxes: TCe manual 6-speed, Eco-G manual 6-speed and Eco-G auto automatic 6-speed dual-clutch.
- Injection: TCe direct with turbocharging; Eco-G indirect on LPG and direct on petrol.
- Displacement: `999`, `1199`, `1199`; cylinders/valves `3/12`; emissions standard `Euro 6e bis`.
- Maximum speed: `180` in all five working columns; 0–100 km/h: `10`, `10,4`, `11,4`, `10`, `11`.
- 80–120 km/h on 4th gear: `7,7`, `8`, `9`, `8,3`, `9,1`; on 5th: `10,7`, `12`, `12,6` for the manual columns; on 6th: `17,1`, `18`, `19` for the manual columns. Blank automatic cells are not projected.
- Protocol `WLTP(2)` and fuel tank `50`; CO₂ and consumption values retain their printed fuel-column order.
- The turning-diameter and mass candidates are incomplete fragments in this chunk and remain context-only.

## Safety boundary

- no change under `data/master` or `data/imports`;
- no selected evidence and no automatic promotion;
- no collapse of LPG and petrol subcolumns;
- no projection of manual-gear elasticity values onto the automatic configuration;
- incomplete steering and mass rows remain context-only;
- source findings are review notes, not approved observations.

## Next package

**Sandero Stepway Technical Page 17 Unresolved Review — Chunk 2** (`residual_gap_023`), covering the remaining 9 candidates.
