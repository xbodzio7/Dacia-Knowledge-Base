# Jogger Page 19 Source Observation Import Closure

Status: **complete review; import queue remains open**  
Reviewed: 2026-07-30  
Source: `src_pl_jogger_brochure_20251217`, page 19

## Result

The three completed follow-up packages added **90 source-specific observations** without overwriting later official evidence:

| Package | Observations | IDs |
| --- | ---: | --- |
| 0–100 km/h acceleration | 26 | 3336–3361 |
| Minimum kerb weight | 22 | 3362–3383 |
| Petrol and LPG capacities | 42 | 3384–3425 |

The page 19 queue is **not yet closed**. Two exact, source-safe import areas remain.

## Remaining safe imports

### 1. Gross vehicle weight

All 22 printed values exactly match current official observations.

| Seat layout | TCe 110 | Eco-G manual | Eco-G automatic | Hybrid 155 |
| --- | ---: | ---: | ---: | ---: |
| 5 seats | 1685 kg | 1765 kg | 1785 kg | 1830 kg |
| 7 seats | 1855 kg | 1940 kg | 1960 kg | 2000 kg |

This is the next package because it covers every current configuration and does not require relabeling either adjacent conflicted source block.

### 2. Braked trailer weight — non-Hybrid only

The brochure value of **1200 kg** matches the later official source for all 16 TCe 110 and Eco-G 120 configurations. The six Hybrid 155 configurations remain excluded because the later official source records **1000 kg**.

## No new import required

The page 19 torque-speed ranges are already represented by the earlier Jogger hybrid-performance import. Matching TCe 110 and Eco-G LPG maximum-power-speed ranges are also already stored. No duplicate import is required.

## Preserved conflicts

- Hybrid 155 maximum power: brochure 105 kW, later official source 116 kW.
- Eco-G petrol maximum-power-speed upper endpoint: brochure 5000 rpm, later official source 5750 rpm.
- The block printed under the gross-train heading has maximum-kerb-like magnitudes.
- The block printed under the gross-vehicle heading has gross-train-like magnitudes.
- Hybrid 155 braked trailer weight: brochure 1200 kg, later official source 1000 kg.

No label is corrected by inference and no conflicting value is promoted automatically.

## Context-only boundaries

- The energy-source row spans governed fuel, hybrid and electric-energy context; it is not one scalar attribute.
- The WLTP protocol footnote has no approved governed attribute and remains contextual evidence.

## Next package

**Jogger Page 19 Gross Vehicle Weight Source Observations** — 22 exact brochure-source observations for all current five- and seven-seat configurations.
