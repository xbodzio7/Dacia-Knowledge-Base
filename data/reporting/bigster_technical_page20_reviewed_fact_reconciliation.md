# Bigster Technical Page 20 Reviewed Fact Reconciliation

Authored review of `post_residual_bigster_technical_page20_reconciliation_001`. It reconciles the 24 complete visual source facts preserved by `residual_gap_016` and `residual_gap_017` with current exact Bigster configuration values and ranges. This package is review-only.

## Source and scope

- source: `src_pl_bigster_brochure_20251210`;
- file: `PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf`;
- SHA-256: `76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74`;
- page: 20;
- reviewed facts: 24;
- current Bigster configurations: 14;
- columns: mild hybrid-G 140, mild hybrid 140, hybrid-G 150 4x4, hybrid 155.

## Classification summary

| Primary classification | Facts |
| --- | ---: |
| `existing_coverage` | 8 |
| `import_ready_gap` | 3 |
| `context_model_required` | 3 |
| `deferred_source_conflict` | 10 |

Classification tags overlap: 21 facts have existing coverage, 6 have an import-ready component, 6 need additional context modeling and 11 contain a deferred official-source conflict.

## Fact register

| # | Attribute | Source values by powertrain | Primary | Tags |
| ---: | --- | --- | --- | --- |
| 1 | `propulsion_system` | G140: Benzyna; LPG; Elektryczny mild hybrid 48 V / M140: Benzyna; Elektryczny mild hybrid 48 V / G150 4x4: Benzyna; LPG; Elektryczny mild hybrid 48 V / H155: Benzyna; Elektryczny full hybrid 280 V | `context_model_required` | `existing_coverage`, `context_model_required`, `deferred_source_conflict` |
| 2 | `maximum_power` | G140: 103 kW (140 KM) przy 5500 obr./min / M140: 103 kW (140 KM) przy 5500 obr./min / G150 4x4: 103 kW (140 KM) przy 4500 obr./min – silnik spalinowy; 113 kW (150 KM) – moc łączna / H155: 116 kW (155 KM) przy 5300 obr./min | `deferred_source_conflict` | `existing_coverage`, `import_ready_gap`, `deferred_source_conflict` |
| 3 | `maximum_torque` | G140: 230 N.m przy 2100 obr./min / M140: 230 N.m przy 2100 obr./min / G150 4x4: 230 N.m przy 4000 obr./min – silnik spalinowy; 87 N.m przy 1630 obr./min – elektryczny / H155: 172 N.m przy 3000 obr./min – silnik spalinowy; 205 N.m przy 0–1630 obr./min – elektryczny | `deferred_source_conflict` | `existing_coverage`, `import_ready_gap`, `context_model_required`, `deferred_source_conflict` |
| 4 | `injection_type` | G140: Wtrysk bezpośredni / M140: Wtrysk bezpośredni / G150 4x4: Wtrysk bezpośredni / H155: Wtrysk bezpośredni | `deferred_source_conflict` | `existing_coverage`, `context_model_required`, `deferred_source_conflict` |
| 5 | `engine_displacement_cm3` | G140: 1199 / M140: 1199 / G150 4x4: 1199 / H155: 1789 | `existing_coverage` | `existing_coverage` |
| 6 | `cylinders_and_valves` | G140: 3 cylindry; 12 zaworów / M140: 3 cylindry; 12 zaworów / G150 4x4: 3 cylindry; 12 zaworów / H155: 4 cylindry; 16 zaworów | `existing_coverage` | `existing_coverage` |
| 7 | `emissions_standard` | G140: Euro 6e-bis / M140: Euro 6e-bis / G150 4x4: Euro 6e-bis / H155: Euro 6e-bis | `deferred_source_conflict` | `deferred_source_conflict` |
| 8 | `particulate_filter` | G140: Tak / M140: Tak / G150 4x4: Tak / H155: Tak | `existing_coverage` | `existing_coverage` |
| 9 | `traction_battery` | G140: Litowo-jonowy; 48 V; 0,84 kWh / M140: Litowo-jonowy; 48 V; 0,84 kWh / G150 4x4: Litowo-jonowy; 48 V; 0,84 kWh / H155: Litowo-jonowy; 280 V; 1,4 kWh | `deferred_source_conflict` | `existing_coverage`, `import_ready_gap`, `deferred_source_conflict` |
| 10 | `maximum_speed_kmh` | G140: 180 / M140: 180 / G150 4x4: 180 / H155: 180 | `existing_coverage` | `existing_coverage` |
| 11 | `acceleration_0_100_s` | G140: 10,0 / M140: 9,8 / G150 4x4: 10,4 / H155: 9,7 | `existing_coverage` | `existing_coverage` |
| 12 | `drivetrain` | G140: 4×2 / M140: 4×2 / G150 4x4: 4×4 z tylnym silnikiem elektrycznym / H155: 4×2 | `existing_coverage` | `existing_coverage`, `context_model_required` |
| 13 | `gearbox_type_and_gears` | G140: Manualna; 6-biegowa / M140: Manualna; 6-biegowa / G150 4x4: Automatyczna; dwusprzęgłowa; 6-biegowa / H155: Automatyczna; Multi-mode; 4+2 | `context_model_required` | `existing_coverage`, `context_model_required` |
| 14 | `front_brake_disc_dimensions_mm` | G140: Φ296x26 / M140: Φ296x26 / G150 4x4: Φ296x26 / H155: Φ296x26 | `existing_coverage` | `existing_coverage` |
| 15 | `homologation_protocol` | G140: WLTP(3) / M140: WLTP(3) / G150 4x4: WLTP(3) / H155: WLTP(3) | `context_model_required` | `context_model_required` |
| 16 | `eco_mode` | G140: Tak / M140: Tak / G150 4x4: Tak / H155: Tak | `import_ready_gap` | `import_ready_gap` |
| 17 | `fuel_tank_capacity_l` | G140: LPG: 50; Benzyna: 50 / M140: Benzyna: 50 / G150 4x4: LPG: 50; Benzyna: 50 / H155: Benzyna: 50 | `existing_coverage` | `existing_coverage` |
| 18 | `combined_cycle_co2_g_km` | G140: Benzyna: 130/132; LPG: 114/116 / M140: 122/124 / G150 4x4: 134/117 (LPG) / H155: 104/106 | `import_ready_gap` | `existing_coverage`, `import_ready_gap` |
| 19 | `combined_cycle_fuel_consumption_l_100km` | G140: Benzyna: 5,7/5,8; LPG: 7,0/7,1 / M140: 5,4/5,5 / G150 4x4: 5,9/7,2 (LPG) / H155: 4,6/4,7 | `import_ready_gap` | `existing_coverage`, `import_ready_gap` |
| 20 | `payload_min_max_kg` | G140: 452/521 / M140: 451/540 / G150 4x4: 462/509 / H155: 453/521 | `deferred_source_conflict` | `existing_coverage`, `deferred_source_conflict` |
| 21 | `luggage_capacity_under_shelf_dm3_vda` | G140: 609** / M140: 667 / 624 / G150 4x4: 444; nie ma zestawu naprawczego / koła zapasowego / H155: 546 / 488 | `deferred_source_conflict` | `existing_coverage`, `deferred_source_conflict` |
| 22 | `luggage_capacity_folded_rear_seat_dm3_vda` | G140: 1877** / M140: 1937 / 1894 / G150 4x4: 1712 / H155: 1851 / 1791 | `deferred_source_conflict` | `existing_coverage`, `deferred_source_conflict` |
| 23 | `luggage_capacity_under_shelf_l` | G140: 660** / M140: 702 / 681 / G150 4x4: 556; nie ma zestawu naprawczego / koła zapasowego / H155: 612 / 566 | `deferred_source_conflict` | `existing_coverage`, `deferred_source_conflict` |
| 24 | `luggage_capacity_folded_rear_seat_l` | G140: 1960** / M140: 1960**; 2002 / 1981 / G150 4x4: 1856 / H155: 1912 / 1866 | `deferred_source_conflict` | `existing_coverage`, `deferred_source_conflict` |

