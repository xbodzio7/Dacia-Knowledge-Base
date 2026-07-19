# Jogger WLTP Efficiency Range Modeling and Import

## Status

`IMPLEMENTED`

This package materializes the denominator selected in PR #123 through the separate range table. Scalar configuration values remain unchanged.

## Denominator

Eight strict specifications create 64 closed page-6 ranges: 24 Eco-G manual, 16 Eco-G automatic, 12 TCe 110 and 12 Hybrid 155 observations. There are 32 combined fuel-consumption ranges and 32 combined CO2 ranges. Eco-G uses separate `lpg` and `petrol` contexts; TCe and Hybrid use `petrol`.

## Provenance

Range IDs form the first contiguous suffix `1-64`. Every row uses observation date `2026-04-01`, source `src_pl_jogger_price_my26_20260401`, page 6 and section `OSIĄGI`. Both endpoints are inclusive.

## PDF validation

The registered PDF SHA-256 is checked in every Python test job. Page-6 source text is additionally verified when a PDF extraction backend is present; the full Python 3.13 Quality gate installs `pdftotext` before validation.

## Baseline counters

The canonical baseline separately tracks scalar values, scalar specifications, value ranges and range specifications.

## Boundary

Payload, acceleration, RPM and battery-capacity evidence remain outside this package. No scalar row is added or replaced.

## Verified baseline

- 528 tests;
- 37 master CSV files and 3,909 rows;
- 1,204 scalar values and 71 scalar specifications;
- 64 range values and 8 range specifications;
- 1,811 availability records;
- 357 attributes in 30 categories.

## Validation

Quality #561 passed on Python 3.10, the full Python 3.13 gate with page-6 PDF text verification, and Windows.

## Next package

**Jogger Payload and Performance Range Selection** will select the remaining seat-qualified and performance ranges separately.
