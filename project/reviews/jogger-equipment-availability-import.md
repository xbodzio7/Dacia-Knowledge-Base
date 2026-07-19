# Jogger Equipment Availability Import

## Status

`IMPLEMENTING`

This package materializes the denominator selected in PR #128 without changing scalar values, ranges, prices or existing availability rows.

## Denominator

Two versioned pages 4-5 matrices define 53 active boolean attributes for all 22 active Jogger configurations. The importer creates exactly 1,166 records: 920 `standard`, 84 `optional` and 162 `not_available`.

## Storage contract

The records form the contiguous availability-ID suffix `1812-2977`. Every row is dated `2026-04-01`, references `src_pl_jogger_price_my26_20260401`, retains the printed source label and preserves package or powertrain qualifiers in notes.

The existing 419 Sandero and 1,392 Duster records remain semantically unchanged.

## Evidence boundary

`start_stop_system` remains a scalar page-6 observation. Conflicting rain-wiper evidence, descriptive appearance values, package prices and features without a selected dedicated contract remain outside this package.

## Expected baseline

- 544 tests;
- 37 master CSV files and 5,155 rows;
- 1,204 scalar values and 71 scalar specifications;
- 144 range values and 19 range specifications;
- 2,977 availability records;
- 357 attributes in 30 categories.

## Next package

**Jogger Technical Reporting Scope Selection** will select the first homogeneous Jogger reporting denominator.
