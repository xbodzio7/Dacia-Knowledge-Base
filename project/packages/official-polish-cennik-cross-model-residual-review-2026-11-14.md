# Official Polish Cennik Cross-Model Residual Review — 2026-11-14

## Purpose

Close the canonical reporting package `official_polish_cennik_cross_model_residual_review_20261114_001`. Reconcile the registered Polish Dacia price-list snapshots against current catalogue-price and commercial-item master records, identify only exact residual gaps, and select the next bounded import package.

## Scope

- Duster MY26 — 2026-11-02
- Bigster MY26 — 2026-10-01 and 2026-11-02
- Sandero / Sandero Stepway MY26 — 2026-11-02
- Jogger MY26 — 2026-10-01
- Spring MY25 dealer stock — 2026-07-08

Brochures, configurator evidence, dealer promotions and separately distributed accessory catalogues are excluded.

## Durable results

- Machine-readable review: `data/reporting/official_polish_cennik_cross_model_residual_review_20261114.json`
- Human-readable review: `data/reporting/official_polish_cennik_cross_model_residual_review_20261114.md`
- Jogger reconciliation report corrected: `data/reporting/jogger_price_list_20261001_reconciliation_001.json`

The review accounts for 70 catalogue price cells, 54 source-specific price rows, 16 reused price cells and 455 existing commercial mappings across six source/date entries.

## Residuals

1. Jogger: 54 exact commercial mappings missing (38 optional, 16 not_available), plus one special non-metallic paint item at 2,800 PLN.
2. Bigster November 2026: registered source SHA exists, but the original PDF binary is not archived in the repository.
3. Spring: no MY26 source is registered; MY25 stock values remain date/model-year bounded.
4. Jogger metallic paint pair 2,800/3,000 PLN has no safe colour/grade assignment.
5. Separate accessory lists are not mapped to vehicle configurations without exact applicability evidence.

## Source-fidelity decisions

- Duster: preserve 230 V in the November technical table and 260 V in narrative text; do not create 280 V.
- Jogger: 7-seat Eco-G 120 manual price matrix is Essential dash, Expression 86,550 PLN, Extreme 94,400 PLN. Master price rows are correct; only the report had shifted values.
- Jogger: Extreme heated front seats marked `P` are part of a package, not a standalone priced option.
- Spring: MY25 dealer-stock prices and campaign terms are not generalized to MY26.

## Next package

`jogger_price_list_20261001_commercial_matrix_import_20261114_001`: add one special non-metallic paint item and 54 dated mappings from Jogger cennik pages 3–4, preserve historical rows, correct the source report, and run independent source-fidelity and full Quality checks.
