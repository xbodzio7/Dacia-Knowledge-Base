# Bigster Page 20 Conflict Preservation Closure Review

Status: **complete**  
Package: `post_residual_bigster_page20_conflict_preservation_closure_review_001`  
Review date: 2026-07-30

## Scope

This review closes the five authored import packages selected from the remaining Bigster brochure page-20 conflicts. It verifies source-specific coexistence without choosing a winner by date, confirms that later price-source observations were not overwritten, and retains all context-blocked or anomalous evidence outside master data.

No file under `data/master/**` or `data/imports/**` is changed by this review.

## Source boundary

- Brochure source: `src_pl_bigster_brochure_20251210`
- File: `PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf`
- SHA-256: `76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74`
- Page: 20
- Brochure observation date: 2025-12-10
- Comparison source: `src_pl_bigster_price_my26_20260703`
- Comparison observation date: 2026-07-03

## Closure totals

| Measure | Result |
| --- | ---: |
| Completed import packages | 5 |
| Approved atomic facts | 6 |
| Scalar import specifications added | 5 |
| Range import specifications added | 1 |
| Brochure scalar observations added | 34 |
| Brochure range observations added | 4 |
| Source-coexistence pairs | 38 |
| Context-blocked boundaries retained | 4 |
| Source anomalies retained | 1 |

## Exact receipts

| Package | PR | Brochure receipt | Retained comparison receipt | Pairs |
| --- | ---: | --- | --- | ---: |
| Hybrid-G 150 engine RPM | #374 | IDs 3302–3307: 3× `max_power_rpm=4500`, 3× `max_torque_rpm=4000` | IDs 1504–1506: `5000`; IDs 1518–1520: `1750` | 6 |
| Emission standard | #376 | IDs 3308–3321: 14× `euro_6e_bis` | IDs 1296–1309: 14× `euro_6` | 14 |
| Hybrid 155 system voltage | #378 | IDs 3322–3324: 3× `280 V` | IDs 1475–1477: 3× `200 V` | 3 |
| Source-stated battery capacity | #381 | IDs 3325–3335: 11× `0.84 kWh` | IDs 1447–1457: 11× `0.839 kWh` | 11 |
| Mild Hybrid-G 140 payload range | #383 | Range IDs 275–278: 4× closed `452–521 kg` | Range IDs 149–152: 4× closed `451–540 kg` | 4 |

The three Hybrid 155 capacity observations at IDs 1458–1460 remain separately registered as `1.4 kWh` from the price source. They were not projected onto the eleven 48 V configurations.

## Preserved non-import boundaries

1. **Fuel scope of injection type** — the brochure row is not fuel-scoped and cannot be projected to LPG against explicit fuel-specific evidence.
2. **Traction-motor scalar RPM** — no approved motor-specific scalar RPM attribute exists for `1630 rpm`.
3. **Traction-motor RPM range** — no approved motor-specific range attribute exists for `0–1630 rpm`.
4. **Hybrid-G 150 cargo equipment context** — numeric cargo values remain blocked while repair-kit and spare-wheel context conflicts.

The literal folded-cargo sequence `1960** 2002 / 1981` remains a preserved source anomaly and is not reinterpreted.

## Decision

All five approved conflict-preservation packages are complete. Every brochure receipt coexists with its registered comparison-source observation, and no conflict has been resolved solely by chronology or numerical precision. The remaining context-blocked and anomalous evidence stays unimported.

Page-20 conflict preservation is therefore closed. Work returns to the deterministic residual queue.

## Next package

`residual_gap_051` — **Sandero Equipment Page 19 Unresolved Review — Chunk 1**.

The package reviews the first 40 of 65 unresolved equipment-matrix candidates from `src_pl_sandero_brochure_20260202`, page 19. It is review-only: exact candidate IDs, text and visual context are preserved without automatic promotion or master-data changes.
