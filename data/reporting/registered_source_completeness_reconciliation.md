# Registered Source Completeness Reconciliation

**Status:** complete  
**Date:** 2026-08-02

## Scope

- Reviewed 22 remaining active-comparison gaps from the canonical exact-source queue.
- Reviewed all 29 active commercial mappings whose amount is blank.
- Covered 81 active configurations and 186 active commercial mappings without adding models or domains.

## Classification result

| Classification | Count | Meaning |
|---|---:|---|
| `importable` | 2 | An exact registered current source states the value or price for the same configuration and item. |
| `source-not-stated` | 27 | The exact registered source does not state the value or price. |
| `source-conflict` | 2 | Registered sources disagree about the commercial state. |
| `context-unmodeled` | 20 | The evidence exists only in a context the current row model does not preserve, or the blank row represents a different context. |

## Importable findings

- `spring_city_package` for `spring_extreme_electric100_automatic`: **1800 PLN**, exact current official configurator snapshot.
- `spring_power_package` for `spring_extreme_electric100_automatic`: **3000 PLN**, exact current official configurator snapshot.

## Active-comparison gaps

- 20 technical slots (`front_track`, `rear_track`, LPG/petrol `max_power_rpm`) are not stated by the registered exact configuration PDFs.
- 2 `gear_shift_indicator` slots belong to automatic configurations. They should be presented as not applicable rather than as missing data.

## Optional-price gaps

- 4 Duster rows record package selection in exact stock vehicles; separate rows already carry the standalone prices. The blank stock-selection rows must remain blank.
- 7 Spring Essential rows have no exact current price for the existing mapped item.
- 2 Spring Extreme package prices are directly importable.
- 2 Spring Type 2 cable rows conflict: the brochure mapping says optional, while the newer stock price list says standard.
- 14 Spring rows have related MY25 stock prices but lack the model-year and/or paint-price-class context required for safe current import.

## Evidence boundary

No blank amount was converted to zero, no technical value was copied from a sibling configuration, and no MY25 stock price was treated as an unrestricted current price. This review records decisions only; it does not mutate master data.

## Next package

`reviewed_gap_state_materialization_001` will import only the two exact current Spring package prices and will expose reviewed terminal states in the comparison and pricing interface. It will preserve Duster stock-selection blanks, surface the two Spring conflicts, and avoid importing MY25-context prices until their context is modeled.
