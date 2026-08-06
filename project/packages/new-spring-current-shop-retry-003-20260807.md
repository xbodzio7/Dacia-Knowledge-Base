# New Spring current shop retry 003

Date: 2026-08-07  
Base commit: `638b9203fd587b61e2a5bc52dc6b9527bfa6b940`  
Package ID: `new_spring_current_shop_retry_003`

## Goal

Recheck retry positions 21–30 from the materialized 30-item New Spring exact-part-number queue and complete the first deferred retry cycle.

## Scope

The package covers these exact part numbers in queue order:

1. `8201756618`
2. `8201756621`
3. `7711949659`
4. `8201742284`
5. `7711945735`
6. `8201375535`
7. `8201751965`
8. `8201751968`
9. `7711784775`
10. `7717300012`

Each record preserves its 2026-08-06 attempt and adds a separate 2026-08-07 retry result.

## Result

- retry positions reviewed: 10;
- confirmed official Polish Dacia Shop cards: 2;
- Polish Dacia Shop cards not resolved: 8;
- confirmed cards without a captured catalogue price: 2;
- current shop catalogue prices captured: 0;
- price matches: 0;
- price mismatches: 0;
- literal label matches: 1;
- literal label drifts: 1;
- New Spring compatibility confirmations: 2;
- status changes: 2.

Confirmed exact-part-number cards:

- `7711949659` — `Pokrowiec na samochód (rozmiar XS)`; literal label match; `NOWY SPRING` compatibility; listed for purchase; catalogue price not exposed.
- `8201742284` — `Dwustronna mata bagażnika Dacia Spring`; current shop label differs from the price-list label; `SPRING` and `NOWY SPRING` compatibility; listed for purchase; catalogue price not exposed.

The remaining eight records stay `dacia_pl_card_not_resolved`.

## Retry-cycle cumulative result

Across retry packages 001–003:

- retry positions reviewed: 30;
- confirmed official Polish Dacia Shop cards: 2;
- cards still not resolved: 28;
- status changes: 2.

Combined with the first-pass result for all 56 references:

- confirmed Polish Dacia Shop cards: 28;
- exact current-price matches: 12;
- confirmed cards without a captured catalogue price: 16;
- cards not resolved: 28;
- price mismatches: 0.

## Evidence boundary

The bounded retry used exact part-number identity and the official Polish Dacia Shop route for each reference.

Non-Polish official Dacia cards, Renault Shop cards and third-party records were used only as exclusion checks. They were not transferred to Polish New Spring evidence.

## Status semantics

`confirmed_card_price_not_captured`

An official Polish Dacia Shop card was confirmed by exact part number, but the bounded retrieval did not expose a catalogue price. This is not a mismatch.

`dacia_pl_card_not_resolved`

No official Polish Dacia Shop card was resolved in the bounded retry. This does not establish withdrawal, incompatibility or unavailability.

## Files

- `data/reporting/official_new_spring_accessory_current_shop_retry_003_20260807.json`
- `data/reporting/official_new_spring_accessory_current_shop_retry_003_20260807.csv`
- `project/state.json`
- `project/STATE_SUMMARY.md`
- `project/packages/new-spring-current-shop-retry-003-20260807.md`

## Boundaries

- no master-data mutation;
- exact part-number identity only;
- prior attempt history is preserved;
- no unresolved card treated as withdrawal, incompatibility or unavailability;
- no missing price treated as mismatch;
- no cross-market official Dacia evidence transfer;
- no Renault Shop substitution;
- no third-party substitution.

## Next package

`new_spring_current_shop_retry_cycle_summary_001` will consolidate all three retry packages and materialize the remaining 28-item unresolved queue.
