# New Spring current Polish Shop reconciliation — batch 001

Date: 2026-08-06  
Base main SHA: `67189f1be19150ca43ca87eb918d8ed67bef35c5`  
Package: `new_spring_current_shop_reconciliation_001`

## Goal

Check one bounded batch of previously unreviewed New Spring accessory part numbers against the official Polish Dacia Shop, while preserving document prices, current shop evidence and missing corroboration as separate facts.

## Prior coverage correction

The 56-row price list had more prior shop coverage than the latest four-row report alone showed:

- the earlier page reconciliation reviewed ten price-list part numbers;
- the later report reviewed four part numbers, two of which overlapped the earlier set;
- twelve unique price-list part numbers had therefore already been reviewed;
- the correct pre-batch remainder was 44 unique part numbers, not 52.

This package excludes all twelve earlier part numbers and selects the first fifteen remaining rows in source order.

## Batch result

- attempted part numbers: 15;
- retrieved Polish Dacia Shop cards: 8;
- exact Polish card not retrieved: 7;
- numeric shop prices exposed: 1;
- exact price matches: 1;
- price mismatches: 0;
- unresolved price comparisons: 14;
- exact label matches among retrieved cards: 6;
- preserved non-exact labels: 2;
- New Spring compatibility confirmed by retrieved cards: 8;
- cards shown as temporarily unavailable: 1;
- cards listed without an unavaility marker: 7.

The only exposed numeric price in this batch is part `8201724187`: 145 PLN in both the 2024 document and the current Polish shop result. The source labels differ only because the document says `aluminowych`, while the shop says `aluminiowych`; both labels remain preserved.

For seven part numbers the exact Polish product URL was not retrievable and an exact part-number search on the Polish shop domain produced no product-card result. Those rows are recorded as unconfirmed. They are not classified as withdrawn or permanently unavailable.

## Coverage after batch

- price-list part numbers attempted at least once: 27 of 56;
- retrieved Polish shop cards: 20 unique price-list part numbers;
- not yet attempted: 29;
- without a retrieved Polish shop card: 36, including the seven attempted-but-unconfirmed rows;
- full shop reconciliation: incomplete.

## Files

- `data/reporting/official_new_spring_accessory_shop_reconciliation_batch_001_20260806.json`
- `data/reporting/official_new_spring_accessory_shop_reconciliation_batch_001_20260806.csv`

## Boundaries

- no master-data mutation;
- no edits to the earlier reports;
- no price mismatch inferred when the shop card omits a numeric price;
- no withdrawal inferred from a missing card or an empty exact search;
- no permanent withdrawal inferred from temporary unavailability;
- no Polish evidence inferred from another Dacia market or a third-party shop;
- no dealer-local price inferred from the national catalogue view;
- no compatibility transfer to legacy Spring or another model.

## Next step

Review a second bounded batch from the 29 part numbers not yet attempted. Keep the seven attempted-but-unconfirmed references unresolved unless an exact Polish official product card becomes retrievable.
