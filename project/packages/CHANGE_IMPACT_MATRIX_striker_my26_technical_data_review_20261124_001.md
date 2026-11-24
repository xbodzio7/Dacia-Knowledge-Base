# Change-impact matrix — Striker MY26 technical data and dimensions

## Package identity

- Package: `striker_my26_technical_data_review_20261124_001`
- Source: `src_pl_striker_price_my26_20261102`; official Polish MY26 cennik, effective 2026-11-02
- Base SHA: `db0aa2b006faa8fb7abe7a64bdc915fd6ea96107`
- Printed pages: 6–7; exact configurations: 11
- Source SHA-256: `d9e1e874ceaf2b65faf37650ad7be4b9a7c9710ee1d09cbdee5856c286e62d35`

## Change inventory

| Entity | Added | Changed | Removed | Notes |
|---|---:|---:|---:|---|
| Scalar configuration observations | 423 | 0 | 0 | 42 declarative specifications |
| Bounded configuration ranges | 21 | 0 | 0 | 3 declarative specifications |
| Configurations / versions / sources | 0 | 0 | 0 | Existing 11 source-linked configurations reused |
| Prices / commercial mappings / availability | 0 | 0 | 0 | Prior price and page-5 packages remain unchanged |
| Attributes / enums | 0 | 0 | 0 | Existing semantic contracts reused |
| Reports / completeness scope | 1 | 0 | 0 | Dedicated technical review and residual-gap evidence |

## Evidence boundaries

- Page 6: powertrain, performance, fuel/emissions, minimum luggage volume, tyre season, weights, towing and payload.
- Page 7: vector-diagram exterior dimensions, visually transcribed because no text layer exists.
- Petrol/LPG distinctions remain separated; numeric intervals remain in the range table.
- No hybrid 150 total power is calculated.
- Hybrid 155 CO₂ `95/96`, running-order mass, maximum folded-seat volume, trim-level tyre fitment, 1000 m standing-start time and unexplained interior dimensions remain excluded or unresolved.

## Required validation

- [ ] All 42 scalar specifications verify against exact master rows.
- [ ] All 3 range specifications verify against exact master rows.
- [ ] Source SHA-256, file size and page count remain exact.
- [ ] Page-6 text checks pass; page-7 text matching is skipped only for the vector diagram while binary identity remains verified.
- [ ] Exact 11-configuration scope and no duplicate semantic observations.
- [ ] Six mandatory CI checks pass on the final exact PR head.
- [ ] Technical review confirms no unsupported values or applicability transfer.

## Baseline expectation

- Tests: 2054
- Master CSV files: 48
- Master rows: 23478
- Configuration values: 8953
- Scalar import specifications: 235
- Configuration value ranges: 472
- Range import specifications: 28
- Availability records: 10399
- Attributes: 417
- Attribute categories: 30
