# New Spring shop coverage reconciliation

Date: 2026-08-06  
Base commit: `67189f1be19150ca43ca87eb918d8ed67bef35c5`  
Package ID: `new_spring_shop_coverage_reconciliation_001`

## Goal

Reconcile the two existing New Spring official-shop evidence reports before checking additional part numbers. The package removes double counting by exact part number and establishes the actual remaining queue.

## Existing evidence

The repository already contains two relevant evidence layers:

- `data/reporting/official_new_spring_accessory_page_reconciliation_20260806.json` from PR #570:
  - 11 shop records;
  - 10 references present in the 2024 New Spring accessory price list;
  - one shop-only reference, `749M68749R`.
- `data/reporting/official_new_spring_accessory_shop_corroboration_20260806.json` from PR #577:
  - four price-list references;
  - two references overlap the earlier report.

The duplicated references are:

- `7717301274`;
- `684344266R`.

## Result

After exact part-number deduplication:

- price-list rows: 56;
- raw shop-evidence rows across both reports: 15;
- raw price-list-reference evidence rows: 14;
- duplicated price-list references: 2;
- unique price-list references with shop evidence: 12;
- references with a captured current shop catalogue price: 8;
- exact document/shop price matches among those eight: 8;
- shop cards recorded without a captured catalogue price: 4;
- price-list references with no shop-evidence record: 44;
- shop-only references: 1;
- full shop reconciliation: not complete.

The earlier value of 52 unreviewed rows described only the four-row scope of PR #577. It is not the repository-wide remaining count because PR #570 had already recorded additional shop evidence.

## Coverage classes

The 12 covered price-list references are retained in the JSON reconciliation report with:

- source document identity;
- price-list name and price;
- shop name;
- captured shop price when present;
- exact-price comparison;
- literal label comparison;
- New Spring compatibility;
- captured availability state;
- every repository evidence path.

The four references with an existing shop card but no captured current price remain incomplete price reconciliations:

- `8201741933`;
- `403152645R`;
- `685605709R`;
- `684342227R`.

The shop-only rubber-mat reference `749M68749R` remains separate from document references `8201756618` and `8201756621`.

## Next bounded batch

`new_spring_current_shop_reconciliation_001` should review the first 12 unresolved references in source order:

1. `7711780759`
2. `7711943172`
3. `7711945185`
4. `966115844R`
5. `7711578466`
6. `403152884R`
7. `403154034R`
8. `403154280R`
9. `8201724187`
10. `283D84357R`
11. `685609899R`
12. `739M00386R`

The CSV queue contains all 44 unresolved references and marks these first 12 with `next_batch_position`.

## Files

- `data/reporting/official_new_spring_accessory_shop_coverage_reconciliation_20260806.json`
- `data/reporting/official_new_spring_accessory_shop_unreviewed_queue_20260806.csv`
- `project/packages/new-spring-shop-coverage-reconciliation-20260806.md`

## Boundaries

- no new live shop retrieval is claimed;
- no master-data mutation;
- no document price is promoted to a current shop price without a captured shop value;
- no missing price is classified as a mismatch;
- no missing card is classified as withdrawal or unavailability;
- temporary unavailability is not permanent withdrawal;
- no similarly named or related references are merged without exact part-number identity.
