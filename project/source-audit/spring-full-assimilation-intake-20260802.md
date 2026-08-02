# Spring brochure and price-list full-assimilation intake

**Package:** `legacy_pdf_full_assimilation_spring_sources_001`  
**Intake date:** 2026-08-02  
**Status:** `fully_reviewed`

## Canonical sources

### Brochure

- source code: `src_pl_spring_brochure_20260219`
- title: `DACIA SPRING broszura`
- market: PL
- document date: 2026-02-19
- repository path: `PDF/Broszury/DACIA SPRING broszura 20260219.pdf`
- verified SHA-256: `73a4c568ce273bc095f6ecf1cfa4f5f2a92324bb2f0bbc171ba45bb4a4cf3c8d`
- verified page count: 22

### Price list

- source code: `src_pl_spring_price_my25_stock_20260708`
- title: `DACIA SPRING cennik MY25 stock`
- market: PL
- effective date: 2026-07-08
- repository path: `PDF/Cenniki/DACIA SPRING cennik MY25 stock 20260708.pdf`
- verified SHA-256: `809d24ec3710aac02b3f3a2f33e1872689430a1d6887f387936a5ac3ff343ae0`
- verified page count: 6

## Completed review

The exact files supplied by the project owner matched the registered hashes and page counts. Every page was reviewed in parsed-text and rendered-image form. The review included:

- all tables and exact cells;
- availability symbols and legends;
- footnotes and their placement;
- image-embedded labels and dimension drawings;
- marketing, legal, Cargo and accessory boundaries;
- comparison with the later saved MY2026 configuration evidence.

## Produced audit artifacts

- `spring-brochure-20260219-page-inventory.md`
- `spring-price-my25-stock-20260708-page-inventory.md`
- `spring-evidence-ledger-20260802.md`
- `spring-source-conflicts-20260802.md`

## Key result

The sources cannot be reduced to one timeless charging-cable state. The February brochure marks the domestic cable standard and Type 2 optional, while the July MY2025 stock price-list matrix marks the domestic cable optional at 1500 PLN and Type 2 standard. The July document also contradicts itself between page-2 prose and the exact page-4 matrix.

These differences are registered as dated/model-year conflicts. This audit does not mutate master data merely to manufacture consistency.

## Completion boundary

Both sources are `fully_reviewed` for page coverage and fact classification. Candidate technical facts remain queued for bounded master comparison; they are not automatically considered imported. The next package must compare non-conflicting battery, charging-time, performance, dimension and luggage observations against current master records before any migration.
