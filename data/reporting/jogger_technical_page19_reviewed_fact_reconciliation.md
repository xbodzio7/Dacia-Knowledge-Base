# Jogger Technical Page 19 Reviewed Fact Reconciliation

Authored review of `post_residual_jogger_technical_page19_reconciliation_001`. It reconciles 22 complete or semantically recoverable source facts preserved by `residual_gap_002`, `residual_gap_024` and `residual_gap_025` with current exact Jogger values and ranges. This package is review-only.

## Source and scope

- source: `src_pl_jogger_brochure_20251217`;
- file: `PDF/Broszury/DACIA JOGGER broszura 20251217.pdf`;
- SHA-256: `eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6`;
- page: 19;
- reviewed facts: 22;
- current Jogger configurations: 22;
- comparison source: `src_pl_jogger_price_my26_20260401` dated 2026-04-01;
- columns remain separate for TCe 110, Eco-G 120 manual LPG/petrol, Eco-G 120 automatic LPG/petrol and Hybrid 155 combustion/electric context.

## Classification summary

| Primary classification | Facts |
| --- | ---: |
| `existing_coverage` | 10 |
| `import_ready_gap` | 5 |
| `context_model_required` | 2 |
| `deferred_source_conflict` | 5 |

Classification tags overlap: 19 facts have existing coverage, 7 contain an import-ready component, 4 require additional context modeling and 5 contain a deferred official-source or printed-label conflict.

## Fact register

| # | Fact | Source values | Primary | Tags |
| ---: | --- | --- | --- | --- |
| 1 | `energy_source_columns` | tce110: Benzyna / ecog120_manual: LPG, Benzyna / ecog120_automatic: LPG, Benzyna / hybrid155: Benzyna, Elektryczność | `context_model_required` | `existing_coverage`, `context_model_required` |
| 2 | `maximum_power` | tce110: 81 kW / ecog120_lpg: 90 kW / ecog120_petrol: 84 kW / hybrid155_total: 105 kW (140 KM) | `deferred_source_conflict` | `existing_coverage`, `deferred_source_conflict` |
| 3 | `maximum_power_speed` | tce110: 5000-5250 rpm / ecog120_lpg: 4500-5000 rpm / ecog120_petrol: 4500-5000 rpm / hybrid155: 5600 rpm | `deferred_source_conflict` | `existing_coverage`, `import_ready_gap`, `deferred_source_conflict` |
| 4 | `maximum_torque` | tce110: 200 Nm / ecog120_lpg: 197 Nm / ecog120_petrol: 190 Nm / hybrid155: 172 Nm combustion + 205 Nm electric | `existing_coverage` | `existing_coverage` |
| 5 | `maximum_torque_speed` | tce110: 2900-3500 rpm / ecog120_lpg: 1750-3750 rpm / ecog120_petrol: 2000-4000 rpm / hybrid155_combustion: 3000-4000 rpm | `import_ready_gap` | `existing_coverage`, `import_ready_gap` |
| 6 | `gearbox` | tce110: manual / ecog120_manual: manual / ecog120_automatic: dual-clutch automatic / hybrid155: automatic Multi-mode | `existing_coverage` | `existing_coverage` |
| 7 | `injection` | tce110: direct turbo injection / ecog120_lpg: indirect/port injection / ecog120_petrol: direct injection / hybrid155_petrol: indirect/multi-point injection / electric: not applicable | `existing_coverage` | `existing_coverage` |
| 8 | `engine_displacement` | tce110: 999 cm3 / ecog120: 1199 cm3 / hybrid155: 1789 cm3 / electric: - | `existing_coverage` | `existing_coverage` |
| 9 | `cylinders_and_valves` | tce110: 3/12 / ecog120: 3/12 / hybrid155: 4/16 / electric: - | `existing_coverage` | `existing_coverage` |
| 10 | `emission_standard` | all_powertrains: Euro 6e-bis | `existing_coverage` | `existing_coverage` |
| 11 | `front_suspension` | all_configurations: McPherson with lower control arm, coil springs, telescopic hydraulic dampers and stabilizer | `existing_coverage` | `existing_coverage` |
| 12 | `rear_suspension` | all_configurations: torsion beam with coil springs, telescopic hydraulic dampers and stabilizer | `existing_coverage` | `existing_coverage` |
| 13 | `maximum_speed` | all_powertrains: 180 km/h | `existing_coverage` | `existing_coverage` |
| 14 | `acceleration_0_100` | five_seat: TCe 10.5, Eco-G manual LPG 10.9, Eco-G manual petrol 11.9, Eco-G auto LPG 10.4, Eco-G auto petrol 11.4, Hybrid 8.9 / seven_seat: TCe 11.2, Eco-G manual LPG 11.0, Eco-G manual petrol 12.0, Eco-G auto LPG 10.7, Eco-G auto petrol 11.7, Hybrid 9.0 | `import_ready_gap` | `existing_coverage`, `import_ready_gap` |
| 15 | `elasticity_80_120` | five_seat: 11.4, 8.1, 9.1, 8.3, 9.2, 6.4 / seven_seat: 12.3, 8.2, 9.2, 8.7, 9.5, 6.5 | `existing_coverage` | `existing_coverage` |
| 16 | `test_protocol` | all_powertrains: WLTP(2) | `context_model_required` | `context_model_required` |
| 17 | `fuel_and_lpg_capacity` | tce110_petrol: 50 L / ecog120_petrol: 50 L / ecog120_lpg: 50 L total / 40 L usable / hybrid155_petrol: 50 L | `import_ready_gap` | `existing_coverage`, `import_ready_gap` |
| 18 | `minimum_kerb_weight` | five_seat: 1193, 1292, 1326, 1359 / seven_seat: 1221, 1321, 1354, 1388 | `import_ready_gap` | `existing_coverage`, `import_ready_gap` |
| 19 | `maximum_kerb_like_mislabeled_block` | five_seat: 1230, 1312, 1335, 1373 / seven_seat: 1261, 1342, 1364, 1405 | `deferred_source_conflict` | `context_model_required`, `deferred_source_conflict` |
| 20 | `gross_train_like_mislabeled_block` | five_seat: 2885, 2965, 2985, 2830 / seven_seat: 3055, 3140, 3160, 3000 | `deferred_source_conflict` | `context_model_required`, `deferred_source_conflict` |
| 21 | `gross_vehicle_weight` | five_seat: 1685, 1765, 1785, 1830 / seven_seat: 1855, 1940, 1960, 2000 | `import_ready_gap` | `existing_coverage`, `import_ready_gap` |
| 22 | `braked_trailer_weight` | tce110: 1200 kg / ecog120_manual: 1200 kg / ecog120_automatic: 1200 kg / hybrid155: 1200 kg | `deferred_source_conflict` | `existing_coverage`, `import_ready_gap`, `deferred_source_conflict` |

