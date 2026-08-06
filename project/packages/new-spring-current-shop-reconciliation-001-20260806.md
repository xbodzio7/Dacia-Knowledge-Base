# New Spring current shop reconciliation 001

Date: 2026-08-06  
Base commit: `b64391861526e89ea794cd0df516f238c9855ded`  
Package ID: `new_spring_current_shop_reconciliation_001`

## Goal

Check the first 12 repository-wide unresolved New Spring accessory price-list references against the official Polish Dacia Shop, using exact part-number identity and preserving document and shop labels separately.

## Selection

The batch is the first 12 rows marked by:

`data/reporting/official_new_spring_accessory_shop_unreviewed_queue_20260806.csv`

No item already covered by PR #570, PR #577 or the repository-wide coverage reconciliation is repeated.

## Result

- target references: 12;
- confirmed Polish Dacia Shop cards: 8;
- Polish Dacia Shop cards not resolved: 4;
- current shop catalogue prices captured: 4;
- exact document/shop price matches: 4;
- price mismatches: 0;
- confirmed cards without an exposed catalogue price: 4;
- literal label matches: 6;
- literal label drifts: 2;
- confirmed New Spring compatibility records: 8;
- temporarily unavailable cards: 4;
- listed add-to-cart cards whose price was not exposed by the retrieved official page: 4.

The four unresolved Polish Dacia Shop cards are:

- `7711943172`;
- `966115844R`;
- `403154280R`;
- `739M00386R`.

They remain unresolved. They are not classified as withdrawn, unavailable or incompatible.

## Price findings

The four captured official-shop prices match the 2024 document prices exactly:

- `7711780759`: 87.00 PLN;
- `7711945185`: 940.00 PLN;
- `8201724187`: 145.00 PLN;
- `283D84357R`: 283.00 PLN.

The following confirmed cards expose the product and New Spring compatibility but did not expose a catalogue price in the bounded retrieval:

- `7711578466`;
- `403152884R`;
- `403154034R`;
- `685609899R`.

A missing captured price is not a mismatch.

## Label findings

Two literal label differences are retained without normalization:

- `7711780759`: the document uses parentheses while the shop uses a hyphen;
- `8201724187`: the shop corrects the document spelling `aluminowych` to `aluminiowych`.

## Cumulative coverage after batch 001

- price-list references: 56;
- unique references with a confirmed Polish Dacia Shop card: 20;
- full price reconciliations: 12;
- confirmed cards without a captured price: 8;
- bounded attempts without a resolved Polish card: 4;
- not yet reviewed: 32;
- full shop reconciliation: not complete.

## Next bounded batch

`new_spring_current_shop_reconciliation_002` should review the next 12 not-yet-reviewed references in source order:

1. `7711945712`
2. `8201751967`
3. `8201743312`
4. `8201751961`
5. `296976446R`
6. `7711943515`
7. `7711943517`
8. `7711943518`
9. `7717278287`
10. `7717301120`
11. `7717301121`
12. `8201486883`

The four unresolved references from batch 001 remain in a separate retry queue and are not mixed into batch 002.

## Files

- `data/reporting/official_new_spring_accessory_current_shop_reconciliation_001_20260806.json`
- `data/reporting/official_new_spring_accessory_current_shop_reconciliation_001_20260806.csv`
- `project/packages/new-spring-current-shop-reconciliation-001-20260806.md`

## Boundaries

- exact part-number identity only;
- Polish Dacia Shop card required for counted confirmation;
- no cross-market transfer;
- no third-party substitution;
- no missing price treated as mismatch;
- no unresolved card treated as withdrawal;
- no temporary unavailability treated as permanent withdrawal;
- no master-data mutation.
