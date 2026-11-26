# Spring Commercial Context Resolution

Package ID: `spring_commercial_context_resolution_001`

Status: complete

## Goal

Resolve the reviewed Spring Type 2 cable conflict and separate exact current MY26 commercial observations from MY2025 stock-only and volatile dealer-stock contexts before any further master-data import.

## Delivered

- registered four official Dacia evidence contexts;
- resolved the Type 2 cable as standard for exact current Essential electric 70 and Extreme electric 100 states;
- preserved Expression electric 70 as unresolved for current MY26 because the exact captured matrix is MY2025 stock-only;
- recorded exact current Essential paint states: Biel alpejska at 0 PLN and Khaki lichen at 2300 PLN;
- retained the MY2025 Expression/Extreme 2300 PLN paint class as historical/contextual evidence only;
- classified dealer-stock totals as whole-vehicle context that cannot be decomposed into reusable standalone prices;
- generated deterministic JSON and Markdown reports with a verification command.

## Master-data boundary

This is a review-only package. It changes no master row, price, availability state, model, domain or attribute.

The existing Type 2 item is modeled as an option while current exact evidence states standard equipment. A safe correction therefore requires an explicit semantic migration, not a zero-price option import.

## Follow-up

Proceed with `spring_current_grade_snapshot_capture_001` to capture exact current Expression and Extreme grade palettes and charging-equipment states before deciding whether bounded availability and commercial-item migrations are justified.
