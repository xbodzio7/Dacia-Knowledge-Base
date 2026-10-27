# Bigster Page 20 Remaining Conflict Boundary Review

Review of `post_residual_bigster_page20_remaining_conflict_boundary_review_001` after all evidence-safe page-20 imports completed so far.

## Source boundary

- source: `src_pl_bigster_brochure_20251210`;
- file: `PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf`;
- page: 20;
- brochure observation date: 2025-12-10;
- later current source: `src_pl_bigster_price_my26_20260703`.

The repository identifies scalar observations by configuration, attribute, fuel/gear context, observation date and source. Therefore explicit contradictory source statements may coexist without overwriting one another. This does not authorize automatic conflict resolution by date and does not permit projecting unscoped source text into a narrower semantic context.

## Source-observation-ready boundaries

| Boundary | Brochure | Later source | Targets | Decision |
| --- | ---: | ---: | ---: | --- |
| Hybrid-G 150 maximum-power speed | 4500 rpm | 5000 rpm | 3 | selected next |
| Hybrid-G 150 maximum-torque speed | 4000 rpm | 1750 rpm | 3 | selected next |
| emission standard | Euro 6e-bis | Euro 6 | 14 | later package |
| Hybrid 155 system voltage | 280 V | 200 V | 3 | later package |
| mild-hybrid source-stated battery capacity | 0.84 kWh | 0.839 kWh | 11 | later package |
| Mild hybrid-G 140 payload range | 452–521 kg | 451–540 kg | 4 | later range package |

Each of these values is explicit and maps to an existing governed attribute or range contract. Importing the older source observation must preserve the later observation and its provenance.

## Context-blocked boundaries

- The page-20 direct-injection row is not fuel-scoped. It cannot be copied to LPG because explicit LPG evidence includes multi-point injection.
- Electric-motor speed statements `1630 rpm` and `0–1630 rpm` have no approved motor-specific RPM attribute; engine `max_torque_rpm` cannot be reused.
- Hybrid-G 150 cargo values depend on a repair-kit/spare-wheel premise contradicted by equipment evidence.
- The literal cargo sequence `1960** 2002 / 1981` is not deterministically attributable to one equipment context and remains unparsed.

## Selected next package

`post_residual_bigster_page20_hybridg150_rpm_conflict_observation_import_001` will add exactly six older brochure observations:

- 3 × `max_power_rpm=4500`;
- 3 × `max_torque_rpm=4000`.

The package must also assert that the three later price-source observations `5000/1750` remain present and unchanged. No electric-motor RPM value is imported.

## Policy

- preserve contradictory registered sources;
- do not overwrite or delete later values;
- do not choose a winner solely by observation date;
- do not infer fuel, equipment or motor context;
- one narrow conflict-preservation package at a time.
