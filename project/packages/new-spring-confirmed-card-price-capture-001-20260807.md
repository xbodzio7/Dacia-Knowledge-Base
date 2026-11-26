# New Spring Confirmed Card Price Capture 001

Date: 2026-08-07  
Base commit: `b28d302d317bcc3b00aa9b7be2dde8a60d1c2677`  
Package ID: `new_spring_confirmed_card_price_capture_001`

## Goal

Revisit the complete homogeneous set of 16 already-confirmed official Polish Dacia Shop cards that lacked a captured current catalogue price, capture exact prices when the bounded official retrieval exposes them, and update repository-wide shop-coverage totals without retrying the separate 28 unresolved cards or changing master data.

## Accelerated package shape

This package is the first direct application of the milestone-review acceleration decision:

- all 16 cards share the same exact-part-number identity rule;
- all 16 use the same official Polish Dacia Shop evidence boundary;
- all 16 share the same price-status semantics;
- the complete set is one logical package and one Pull Request;
- internal chunking is only an execution detail;
- result summary is materialized inside this package rather than as a separate summary Pull Request.

## Result

- confirmed cards reviewed: 16;
- current catalogue prices captured: 2;
- exact current-price matches: 2;
- price mismatches: 0;
- cards still confirmed without a captured catalogue price: 14;
- unresolved cards retried: 0;
- master-data mutations: 0.

The two newly captured catalogue prices are:

| Part number | Official Polish Dacia Shop card | Document price | Captured shop price | Result |
| --- | --- | ---: | ---: | --- |
| `7711943515` | Przewód ładowania akumulatora - złącze T2-E/F | 1230.00 zł | 1230.00 zł | exact match |
| `7711945184` | Dashcam - Nextbase 322 GW i karta SD 32 GB | 1419.00 zł | 1419.00 zł | exact match |

For the other 14 exact official cards, the bounded retrieval resolved the card but did not expose a catalogue price. Their status remains `confirmed_card_price_not_captured`; this is not a mismatch.

## Repository-wide New Spring shop coverage

After this package:

- price-list references: 56;
- confirmed official Polish Dacia Shop cards: 28;
- exact current-price matches: 14;
- confirmed cards without a captured catalogue price: 14;
- unresolved cards: 28;
- price mismatches: 0.

## Evidence handling

The package uses the direct official Polish Dacia Shop card URL for every exact part number.

A price is promoted only when the official Polish Dacia Shop search surface exposes a numeric catalogue price for the same exact part number. The two captured prices were exposed by recent official-shop search snapshots and match the document prices exactly.

For rows where no product price is exposed, delivery price text such as `Odbiór osobisty 0 zł` is ignored and must not be treated as the product catalogue price.

## Files

- `data/reporting/official_new_spring_accessory_confirmed_card_price_capture_001_20260807.json`
- `data/reporting/official_new_spring_accessory_confirmed_card_price_capture_001_20260807.csv`
- `project/packages/new-spring-confirmed-card-price-capture-001-20260807.md`
- `project/state.json`
- `project/STATE_SUMMARY.md`

## Boundaries

- exact part-number identity only;
- official Polish Dacia Shop evidence only;
- no retry of `data/reporting/official_new_spring_accessory_current_shop_unresolved_queue_20260807.csv`;
- no missing product price treated as a mismatch;
- no delivery price treated as a product price;
- no foreign-market official Dacia evidence transfer;
- no Renault Shop substitution;
- no third-party substitution;
- no master-data mutation;
- one logical Pull Request for the complete 16-card homogeneous set;
- full quality gate on the final package head.

## Next bounded package

The remaining unresolved queue contains 28 exact references. A second bounded retry is eligible no earlier than 2026-08-08 unless new direct evidence appears first.

The next package is therefore `new_spring_current_shop_retry_cycle_002`, using the accelerated cadence:

- all 28 unresolved references in one logical package;
- internal chunks allowed for reviewability;
- same-package consolidated summary and remaining queue;
- no three-micro-PR plus separate-summary sequence.
