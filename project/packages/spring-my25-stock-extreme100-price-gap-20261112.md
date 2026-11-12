# Spring MY25 stock price list — exact Extreme Electric 100 price closure

**Package:** `spring_my25_stock_extreme100_price_gap_20261112_001`  
**Source:** `src_pl_spring_price_my25_stock_20260708`  
**Official document:** [DACIA SPRING cennik MY25 stock](https://cdn.group.renault.com/dac/pl/pdf/cenniki/spring-price-2025.pdf.asset.pdf/11eef439c3.pdf)  
**Scope:** Polish MY25 dealer stock only.

## Change

The six-page documentary audit records two exact catalogue-price cells on printed page 1:
- Expression Electric 70 — 81,500 PLN (already linked to the source in master data).
- Extreme Electric 100 — 85,900 PLN (previously present only as a later configurator observation, without a price-list observation or source-configuration relationship).

This package adds the missing dated 2026-07-08 catalogue-price observation for `spring_extreme_electric100_automatic` and links that exact configuration to the MY25 stock price-list source.

## Evidence boundary

- The 85,900 PLN value is taken from the source's explicit page-1 catalogue-price cell.
- Applicability remains restricted to MY25 vehicles in dealer stock; it is not a MY26 price.
- The 17,000 PLN stock promotion is not distributed across configurations or represented as a catalogue-price reduction.
- The separate 2026-07-31 configurator observation is retained as a distinct source/date observation.
- No brochure or configurator facts are imported by this package.

## Validation

`tests/test_spring_my25_stock_price_gap.py` checks the exact price, source link, and MY25-only boundary.