## Safe import boundary

Three source facts contain safe non-conflicting gaps: `eco_mode`, `combined_cycle_co2_g_km`, and `combined_cycle_fuel_consumption_l_100km`. The next package is limited to 30 inclusive CO2 and fuel-consumption ranges whose upper endpoints already equal current exact values. Hybrid-G 150 4x4 exact petrol/LPG pairs and every deferred conflict are excluded.

## Preserved conflicts and context

- Hybrid 155: brochure hybrid-system voltage 280 V versus current later-source exact value 200 V.
- Hybrid-G 150 4x4: maximum-power RPM 4500 versus current 5000; engine maximum-torque RPM 4000 versus current 1750.
- LPG injection cannot be inferred from the brochure’s unscoped direct-injection row.
- Euro 6e-bis conflicts with current later-source Euro 6 values.
- Traction-battery type is absent; Hybrid 155 voltage and 0.84/0.839 kWh precision remain source-sensitive.
- Mild hybrid-G 140 payload is 452–521 kg in the brochure versus 451–540 kg in current later-source ranges.
- Hybrid-G 150 4x4 cargo values remain blocked by contradictory repair-kit/spare-wheel equipment context.
- The printed mild-hybrid 140 final cargo cell contains the literal anomalous sequence `1960** 2002 / 1981`; it is not reinterpreted.

## Policy

- no `data/master/**` changes;
- no approved import specification;
- no automatic promotion;
- current exact values are not overwritten;
- official-source conflicts remain deferred.

## Next package

`post_residual_bigster_page20_emissions_consumption_range_import_001` will add only the 30 non-conflicting inclusive CO2 and combined-cycle consumption ranges identified above.
