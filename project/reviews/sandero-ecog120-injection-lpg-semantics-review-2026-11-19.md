# Sandero / Sandero Stepway Eco-G 120 Injection and LPG Capacity Semantics Review — 2026-11-19

## Objective

Close the bounded review of the 2026-11-02 official Polish Sandero / Sandero Stepway cennik page 5 without inferring fuel-specific injection or LPG vessel-capacity semantics.

## Evidence boundary

The Sandero source labels Eco-G 120 injection as one unqualified “bezpośredni” value and states LPG 40 l / petrol 50 l. The Jogger cennik distinguishes petrol direct / LPG indirect injection and LPG total / fillable capacity 50 / 40 l, but the repository has no normalized Eco-G 120 engine record or model-engine relationship linking the models. Do not transfer the Jogger-specific detail to Sandero.

## Deliverables

- `data/reporting/sandero_my26_20261102_ecog120_injection_lpg_semantics_review_20261119_001.json`
- `data/reporting/sandero_my26_20261102_ecog120_injection_lpg_semantics_review_20261119_001.md`
- Report registry entry.
- Focused regression test.
- No master-data or import-spec changes.

## Completion rule

The review may close with both semantic findings explicitly marked `needs_review` / “Do sprawdzenia”. Preserve all 18 existing fuel-capacity observations unchanged.
