# Interactive Shortlist Interface Repair

Date: 2026-07-31

Status: **complete**

## User-visible repairs

- restores one forced dark theme across the page, filters, result cards, selection panel and comparison table;
- groups equal commercial grade names across selected models while expanding each choice to the exact underlying version codes;
- gives the comparison parameter column and every configuration column deterministic widths;
- keeps model headers visible during vertical scrolling inside the comparison viewport;
- keeps parameter and category names visible during horizontal scrolling;
- replaces the oversized category colspan cell with one sticky category label cell and a separate filler cell.

## Semantics

The package changes presentation and filter ergonomics only. It does not infer missing values, merge reporting scopes, create cross-scope pairs, or modify source-backed catalogue data.

## Follow-up

A separate source review will audit brochure colour offers, explicit grade inheritance such as `Expression = Essential +`, and repeated missing values that may be resolved only through direct source statements.
