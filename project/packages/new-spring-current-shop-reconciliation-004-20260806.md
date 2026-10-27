# New Spring current shop reconciliation 004

Date: 2026-08-06  
Base commit: `8cc4ad8a4eff7c42834a585bdab130ce94a1d947`  
Package ID: `new_spring_current_shop_reconciliation_004`

## Goal

Complete the first bounded review pass for the official New Spring accessory price list by checking all eight remaining never-reviewed references against the official Polish Dacia Shop.

## Selection

The batch is the exact final first-pass batch declared by:

`data/reporting/official_new_spring_accessory_current_shop_reconciliation_003_20260806.json`

The 25 retry-deferred references from batches 001–003 are not mixed into this package.

## Result

- target references: 8;
- confirmed Polish Dacia Shop cards: 3;
- Polish Dacia Shop cards not resolved: 5;
- current shop catalogue prices captured: 0;
- price mismatches: 0;
- confirmed cards without an exposed catalogue price: 3;
- literal label matches: 1;
- literal label drifts: 2;
- confirmed New Spring compatibility records: 3;
- temporarily unavailable cards: 0;
- listed add-to-cart cards whose price was not exposed by the retrieved official page: 3.

The confirmed Polish Dacia Shop cards are:

- `7711949678` — `Indukcyjna magnetyczna ładowarka do smartfona mocowana na kratce nawiewu`;
- `8201737398` — `Indukcyjna ładowarka do smartfonów Dacia`;
- `7711945184` — `Dashcam - Nextbase 322 GW i karta SD 32 GB`.

All three cards expose the exact reference and `NOWY SPRING` compatibility. None of the retrieved pages exposes a catalogue price.

The five unresolved Polish Dacia Shop cards are:

- `8201375535`;
- `8201751965`;
- `8201751968`;
- `7711784775`;
- `7717300012`.

They remain unresolved. They are not classified as withdrawn, unavailable or incompatible. Official Renault Shop PL, foreign-market Dacia and third-party records are not substituted for a Polish Dacia Shop card.

## Label findings

- `7711949678` is a literal document/shop label match.
- `8201737398`: the shop adds the brand qualifier `Dacia`.
- `7711945184`: the shop uses `Dashcam -` where the price list uses `Wideorejestrator`.

Exact part-number identity remains primary; shop labels are not normalized back into document wording.

## First-pass coverage complete

After batch 004:

- price-list references: 56;
- references with a confirmed Polish Dacia Shop card: 26;
- full price reconciliations: 12;
- confirmed cards without a captured price: 14;
- bounded attempts without a resolved Polish card: 30;
- not yet reviewed: 0;
- first bounded review pass: complete;
- full shop reconciliation: not complete.

The 30 unresolved references remain in a deferred retry queue. Repeating the same bounded retrieval on the same day is not promoted as new evidence.

## Next package

`new_spring_current_shop_first_pass_summary` should consolidate:

- all 56 price-list references;
- all confirmed Polish Dacia Shop cards;
- captured current prices and price-match results;
- confirmed cards without exposed prices;
- the 30-item deferred retry queue;
- coverage and completion counters.

The consolidation should not perform a same-day retry and should not mutate master data.

## Files

- `data/reporting/official_new_spring_accessory_current_shop_reconciliation_004_20260806.json`
- `data/reporting/official_new_spring_accessory_current_shop_reconciliation_004_20260806.csv`
- `project/packages/new-spring-current-shop-reconciliation-004-20260806.md`

## Boundaries

- exact part-number identity only;
- Polish Dacia Shop card required for counted confirmation;
- no cross-market or cross-brand transfer;
- no third-party substitution;
- no missing price treated as mismatch;
- no unresolved card treated as withdrawal;
- no temporary unavailability treated as permanent withdrawal;
- no same-day retry promoted as new evidence;
- no master-data mutation.
