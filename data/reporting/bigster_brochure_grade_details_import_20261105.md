# Bigster brochure grade-specific cabin details — 2025-12-10

## Source
- Official Polish Bigster brochure, document date: 2025-12-10
- Registered source: `src_pl_bigster_brochure_20251210`
- SHA-256: `76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74`
- Reviewed printed pages 14–17 (PDF pages 15–18)

## Imported data
- 56 source-linked scalar observations across 14 exact active configurations.
- 4 attributes: `parking_brake_type`, `steering_wheel_material`, `rear_seat_folding`, `speaker_count`.
- 16 declarative import specifications (one attribute and one grade/page per specification).
- Grade scope: Essential 2, Expression 4, Journey 4, Extreme 4.

| Attribute | Essential | Expression | Journey | Extreme |
|---|---|---|---|---|
| Parking brake | manual | electric | electric | electric |
| Steering wheel material | eco_leather_soft_feel | inherited | inherited | inherited |
| Rear seat folding | 1/3-2/3 | 40/20/40 | 40/20/40 | 40/20/40 |
| Speaker count | 4 | 4 standard | 6 | 6 |

## Evidence and interpretation
The brochure explicitly defines the grade inheritance chain: Expression = Essential+, Journey = Expression+, Extreme = Expression+. The imported values follow only those explicit grade relationships and the exact active configurations linked to the source.

Expression retains the Essential four-speaker Media Display baseline; Media Nav Live with six speakers is an optional upgrade on that grade and is not treated as standard. Journey and Extreme specify six-speaker Arkamys 3D audio as standard.

The historical Essential rear-seat split (1/3-2/3) is retained separately from the later 2026 configurator observation (40/60). Existing 2026 observations are not overwritten.

## Safety boundaries
- No new configurations or source-configuration relationships.
- No inference across powertrains beyond the brochure's explicit grade inheritance.
- No existing value or availability observation overwritten.
- The brochure's original wording is retained in each observation note.
- No equipment option/package is promoted to standard unless the brochure explicitly lists it as standard.

## Validation
The regression test checks all 56 exact rows, the 16 import specifications, contiguous IDs 8234–8289, all 14 active source-linked configurations, source SHA-256, and preservation of later-source observations.
