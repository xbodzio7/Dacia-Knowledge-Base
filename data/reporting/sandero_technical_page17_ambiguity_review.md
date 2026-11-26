# Sandero Technical Page 17 Ambiguity Review

Authored review of `residual_gap_004`. Decisions preserve row, powertrain and candidate boundaries and do not approve imports.

## Summary

| Measure | Value |
| --- | ---: |
| Reviewed candidates | 5 |
| Covered by selected evidence | 0 |
| Partially covered | 5 |
| Selected evidence signatures | 8 |
| Selected evidence records | 16 |

## Candidate decisions

| Line | Candidate | Decision | Selected signatures | Exact text |
| ---: | --- | --- | ---: | --- |
| 15 | `af8a18cbf33fdcd88948e6aee518dafabcbd161530767a7dfe5af917885ca481` | `partially_covered` | 2 | Maks. moc w kW EWG (KM) |
| 19 | `515189b35b81d62360ad7b68509b7e48fe6d8607f89baa4cd10a4be0fc5478c3` | `partially_covered` | 2 | Maks. moment obrotowy w Nm |
| 82 | `9e24e542a7f69f9b3e053325bb9b606de1c0142e0bb19b3ba882cee4b3d196bf` | `partially_covered` | 2 | Maksymalna masa własna                      1132                        1209                               1232 |
| 84 | `8c95af2d22e4b73b8cce5e064156bcab2a61942c6164133eb0b6652e688d4c1e` | `partially_covered` | 1 | Dopuszczalna masa całkowita |
| 87 | `7d03dc1a0f23d041d391cc4a2e7ff42ad1c1582209a5bc866a24fc6f5d554df2` | `partially_covered` | 1 | Dopuszczalna masa całkowita |

## Partial findings

### Line 15 — `af8a18cbf33fdcd88948e6aee518dafabcbd161530767a7dfe5af917885ca481`

Both attached signatures match the LPG and petrol cells for the Eco-G 120 automatic column. The same values printed for the manual Eco-G column and the 74 kW TCe value have no attached records and are not inferred.
- `engine_power`: `74`, `90`, `84` — The row also prints TCe 100 and manual Eco-G values, but the attached evidence covers only two automatic Eco-G configurations.

### Line 19 — `515189b35b81d62360ad7b68509b7e48fe6d8607f89baa4cd10a4be0fc5478c3`

Both attached signatures match the LPG and petrol torque cells for the Eco-G 120 automatic column. TCe 100 and manual Eco-G cells remain source facts because no matching records are attached to this candidate.
- `engine_torque`: `200`, `197`, `190` — The complete visual row contains TCe 100 and manual Eco-G values beyond the attached automatic-configuration evidence.

### Line 82 — `9e24e542a7f69f9b3e053325bb9b606de1c0142e0bb19b3ba882cee4b3d196bf`

The two attached masses match the manual and automatic Eco-G columns. The visible 1132 kg TCe value has no attached evidence and is not projected to any configuration.
- `maximum_kerb_weight`: `1132` — The TCe column is visible in the source row but is outside the attached evidence set.

### Line 84 — `8c95af2d22e4b73b8cce5e064156bcab2a61942c6164133eb0b6652e688d4c1e`

This first repeated label fragment begins the vehicle-GVW row and therefore selects only the attached 1665 kg gross-vehicle signature. The attached 2765 kg gross-train signature belongs to the following row and is rejected here.
- `gross_vehicle_weight`: `1570`, `1640` — The TCe and manual Eco-G vehicle-GVW values are visible but have no attached signatures for this candidate.

### Line 87 — `7d03dc1a0f23d041d391cc4a2e7ff42ad1c1582209a5bc866a24fc6f5d554df2`

This second repeated label fragment begins the gross-train row and therefore selects only the attached 2765 kg gross-train signature. The attached 1665 kg gross-vehicle signature belongs to the preceding row and is rejected here.
- `gross_train_weight`: `2550`, `2740` — The TCe and manual Eco-G gross-train values are visible but have no attached signatures for this candidate.

## Safety boundary

- no file under `data/master` is changed;
- no approved import specification is created or changed;
- values without attached evidence are retained only as source facts;
- gross-vehicle and gross-train evidence is not exchanged between repeated label fragments;
- selected automatic evidence is not projected onto manual or TCe configurations.

## Next package

**Sandero Stepway Technical Page 17 Ambiguity Review** — Review the 4 ambiguous technical candidates from the Sandero Stepway brochure page 17 against their 12 preserved evidence signatures without creating master-data rows or approved import specifications.
