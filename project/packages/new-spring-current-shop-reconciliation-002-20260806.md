# New Spring current shop reconciliation 002

Date: 2026-08-06  
Base commit: `269b0ef825bd642951d96dcadc02d450da444336`  
Package ID: `new_spring_current_shop_reconciliation_002`

## Goal

Check the next 12 not-yet-reviewed New Spring accessory price-list references against the official Polish Dacia Shop, using exact part-number identity and preserving document and shop labels separately.

## Selection

The batch is the exact `next_batch` declared by:

`data/reporting/official_new_spring_accessory_current_shop_reconciliation_001_20260806.json`

Retry-deferred references from batch 001 are not mixed into this package.

## Result

- target references: 12;
- confirmed Polish Dacia Shop cards: 2;
- Polish Dacia Shop cards not resolved: 10;
- current shop catalogue prices captured: 0;
- price mismatches: 0;
- confirmed cards without an exposed catalogue price: 2;
- literal label matches: 1;
- literal label drifts: 1;
- confirmed New Spring compatibility records: 2;
- temporarily unavailable cards: 0;
- listed add-to-cart cards whose price was not exposed by the retrieved official page: 2.

The two confirmed Polish Dacia Shop cards are:

- `8201751967` — `Podłokietnik`;
- `7711943515` — `Przewód ładowania akumulatora - złącze T2-E/F`.

Both cards expose the exact reference and `NOWY SPRING` compatibility. Neither retrieved page exposes a catalogue price.

The ten unresolved Polish Dacia Shop cards are:

- `7711945712`;
- `8201743312`;
- `8201751961`;
- `296976446R`;
- `7711943517`;
- `7711943518`;
- `7717278287`;
- `7717301120`;
- `7717301121`;
- `8201486883`.

They remain unresolved. They are not classified as withdrawn, unavailable or incompatible. Official Renault Shop PL, foreign-market Dacia and third-party records are not substituted for a Polish Dacia Shop card.

## Label finding

Part `7711943515` retains a literal label difference:

- price-list label: `Przewód ładowania akumulatora z gniazda domowego T2-E/F jednofazowy 10 A - długość 6,5m`;
- shop label: `Przewód ładowania akumulatora - złącze T2-E/F`.

The exact part number remains the stable identity. The shorter shop label is not normalized back into the document wording.

## Cumulative coverage after batch 002

- price-list references: 56;
- unique references with a confirmed Polish Dacia Shop card: 22;
- full price reconciliations: 12;
- confirmed cards without a captured price: 10;
- bounded attempts without a resolved Polish card: 14;
- not yet reviewed: 20;
- full shop reconciliation: not complete.

## Next bounded batch

`new_spring_current_shop_reconciliation_003` should review the next 12 not-yet-reviewed references in source order:

1. `8201486884`
2. `8201738553`
3. `8201751532`
4. `8201751534`
5. `8201752597`
6. `8201752599`
7. `8201756618`
8. `8201756621`
9. `7711949659`
10. `8201742284`
11. `7711945735`
12. `7717277903`

The 14 unresolved references from batches 001 and 002 remain in a separate retry queue and are not mixed into batch 003.

## Files

- `data/reporting/official_new_spring_accessory_current_shop_reconciliation_002_20260806.json`
- `data/reporting/official_new_spring_accessory_current_shop_reconciliation_002_20260806.csv`
- `project/packages/new-spring-current-shop-reconciliation-002-20260806.md`

## Boundaries

- exact part-number identity only;
- Polish Dacia Shop card required for counted confirmation;
- no cross-market or cross-brand transfer;
- no third-party substitution;
- no missing price treated as mismatch;
- no unresolved card treated as withdrawal;
- no temporary unavailability treated as permanent withdrawal;
- no master-data mutation.
