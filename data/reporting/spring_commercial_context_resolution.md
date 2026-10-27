# Spring Commercial Context Resolution

**Status:** complete  
**Date:** 2026-08-02  
**Master-data mutations:** 0

## Type 2 charging cable

Current exact official MY26 evidence resolves the cable as **standard equipment** for:

- `spring_essential_electric70_automatic`,
- `spring_extreme_electric100_automatic`.

`spring_expression_electric70_automatic` remains unresolved for the current model year. The exact official matrix available in this review is explicitly limited to MY2025 dealer stock, so its standard state is not promoted to MY26.

The existing commercial item is option-shaped. This package therefore records the conflict resolution but does not create a zero-price option or silently change availability semantics.

## Paint context

Exact current MY26 observations:

- `spring_essential_electric70_automatic` / `spring_colour_biel_alpejska`: **standard**, 0 PLN
- `spring_essential_electric70_automatic` / `spring_colour_lichen_khaki`: **optional**, 2300 PLN

The official 2300 PLN paint class for Expression and Extreme belongs to the MY2025 stock-only price list. It remains historical/contextual evidence and is not transferred to current MY26 mappings. Legacy colours absent from the captured Essential palette are not globally removed because current Expression and Extreme palettes were not captured exactly.

## Stock context

Classification: `whole_vehicle_context_only`.

Dealer-stock totals and selected equipment are not reusable standalone option or paint prices unless separately itemized.

## Findings

- Current exact MY26 evidence resolves the Type 2 cable as standard for Essential electric 70 and Extreme electric 100.
- Expression electric 70 remains unresolved for current MY26 because the exact official matrix captured in this review is MY2025 stock-only.
- Essential MY26 has exact current paint states: Biel alpejska is standard at 0 PLN and Khaki lichen is optional at 2300 PLN.
- The 2300 PLN MY2025 paint class is not promoted to current Expression or Extreme mappings.
- Whole-vehicle stock totals are not decomposed into reusable standalone option or paint prices.

## Data boundary

- master rows changed: **0**,
- prices imported: **0**,
- availability states changed: **0**,
- models or domains added: **0**.

## Next package

`spring_current_grade_snapshot_capture_001` will capture exact current Expression and Extreme grade states before any bounded commercial migration.
