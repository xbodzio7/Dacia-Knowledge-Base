# Jogger Page 19 Range and Context Follow-up Review

Status: **complete with existing coverage and preserved context**  
Reviewed: **2026-07-30**

## Result

No new range or scalar import is required. The repository already contains **58 source-specific RPM ranges** from page 19 and six Hybrid 155 scalar values at **5600 rpm**.

| Coverage | IDs | Count | Decision |
|---|---:|---:|---|
| Maximum-power RPM ranges | 177–202 | 26 | Existing coverage |
| Maximum-torque RPM ranges | 203–234 | 32 | Existing coverage |
| Hybrid 155 maximum-power RPM | 2285–2290 | 6 | Existing scalar coverage |

## Preserved source differences

- Eco-G 120 petrol maximum-power range is `4500–5000 rpm` in the brochure and `4500–5750 rpm` in the later official source for ten configurations. Both dated observations coexist; the later source keeps current precedence.
- Hybrid 155 total system power is `105 kW` in the brochure and `116 kW` in the later official source. The six current `116 kW` values remain authoritative; no conflicting brochure total is imported.

## Context boundaries

- fuel and energy columns are represented through governed fuel context and separate Hybrid fields, not a synthetic combined scalar;
- `WLTP(2)` remains explanatory protocol context because there is no approved homologation-protocol attribute;
- dash cells for electric-motor speed remain non-values and are not converted by inference.

## Closure

The Jogger page-19 follow-up chain is complete. No schema or master-data change is needed. Work returns to a verified-PDF residual queue re-entry review to select the next genuinely actionable package without reopening closed conflicts.
