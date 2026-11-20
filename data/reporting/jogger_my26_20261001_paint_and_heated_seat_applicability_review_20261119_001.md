# Jogger MY26 2026-10-01 Metallic Paint and Heated Seat Applicability Review

Report ID: jogger_my26_20261001_paint_and_heated_seat_applicability_review_20261119_001
Generated: 2026-11-20T21:35:05Z
Analysed commit: 8bcc724454adf90f9d022864010f2b76e6286edc
Status: current
Scope: Official Polish Jogger MY26 cennik effective 2026-10-01, printed pages 3–4; review of metallic-paint price applicability and Extreme heated-front-seat package marker against all 12 source-linked configurations and existing dated commercial mappings.

## Source and provenance

- Official source: [Dacia Jogger MY26 cennik effective 2026-10-01](https://cdn.group.renault.com/dac/pl/pdf/cenniki/jogger-price.pdf.asset.pdf/f5cdbd7878.pdf)
- Archived source: `owner_supplied/2026-10-01/f5cdbd7878.pdf`
- SHA-256: `12e536c1e60e9e7f91228b27a9d962cecacb5a5287d585f419a14af3003e8b46`
- Source code: `src_pl_jogger_price_my26_20261001`
- Printed pages reviewed: 3 and 4
- Exact scope: 12 source-linked configurations across Essential, Expression and Extreme.

## Page 3 — metallic paint

The page-3 matrix shows the following under each of the three grades:

| Source row | Essential | Expression | Extreme |
|---|---:|---:|---:|
| Lakier niemetalizowany / niemetalizowany specjalny | 0 / 2800 | 0 / 2800 | 0 / 2800 |
| Lakier metalizowany | 2800 / 3000 | 2800 / 3000 | 2800 / 3000 |

The special non-metallic finish is already represented by the distinct `jogger_special_nonmetallic_paint_option` item at 2,800 PLN across all 12 configurations. It must not be conflated with metallic paint.

The metallic row repeats the 2,800/3,000 PLN pair for all grades but does not name colours or explain which exact variant each amount represents. The printed table therefore does not establish a safe colour/grade/configuration crosswalk. In particular, no 5-seat/7-seat interpretation is added without an explicit source legend.

**Disposition:** `needs_review`. Preserve the pair as source evidence; add no metallic-paint commercial item or configuration mappings.

## Page 4 — heated front seats and ZIMOWY package

| Grade | Heated front seats row | Interpretation |
|---|---:|---|
| Essential | — | Not available |
| Expression | 700 PLN | Standalone optional equipment |
| Extreme | P | Included as a package element, not a standalone 700 PLN option |

The page legend explicitly defines `P = element pakietu`. The same page lists **Pakiet ZIMOWY** at **1,200 PLN** for Extreme and names its contents: heated front seats and a heated steering wheel.

The existing 54 dated commercial mappings already encode:
- four Expression configurations with standalone heated seats at 700 PLN;
- two Essential configurations where heated seats are unavailable;
- six Extreme configurations with the ZIMOWY package at 1,200 PLN;
- six non-Extreme configurations where the ZIMOWY package is unavailable;
- zero standalone Extreme heated-seat mappings.

**Disposition:** the Extreme package dependency is resolved. No master-data change is required.

## Outcome

- 54 existing commercial mappings verified against the exact 12 source-linked configurations.
- 0 master rows added or updated.
- 0 commercial items or mappings added/changed.
- Existing special non-metallic paint, heated-seat and ZIMOWY mappings preserved.
- No source binary changed.

The review is complete as an evidence assessment. The metallic-paint pair remains explicitly unresolved; the Extreme heated-seat marker is explained by the priced ZIMOWY package.
