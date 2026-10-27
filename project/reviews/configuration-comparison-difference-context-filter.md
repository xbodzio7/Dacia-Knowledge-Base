# Configuration Comparison Difference Context Filter

## Decision

Add an optional exact `--difference-context` filter to the flat configuration-differences CSV.

The filter is exposed through the unified command:

```bash
python tools/dkb.py configuration-comparison \
  --difference-context fuel_type_code=lpg \
  --csv ../configuration-comparison-differences-lpg.csv
```

## Context contract

Accepted values come from `configuration-comparison-item-catalog.csv` and use the catalog representation rather than the more detailed display context already stored in the differences CSV.

The current active comparison scope exposes five exact contexts:

```text
<empty>
fuel_type_code=
fuel_type_code=lpg
fuel_type_code=petrol
market=PL;currency_code=PLN
```

Use this syntax for the empty equipment context:

```bash
python tools/dkb.py configuration-comparison \
  --difference-context= \
  --csv ../configuration-comparison-equipment-differences.csv
```

Price context deliberately omits `price_type`. The item code already identifies the price type, so this command composes without duplication:

```bash
python tools/dkb.py configuration-comparison \
  --difference-domain prices \
  --difference-item-code catalog_gross \
  --difference-context 'market=PL;currency_code=PLN' \
  --csv ../catalog-gross-pln-differences.csv
```

The existing CSV `context` field is unchanged. Price rows continue to contain the detailed value:

```text
market=PL;price_type=catalog_gross;currency_code=PLN
```

## Validation order

The requested context is validated against the full active comparison report before applying:

- pair type,
- difference domain,
- item code,
- difference-row selection.

A known context that has no rows after the other filters produces a deterministic header-only CSV. An unknown context fails with `unsupported difference context`.

## Composition

The context filter composes with:

- `--pair-type`,
- `--difference-domain`,
- `--difference-item-code`.

It affects only the flat CSV. JSON, Markdown, summaries, evidence counts and the unfiltered CSV remain unchanged.

## Verified snapshot

The active full report contains 305 difference rows. Exact context counts are:

| Context | Difference rows |
| --- | ---: |
| empty equipment context | 24 |
| `fuel_type_code=` | 144 |
| `fuel_type_code=lpg` | 61 |
| `fuel_type_code=petrol` | 55 |
| `market=PL;currency_code=PLN` | 21 |

For `co2_emissions`, the exact filters return:

- 17 LPG differences,
- 17 petrol differences.

For `same_version_different_transmission`, the corresponding counts are:

- 0 empty-context equipment rows,
- 10 rows for `fuel_type_code=`,
- 6 LPG rows,
- 5 petrol rows,
- 2 PLN price rows.

## Compatibility boundary

The original `configuration_comparison.py` remains the implementation of report collection and all existing output formats. `configuration_comparison_context.py` adds only the context-filtering layer.

The unified CLI routes normal calls to the original implementation. It routes calls containing `--difference-context` and command-specific help to the compatibility layer. Existing script paths, function signatures and no-filter behavior therefore remain unchanged.

## Regression contract

`tests/configuration_comparison_context_filter_contract.py` verifies:

- exact context discovery,
- empty equipment context handling,
- price context normalization,
- composition with pair, domain and item filters,
- validation against the full report before pair filtering,
- unknown-context rejection,
- unchanged JSON, Markdown, CSV schema and default 305-row output,
- full-snapshot context counts,
- unified CLI routing.

The contract runs explicitly on Python 3.10 and Windows without changing the established 410-test documentation baseline.

## Scope boundary

This package does not change:

- master data,
- report collection or comparison semantics,
- JSON or Markdown,
- the difference CSV schema or detailed context values,
- item catalog columns,
- Quality artifact names, paths or retention,
- evidence classifications.
