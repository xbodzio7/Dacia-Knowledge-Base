# Sandero Official-Web Source Gap Review

## Selection

The completeness reanalysis ranked `src_pl_sandero_official_web_configurations_20260723` first because the two automatic Sandero configurations still contain 48 missing technical slots and 32 missing equipment slots in their reporting denominator.

## Source reconciliation

The registered snapshot contains four exact catalogue prices and eight version-level standard highlights. Those highlights expand to 16 exact configuration observations across Expression and Journey manual and automatic states.

PR #223 already imported all four prices and all 16 source-visible standard-equipment observations. The source contains no automatic-specific technical table and no explicit `not_applicable` classifications for the remaining completeness slots.

## Decision

The source is classified as `source_exhausted_not_stated` for this gap review.

- no master-data row is added or modified;
- missing slots are not converted to zero, unknown, unavailable or not applicable;
- broad package and option mentions remain unassigned because exact Eco-G gearbox applicability is not proven;
- the default Essential TCe 100 configurator state is not projected onto Eco-G configurations;
- no previously imported observation is duplicated.

## Next candidate

The next ranked source-backed candidate is Jogger with `src_pl_jogger_price_my26_20260401`: 32 missing technical slots, no missing equipment slots and weighted impact 96. The next package must inspect the exact PDF evidence before importing any values.