## Safe next import boundary

The next package is limited to the 26 missing brochure-source `acceleration_0_100` observations: 6 petrol observations for current TCe 110 configurations, 12 fuel-specific observations for current Eco-G 120 manual configurations and 8 fuel-specific observations for current Eco-G 120 automatic configurations. The six Hybrid 155 brochure observations already exist and are excluded. All 26 planned values equal the later official-source values, so the package adds provenance without selecting a winner or overwriting an observation.

## Preserved conflicts and context

- Hybrid 155 total system power remains `105 kW` in the brochure versus `116 kW` in the later official source.
- Eco-G petrol maximum-power range remains `4500–5000 rpm` in the brochure versus `4500–5750 rpm` later.
- Hybrid 155 braked-trailer capacity remains `1200 kg` in the brochure versus `1000 kg` later.
- Two mass blocks retain their literal printed DMC headings even though the values follow maximum-kerb and gross-train patterns; no relabeling by magnitude is allowed.
- The seven-column energy-source row and `WLTP(2)` require governed context rather than scalar projection.
- CO₂ and consumption value lines are outside the reviewed candidate blocks and are not reconstructed from adjacent text.

## Policy

- no `data/master/**` changes;
- no approved import specification;
- no automatic promotion;
- current exact values are not overwritten;
- source-specific conflicts remain unresolved;
- printed source labels are not corrected by inference.

## Next package

`post_residual_jogger_page19_acceleration_source_observation_import_001` will add only the 26 missing source-specific acceleration observations described above.
