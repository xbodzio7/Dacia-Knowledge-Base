# Spring non-conflicting technical observations review

Package: `spring_nonconflicting_technical_observations_review_001`

Sources:

- `src_pl_spring_brochure_20260219`
- `src_pl_spring_price_my25_stock_20260708`
- existing exact saved MY2026 configuration observations

## Existing coverage

The completed brochure technical import already records 54 scalar values and three closed power-RPM ranges for Essential Electric 70, Expression Electric 70 and Extreme Electric 100. It includes configuration-bound powertrain, battery-capacity, voltage, performance and luggage observations described in the repository documentation. Existing saved MY2026 configuration observations additionally provide later exact-state technical values.

## Comparison result

| Candidate area | Source fact | Result | Reason |
| --- | --- | --- | --- |
| Battery chemistry | LFP for Electric 70 and Electric 100 | `missing_safe_candidate` | Exact table cell, same value for both listed powertrains, no contradictory later source found, controlled enum already exists. |
| Battery mass | 204 kg for Electric 70 and Electric 100 | `missing_safe_candidate` | Exact table cell, explicit unit and no measurement ambiguity. |
| Battery capacity | 24.3 kWh | `already_represented` | Covered by prior Spring technical imports and saved configurations. |
| Nominal voltage | 354 V | `already_represented` | Covered by prior Spring technical imports and saved configurations. |
| AC/DC charging times | 10h11, 6h47, 3h20 and 29 min | `deferred_context` | Values depend on charger power and SOC interval; current scalar model must preserve both before import. DC availability is option/package dependent. |
| Maximum speed | 125 km/h in MY2025 stock list | `conflict` | Later exact MY2026 saved configurations report 130 km/h; retain dated states and do not overwrite. |
| Acceleration 0–100 | 12.3 / 9.6 s | `already_or_dated_conflict_review` | Prior brochure/saved observations exist; exact model-year applicability must be compared before another record is added. |
| WLTP range | 222/225 km variants and 225 km | `deferred_footnote_context` | Electric 70 value depends on footnoted wheel/configuration state that is not safely encoded by a single timeless value. |
| Passenger dimensions | drawing and technical-table values | `already_or_deferred_basis` | Several dimensions already exist from prior technical/saved imports; wheel/load-dependent clearance and image-only bases remain deferred. |
| Luggage 308 L / 288 dm3 and 1004 L folded | multiple measurement bases and seat states | `partly_represented` | Minimal ISO/VDA context already exists; maximum volume requires exact seat-state and measurement-basis comparison. |
| Cargo 1085 L / 341 kg | Cargo derivative | `deferred_separate_configuration` | Must not populate passenger configurations. |

## Selected next migration

`spring_stock_battery_material_observations_migration_001`

Scope:

1. verify or add the canonical battery-mass attribute and kg unit mapping;
2. materialize dated `battery_chemistry=LFP` and `battery_mass=204 kg` observations for the exact MY2025 stock configurations represented by Expression Electric 70 and Extreme Electric 100;
3. preserve source/date provenance;
4. make no changes to charging times, range, speed, dimensions, luggage or Cargo.

## Evidence boundary

The review selects only facts whose meaning does not depend on charging equipment, SOC interval, wheel choice, seat state or a later conflicting MY2026 observation. No absence is interpreted as unavailability.
