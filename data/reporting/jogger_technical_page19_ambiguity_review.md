# Jogger Technical Page 19 Ambiguity Review

Authored review of `residual_gap_002`. Decisions preserve the source page and do not approve imports.

## Summary

| Measure | Value |
| --- | ---: |
| Reviewed candidates | 16 |
| Covered by selected evidence | 1 |
| Partially covered | 2 |
| Context-only non-import | 0 |
| Deferred source conflict | 7 |
| Unresolved signature mismatch | 6 |
| Selected evidence signatures | 3 |
| Selected evidence records | 28 |

## Candidate decisions

| Line | Candidate | Decision | Selected signatures | Exact text |
| ---: | --- | --- | ---: | --- |
| 12 | `91156aecc0c5e1c4f3c907a8d7bed4a6e48cc8ebd1b6c53a36b4ead6c5a737c3` | `deferred_source_conflict` | 0 | Maks. moc kW EWG (KM) przy                                                                                              105 (140) |
| 51 | `af25bb2ab9eafa6499e0439b643700e4476f3b0e64ffc6c5bd86c6d038bd099f` | `covered_by_selected_evidence` | 1 |                                                            amortyzatorami hydraulicznymi i stabilizatorem |
| 61 | `87f2256211644e68452882048c3c195bc6f8131db92038884e9f9aef4faf2281` | `partially_covered` | 1 |                     Wersja 5-miejscowa        10,5          10,9            11,9         10,4            11,4                8,9 |
| 62 | `dc6fdb0c6ad6ccde3275ec5df42e1cdaf1cbaa606b12d339b2234fff2417f238` | `partially_covered` | 1 |                     Wersja 7-miejscowa        11,2           11              12          10,7            11,7                 9 |
| 67 | `a9cbecb27287715ea402b4ae8ba2754e10b0b994bea11d48e2eae3c2051d56e5` | `unresolved_signature_mismatch` | 0 |                   Wersja 5-miejscowa          11,4          8,1             9,1          8,3             9,2                 6,4 |
| 68 | `3e57e1eae5d0f58acf0756a50ff74047cc45c30cd1efe0729d8be2f920ae1315` | `unresolved_signature_mismatch` | 0 |                   Wersja 7-miejscowa          12,3          8,2             9,2          8,7             9,5                 6,5 |
| 82 | `123c5c41b995919ac7aa0157fc195514ecc93df2bf1b15268051b8e60a3504ac` | `unresolved_signature_mismatch` | 0 |                Wersja 5-miejscowa             1193                   1292                         1326                       1359 |
| 83 | `b9aeb4aed7119c4e5920f29463cdb73908d18d5f9b2fdc9afee2ddec407ecefe` | `unresolved_signature_mismatch` | 0 |                Wersja 7-miejscowa             1221                   1321                         1354                       1388 |
| 87 | `72df9514c775a1e00171477bb61d20407e9c34a1b2bf2c4366e9f7e8e6211982` | `deferred_source_conflict` | 0 |                 Wersja 5-miejscowa            1230                   1312                         1335                       1373 |
| 88 | `f09c7f9f12583734f27b8282f460661317f2e04fead563099253d13097999b41` | `deferred_source_conflict` | 0 |                 Wersja 7-miejscowa            1261                   1342                         1364                       1405 |
| 92 | `a97212de9458f15c537f77ea07a2c876fa82108c54cca5ab727d3f68c0030155` | `deferred_source_conflict` | 0 |                Wersja 5-miejscowa             2885                   2965                         2985                       2830 |
| 93 | `259cb9881353399e4f854a0ec9ec976c633835640dad94f92a36975ba3934a08` | `deferred_source_conflict` | 0 |                Wersja 7-miejscowa             3055                   3140                         3160                       3000 |
| 97 | `4fac5cebdeae28892c2ee77ced0abb3bd59006918fef0462f69b1b8dd0e6999e` | `unresolved_signature_mismatch` | 0 |                Wersja 5-miejscowa             1685                   1765                         1785                       1830 |
| 98 | `a140b4a368f27e1b1b815bb6c70c80635bad3e0cbbcdaaa3442bde6450e0dd94` | `unresolved_signature_mismatch` | 0 |                Wersja 7-miejscowa             1855                   1940                         1960                       2000 |
| 102 | `371081416255a70abb7008af66e06bd9284fa208d6d2f3bea1685203eaf2ecc0` | `deferred_source_conflict` | 0 |                 Wersja 5-miejscowa            1200                   1200                         1200                       1200 |
| 103 | `6cf0cdad93218297dd60fd7d35499aa3c252987c7a867dbac1b9bbd2067904ed` | `deferred_source_conflict` | 0 |                 Wersja 7-miejscowa            1200                   1200                         1200                       1200 |

## Residual authored findings

### Line 12 — `91156aecc0c5e1c4f3c907a8d7bed4a6e48cc8ebd1b6c53a36b4ead6c5a737c3`

The row states 105 kW total Hybrid 155 output, every attached signature is max-power engine speed, and the later official MY26 source states 116 kW. The conflict remains non-importable.
- `hybrid_system_power_total`: `105` — The older brochure value conflicts with the later official 116 kW observation and has no attached power signature.

### Line 61 — `87f2256211644e68452882048c3c195bc6f8131db92038884e9f9aef4faf2281`

Only the attached 8.9-second signature belongs to this five-seat row; 9 seconds belongs to the seven-seat row.
- `acceleration_0_100`: `10.5`, `10.9`, `11.9`, `10.4`, `11.4` — Visible five-seat values without signatures attached to this candidate.

