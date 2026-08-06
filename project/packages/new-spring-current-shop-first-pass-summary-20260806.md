# New Spring current shop first-pass summary

Date: 2026-08-06  
Base commit: `ead11a677e14074c4a1dc58e698ad362e8bb9802`  
Package ID: `new_spring_current_shop_first_pass_summary`

## Goal

Consolidate the complete first bounded review pass for all 56 references in the official New Spring accessory price list and materialize the deferred retry queue without performing a same-day retry.

## Evidence

The summary combines:

- repository-wide shop coverage reconciliation;
- current-shop reconciliation batches 001–004;
- the official 56-row New Spring accessory price-list extract.

No source is replaced by a cross-market, cross-brand or third-party record.

## First-pass result

- price-list references: 56;
- confirmed Polish Dacia Shop cards: 26;
- exact current-price matches: 12;
- price mismatches: 0;
- confirmed cards without a captured catalogue price: 14;
- Polish Dacia Shop cards not resolved: 30;
- literal label matches among confirmed cards: 15;
- literal label drifts among confirmed cards: 11;
- temporarily unavailable confirmed cards: 12;
- listed confirmed cards: 14;
- not yet reviewed: 0;
- first bounded review pass: complete;
- full shop reconciliation: not complete.

## Status semantics

`confirmed_price_exact_match`

An official Polish Dacia Shop card was confirmed by exact part number, a current catalogue price was captured, and it equals the document price.

`confirmed_card_price_not_captured`

An official Polish Dacia Shop card was confirmed by exact part number, but the bounded retrieval did not expose a catalogue price. This is not a mismatch.

`dacia_pl_card_not_resolved`

No official Polish Dacia Shop card was resolved in the bounded retrieval. This does not establish withdrawal, incompatibility or unavailability.

## Retry queue

The separate retry queue contains 30 unresolved references in original price-list ordinal order.

- no retry was performed on the same day;
- the prior unresolved status is preserved;
- the queue is ready for a later bounded package `new_spring_current_shop_retry_001`;
- retry results must replace neither document evidence nor previous attempt history.

## Files

- `data/reporting/official_new_spring_accessory_current_shop_first_pass_summary_20260806.json`
- `data/reporting/official_new_spring_accessory_current_shop_first_pass_summary_20260806.csv`
- `data/reporting/official_new_spring_accessory_current_shop_retry_queue_20260806.csv`
- `project/packages/new-spring-current-shop-first-pass-summary-20260806.md`

## Boundaries

- no master-data mutation;
- exact part-number identity only;
- one first-pass status for every price-list reference;
- no missing price treated as mismatch;
- no unresolved card treated as withdrawal;
- no same-day retry promoted as new evidence;
- no cross-market, cross-brand or third-party evidence transfer.
