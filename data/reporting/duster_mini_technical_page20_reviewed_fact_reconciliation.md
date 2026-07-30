# Duster Mini Technical Page 20 Reviewed Fact Reconciliation

Status: **complete with import handoff**  
Reviewed: **2026-07-30**

## Scope

The reconciliation reuses all 65 authored decisions from ambiguity package `003` and unresolved packages `020–021`. It compares them with the current exact master data for the seven manual 4×2 Eco-G 120 and mild hybrid 140 configurations.

## Candidate partition

| Classification | Candidates | Result |
|---|---:|---|
| Current exact same-source coverage | 10 | Closed |
| Current exact later-source coverage | 8 | Closed |
| Current configuration identity | 2 | Closed |
| Import-ready exact gap | 5 | Handoff: 35 observations |
| Context model required | 2 | Deferred |
| Explicit non-import or context | 38 | Preserved |
| **Total** | **65** | Classified once |

## Import-ready gaps

Each exact row applies to the four Eco-G 120 manual and three mild hybrid 140 manual configurations:

- emission standard: `euro_6e_bis`;
- particulate filter: `true`;
- Start & Stop: `true`;
- Eco mode: `true`;
- gross vehicle weight: `1805 kg` for Eco-G and `1830 kg` for mild hybrid 140.

The follow-up import will add **35 append-only observations**, planned as IDs `3464–3498`.

## Preserved boundaries

The unscoped `Bezpośredni` injection row is not imported for dual-fuel Eco-G because the governed model distinguishes injection by fuel context. Energy-source columns remain powertrain context. Dash cells, country-dependent CO₂/consumption text, incomplete rows and explanatory footnotes remain non-values.

## Handoff

**Duster Mini Page 20 Exact Scalar Gap Import**
