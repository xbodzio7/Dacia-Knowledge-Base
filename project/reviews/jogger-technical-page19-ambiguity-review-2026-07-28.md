# Jogger Technical Page 19 Ambiguity Review

Date: 2026-07-28
Status: complete

## Purpose

Review all 16 candidates in `residual_gap_002` against the archived page layout and only their preserved evidence signatures.

## Source boundary

- source: `src_pl_jogger_brochure_20251217`;
- file: `PDF/Broszury/DACIA JOGGER broszura 20251217.pdf`;
- SHA-256: `eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6`;
- page: 19;
- candidates: 16.

## Outcome

| Decision | Candidates |
| --- | ---: |
| Covered | 1 |
| Partially covered | 2 |
| Deferred source conflict | 7 |
| Signature mismatch | 6 |
| **Total** | **16** |

Three signatures containing 28 records are selected. The review preserves the 105/116 kW Hybrid 155 conflict, contradictory mass labels and the 1200/1000 kg Hybrid trailer conflict. Acceleration evidence is never substituted for elasticity, mass or towing.

## Commands

```bash
python tools/dkb.py jogger-technical-page19-ambiguity-review
python tools/dkb.py jogger-technical-page19-ambiguity-review --verify
```

No master data or approved import specification is changed.

## Next package

**Duster Mini Technical Page 20 Ambiguity Review** — 5 candidates and 26 preserved signatures.
