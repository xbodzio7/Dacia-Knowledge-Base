# Jogger Page 19 Remaining Mass Conflict Closure

Status: **complete with preserved boundaries**  
Reviewed: **2026-07-30**

## Closure result

All safe exact scalar imports selected from Jogger brochure page 19 are complete. Five append-only packages added **128 source-specific observations** without overwriting later official values.

| Area | IDs | Observations | Result |
|---|---:|---:|---|
| 0–100 km/h acceleration | 3336–3361 | 26 | Imported |
| Minimum kerb weight | 3362–3383 | 22 | Imported |
| Petrol/LPG capacities | 3384–3425 | 42 | Imported |
| Gross vehicle weight | 3426–3447 | 22 | Imported |
| Non-Hybrid braked trailer weight | 3448–3463 | 16 | Imported |

## Preserved mass boundaries

Two blocks remain unimported because the printed headings conflict with the magnitudes. The repository does not relabel source evidence by inference:

- values `1230/1312/1335/1373` and `1261/1342/1364/1405` are printed under a gross-train heading but resemble maximum kerb weight;
- values `2885/2965/2985/2830` and `3055/3140/3160/3000` are printed under a gross-vehicle heading but resemble gross vehicle plus trailer.

Hybrid 155 braked-trailer evidence also remains a deliberate non-import boundary: the brochure states **1200 kg**, while the later official MY26 source states **1000 kg** for all six current Hybrid 155 configurations.

## Non-mass follow-up

The mass closure does not decide RPM range modeling, energy-source column semantics, homologation-protocol context or the Hybrid 155 total-power conflict. Those items move to **Jogger Page 19 Range and Context Follow-up Review**.

## Decision

- safe exact scalar imports complete;
- no current value overwritten;
- no inferred relabeling;
- official conflicts remain visible;
- page-19 mass review closed.
