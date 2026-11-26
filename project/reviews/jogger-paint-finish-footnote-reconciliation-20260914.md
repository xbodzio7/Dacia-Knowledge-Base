# CAT-GAP-015 — Jogger paint-finish footnote reconciliation

Date: 2026-09-14

## Scope

CAT-GAP-015 covered the remaining Jogger paint-finish footnote conflict for the current colour surface. The target was to reconcile the finish classification without treating the configurator's colour surcharge as proof of finish type.

## Current official configurator

The current Dacia Jogger configurator exposes three colours in the observed current state:

- `biel alpejska` — 0 zł;
- `szary schiste` — +2700 zł;
- `czarna perła` — +2700 zł.

Source: https://www.dacia.pl/samochody/jogger-hybydowy/konfigurator.html

The configurator establishes current colour identity and price, but it does not itself label each colour as metallic or non-metallic.

## 2026 price documentation

The official 2026 Jogger equipment/price document separates:

- `Lakier niemetalizowany / niemetalizowany specjalny` — 0 / 2700 zł;
- `Lakier metalizowany` — 2700 / 2900 zł.

Source: https://cdn.group.renault.com/dac/pl/pdf/cenniki/JOGGER_PY_2026.pdf.asset.pdf/998fb1c410.pdf

This establishes the current finish-price categories, but not the colour-to-finish mapping by itself.

## Colour-to-finish reconciliation

### Biel Alpejska

A current 2026 Dacia dealer listing for Jogger 1.2 Eco-G 120 Expression 7os. identifies `Biel Alpejska` and explicitly lists `Lakier niemetalizowany`.

Source: https://kup.dacia.pl/wyszukiwarkaszczegoly/dacia/jogger/2026/122384

Classification: **niemetalizowany**.

### Szary Schiste

Dacia dealer evidence identifies `Szary Schiste` as `Lakier metalizowany`; the current Dacia-shop catalogue continues to show the colour as a paid option on 2026 Jogger inventory.

Source: https://kup.dacia.pl/nowedealerszczegoly/auto-spektrum/dacia/jogger/2025/127199

Supporting current inventory example: https://www.otomoto.pl/osobowe/oferta/dacia-jogger-ID6I6DlI.html

Classification: **metalizowany**.

### Czarna Perła

Dacia dealer evidence identifies `Czarna Perła` on Jogger. The official Jogger brochure explicitly classifies `Czarna Perła` as `Lakier metalizowany`.

Sources:

- https://kup.dacia.pl/nowedealerszczegoly/opalinski/dacia/jogger/2025/111516
- https://cdn.group.renault.com/dac/pl/pdf/broszury/jogger-brochure.pdf

Classification: **metalizowany**.

## Decision

For the current three-colour Jogger surface, the classification is reconciled as:

| Colour | Finish |
|---|---|
| Biel Alpejska | niemetalizowany |
| Szary Schiste | metalizowany |
| Czarna Perła | metalizowany |

No canonical master-data or availability change is required. The repository already has the relevant source-backed model and colour structures, and this package does not introduce a new value or compatibility assertion.

## Evidence boundary

The central 2026 configurator remains price-oriented rather than finish-labelled. Therefore this package does **not** claim that the configurator itself exposes the finish classification. The reconciliation combines current configurator identity, current 2026 pricing documentation, current Dacia dealer evidence and the official Jogger colour-footnote terminology.

Historical brochure terminology is used only to classify the three named colours that remain in the current surface; it is not used to project discontinued colours into the 2026 configurator.

## Explicit exclusions

- no inference from price alone;
- no projection to colours outside the current three-colour surface;
- no master-data writes;
- no availability writes;
- no reopening of CAT-GAP-002, CAT-GAP-003 or CAT-GAP-004;
- no reopening of the closed Sandero Stepway full-modal evidence boundary;
- no changes to historical PR #634, #637 or #639.
