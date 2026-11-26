# Post-Spring Charging Cable Priority Selection Review

Status: `complete`

## Selected next package

`spring_biel_alpejska_default_colour_migration_001`

Add the exact-current Spring Essential Biel Alpejska direct `exterior_color` value through the canonical declarative import contract and convert only its existing commercial mapping to standard at zero surcharge.

## Evidence

- configuration: `spring_essential_electric70_automatic`;
- direct attribute: `exterior_color` = `biel alpejska`;
- source: `src_pl_spring_commercial_context_20260802` dated `2026-08-02`;
- current direct value rows: `0`;
- current commercial mapping: `optional` with unknown amount;
- target commercial state: `standard`, `0 PLN`.

## Boundaries

- Use the current configuration-value import-spec schema and importer.
- Change no Expression or Extreme paint mapping.
- Change no charging-cable record.
- Do not infer unavailability for residual colours.
- Add exactly one master row and update exactly one existing mapping.

## Deferred candidates

- `spring_expression_current_commercial_state_capture_001` — exact option states remain incomplete.
- `spring_extreme_paint_palette_capture_001` — no complete exact-current priced palette is registered.
- `spring_residual_essential_palette_reconciliation_001` — missing legacy colours cannot be treated as unavailable.