### Line 62 — `dc6fdb0c6ad6ccde3275ec5df42e1cdaf1cbaa606b12d339b2234fff2417f238`

Only the attached 9-second signature belongs to this seven-seat row; 8.9 seconds belongs to the five-seat row.
- `acceleration_0_100`: `11.2`, `11`, `12`, `10.7`, `11.7` — Visible seven-seat values without signatures attached to this candidate.

### Line 67 — `a9cbecb27287715ea402b4ae8ba2754e10b0b994bea11d48e2eae3c2051d56e5`

The row is 80–120 km/h elasticity, but both attached signatures are 0–100 km/h acceleration.
- `elasticity_80_120`: `11.4`, `8.1`, `9.1`, `8.3`, `9.2`, `6.4` — No matching elasticity signature is attached.

### Line 68 — `3e57e1eae5d0f58acf0756a50ff74047cc45c30cd1efe0729d8be2f920ae1315`

The row is 80–120 km/h elasticity, but both attached signatures are 0–100 km/h acceleration.
- `elasticity_80_120`: `12.3`, `8.2`, `9.2`, `8.7`, `9.5`, `6.5` — No matching elasticity signature is attached.

### Line 82 — `123c5c41b995919ac7aa0157fc195514ecc93df2bf1b15268051b8e60a3504ac`

The row is five-seat minimum kerb mass, but both attached signatures are acceleration.
- `minimum_kerb_weight`: `1193`, `1292`, `1326`, `1359` — No matching mass signature is attached.

### Line 83 — `b9aeb4aed7119c4e5920f29463cdb73908d18d5f9b2fdc9afee2ddec407ecefe`

The row is seven-seat minimum kerb mass, but both attached signatures are acceleration.
- `minimum_kerb_weight`: `1221`, `1321`, `1354`, `1388` — No matching mass signature is attached.

### Line 87 — `72df9514c775a1e00171477bb61d20407e9c34a1b2bf2c4366e9f7e8e6211982`

The printed gross-train label conflicts with values below gross vehicle weight that follow a maximum-kerb-mass pattern; attached acceleration signatures are rejected.
- `maximum_kerb_weight`: `1230`, `1312`, `1335`, `1373` — Likely five-seat maximum kerb masses, but the source label conflicts; no import meaning is approved.

### Line 88 — `f09c7f9f12583734f27b8282f460661317f2e04fead563099253d13097999b41`

The printed gross-train label conflicts with values below gross vehicle weight that follow a maximum-kerb-mass pattern; attached acceleration signatures are rejected.
- `maximum_kerb_weight`: `1261`, `1342`, `1364`, `1405` — Likely seven-seat maximum kerb masses, but the source label conflicts; no import meaning is approved.

### Line 92 — `a97212de9458f15c537f77ea07a2c876fa82108c54cca5ab727d3f68c0030155`

The printed gross-vehicle label conflicts with values equal to gross vehicle plus braked trailer, the gross-train pattern; attached acceleration signatures are rejected.
- `gross_train_weight`: `2885`, `2965`, `2985`, `2830` — Numerically five-seat gross train weights, but the printed label conflicts.

### Line 93 — `259cb9881353399e4f854a0ec9ec976c633835640dad94f92a36975ba3934a08`

The printed gross-vehicle label conflicts with values equal to gross vehicle plus braked trailer, the gross-train pattern; attached acceleration signatures are rejected.
- `gross_train_weight`: `3055`, `3140`, `3160`, `3000` — Numerically seven-seat gross train weights, but the printed label conflicts.

### Line 97 — `4fac5cebdeae28892c2ee77ced0abb3bd59006918fef0462f69b1b8dd0e6999e`

The row is five-seat gross vehicle weight, but both attached signatures are acceleration.
- `gross_vehicle_weight`: `1685`, `1765`, `1785`, `1830` — No matching mass signature is attached.

### Line 98 — `a140b4a368f27e1b1b815bb6c70c80635bad3e0cbbcdaaa3442bde6450e0dd94`

The row is seven-seat gross vehicle weight, but both attached signatures are acceleration.
- `gross_vehicle_weight`: `1855`, `1940`, `1960`, `2000` — No matching mass signature is attached.

### Line 102 — `371081416255a70abb7008af66e06bd9284fa208d6d2f3bea1685203eaf2ecc0`

The older brochure assigns 1200 kg to Hybrid 155, while the later official source assigns 1000 kg; attached acceleration signatures are rejected.
- `braked_trailer_weight`: `1200`, `1200`, `1200`, `1200` — The Hybrid 155 value conflicts with the later official 1000 kg observation.

### Line 103 — `6cf0cdad93218297dd60fd7d35499aa3c252987c7a867dbac1b9bbd2067904ed`

The older brochure assigns 1200 kg to Hybrid 155, while the later official source assigns 1000 kg; attached acceleration signatures are rejected.
- `braked_trailer_weight`: `1200`, `1200`, `1200`, `1200` — The Hybrid 155 value conflicts with the later official 1000 kg observation.

## Safety boundary

- no file under `data/master` is changed;
- no approved import specification is created or changed;
- no mismatched signature is substituted across attributes;
- contradictory Jogger mass labels and superseded Hybrid 155 values remain explicitly deferred.

## Next package

**Duster Mini Technical Page 20 Ambiguity Review** — Review the 5 ambiguous technical candidates from the Duster mini-brochure page 20 against their 26 preserved evidence signatures without creating master-data rows or approved import specifications.
