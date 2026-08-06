# New Spring current shop reconciliation 003

Date: 2026-08-06  
Base commit: `71aa411a525f8af4eb11ac92c518030a1eed586c`  
Package ID: `new_spring_current_shop_reconciliation_003`

## Goal

Check the next 12 not-yet-reviewed New Spring accessory price-list references against the official Polish Dacia Shop, using exact part-number identity and preserving document and shop labels separately.

## Selection

The batch is the exact `next_batch` declared by:

`data/reporting/official_new_spring_accessory_current_shop_reconciliation_002_20260806.json`

Retry-deferred references from batches 001 and 002 are not mixed into this package.

## Result

- target references: 12;
- confirmed Polish Dacia Shop cards: 1;
- Polish Dacia Shop cards not resolved: 11;
- current shop catalogue prices captured: 0;
- price mismatches: 0;
- confirmed cards without an exposed catalogue price: 1;
- literal label matches: 0;
- literal label drifts: 1;
- confirmed New Spring compatibility records: 1;
- temporarily unavailable cards: 0;
- listed add-to-cart cards whose price was not exposed by the retrieved official page: 1.

The confirmed Polish Dacia Shop card is:

- `7717277903` — `Lodówka samochodowa`.

The card exposes the exact reference and `NOWY SPRING` compatibility. The retrieved page does not expose a catalogue price.

The 11 unresolved Polish Dacia Shop cards are:

- `8201486884`;
- `8201738553`;
- `8201751532`;
- `8201751534`;
- `8201752597`;
- `8201752599`;
- `8201756618`;
- `8201756621`;
- `7711949659`;
- `8201742284`;
- `7711945735`.

They remain unresolved. They are not classified as withdrawn, unavailable or incompatible. Official Renault Shop PL, foreign-market Dacia and third-party records are not substituted for a Polish Dacia Shop card.

## Label finding

Part `7717277903` retains a literal label difference:

- price-list label: `Lodówka przenośna`;
- shop label: `Lodówka samochodowa`.

The exact part number remains the stable identity. The shop label is not normalized back into the document wording.

## Cumulative coverage after batch 003

- price-list references: 56;
- unique references with a confirmed Polish Dacia Shop card: 23;
- full price reconciliations: 12;
- confirmed cards without a captured price: 11;
- bounded attempts without a resolved Polish card: 25;
- not yet reviewed: 8;
- full shop reconciliation: not complete.

## Final first-pass batch

`new_spring_current_shop_reconciliation_004` should review all eight remaining not-yet-reviewed references in source order:

1. `8201375535`
2. `8201751965`
3. `8201751968`
4. `7711784775`
5. `7711949678`
6. `8201737398`
7. `7711945184`
8. `7717300012`

The 25 unresolved references from batches 001–003 remain in a separate retry queue and are not mixed into batch 004.

## Files

- `data/reporting/official_new_spring_accessory_current_shop_reconciliation_003_20260806.json`
- `data/reporting/official_new_spring_accessory_current_shop_reconciliation_003_20260806.csv`
- `project/packages/new-spring-current-shop-reconciliation-003-20260806.md`

## Boundaries

- exact part-number identity only;
- Polish Dacia Shop card required for counted confirmation;
- no cross-market or cross-brand transfer;
- no third-party substitution;
- no missing price treated as mismatch;
- no unresolved card treated as withdrawal;
- no temporary unavailability treated as permanent withdrawal;
- no master-data mutation.
