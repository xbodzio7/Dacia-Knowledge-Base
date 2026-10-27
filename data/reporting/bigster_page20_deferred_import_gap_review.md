# Bigster Page 20 Deferred Import Gap Review

Authored review of `post_residual_bigster_page20_deferred_import_gap_review_001`. It isolates three evidence-safe atomic subfacts from compound page-20 rows that also contain deferred conflicts. This package is review-only.

## Source and scope

- source: `src_pl_bigster_brochure_20251210`;
- file: `PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf`;
- SHA-256: `76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74`;
- page: 20;
- reviewed safe subfacts: 3;
- current Bigster configurations: 14;
- planned observations: 20.

## Import-ready subfacts

| Source subfact | Canonical attribute | Value | Configurations | Rows |
| --- | --- | ---: | ---: | ---: |
| `113 kW (150 KM) – moc łączna` | `hybrid_system_power_total` | `113` kW | 3 Hybrid-G 150 4×4 | 3 |
| `87 N.m przy 1630 obr./min – elektryczny` | `traction_motor_torque` | `87` Nm | 3 Hybrid-G 150 4×4 | 3 |
| `Litowo-jonowy` | `hybrid_battery_type` | `lithium_ion` | all 14 Bigster | 14 |

The total-system power attribute is explicitly source-stated and is not calculated from component powers. The torque value maps to the traction motor, not the combustion engine. The battery chemistry uses the active `hybrid_battery_type` enum contract already used by hybrid configurations; `traction_battery_type` is not selected, avoiding duplicate semantics.

## Exact target boundary

The three Hybrid-G 150 4×4 targets are:

- `bigster_expression_hybridg150_4x4_automatic`;
- `bigster_extreme_hybridg150_4x4_automatic`;
- `bigster_journey_hybridg150_4x4_automatic`.

Battery chemistry applies to all 14 active Bigster configurations. Every target already has the canonical `brochure_technical_data_for` relationship to the source.

## Preserved conflicts and context

- Hybrid-G 150 4×4 engine maximum-power speed remains brochure `4500 rpm` versus current exact `5000 rpm`.
- Hybrid-G 150 4×4 engine maximum-torque speed remains brochure `4000 rpm` versus current exact `1750 rpm`.
- The electric-motor phrase includes `1630 rpm`, but no approved motor-specific RPM attribute exists; `max_torque_rpm` remains engine-scoped.
- The first three powertrains retain the battery-capacity precision boundary `0.84 kWh` versus current `0.839 kWh`.
- Hybrid 155 retains the official-source voltage conflict `280 V` versus current exact `200 V`.

None of those values is imported, overwritten or resolved by date preference.

## Policy

- no `data/master/**` changes;
- no import specification in this review package;
- compound source rows are split only where the canonical attribute semantics are explicit;
- all RPM, capacity and voltage conflicts remain deferred;
- current exact observations remain unchanged.

## Next package

`post_residual_bigster_page20_deferred_import_gap_import_001` will add exactly 20 scalar observations: 3 × `hybrid_system_power_total=113`, 3 × `traction_motor_torque=87`, and 14 × `hybrid_battery_type=lithium_ion`. Three strict single-attribute import specifications, the affected completeness scopes and live candidate-coverage contracts will be updated in the same import package.
