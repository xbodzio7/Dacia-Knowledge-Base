# Configuration Comparison Item Catalog Regression Coverage Review

Date: 2026-07-17

## Scope

This review closes **Configuration Comparison Item Catalog Regression Coverage** merged through PR #64.

Reviewed evidence:

- the discovery-time contract module in `tests/test_configuration_comparison_item_catalog.py`,
- deterministic catalog-row and CSV assertions,
- cross-domain collision rejection coverage,
- unified CLI registration and forwarding coverage,
- successful Quality run #162.

## Result

The regression package is accepted without corrective follow-up.

The contract module now guards:

- controlled domain and item-code ordering,
- price, technical and equipment metadata,
- aggregation of multiple fuel contexts,
- `equal`, `different` and `not_comparable` counts,
- deterministic CSV serialization and parsing,
- rejection of item-code collisions across domains,
- forwarding through the unified CLI.

The `load_tests` integration preserves the verified 410-test documentation baseline while still failing unittest discovery if a catalog contract assertion fails.

## Remaining usability gap

The catalog currently exposes only `context_count`. This identifies that six technical codes have two fuel contexts, but users still cannot discover the actual context values from the catalog CSV.

For example, the catalog can report `context_count = 2` for a fuel-sensitive item without showing that the values are `fuel_type_code=lpg` and `fuel_type_code=petrol`.

## Selected next package

### Configuration Comparison Item Catalog Context Values

Proposed scope:

- add a deterministic `contexts` column to the catalog CSV,
- serialize unique contexts in lexical order with a controlled separator,
- retain `context_count` as the machine-friendly cardinality,
- preserve one empty context for configuration-level equipment,
- expose market/currency context for prices and fuel context for technical items,
- extend the existing catalog contract guard,
- update the catalog contract documentation,
- make no changes to master data, evidence, comparison report generation, quality steps or workflow structure.

## Decision

The catalog regression package is complete. The next package is **Configuration Comparison Item Catalog Context Values**.