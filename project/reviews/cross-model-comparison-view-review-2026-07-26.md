# Cross-Model Comparison View Review

Date: 2026-07-26

## Decision

Select **Scope-Preserving Model Navigation** for the next cross-model consumer surface.

The new view will not create a second comparison engine. It will provide:

1. five model-family overview cards;
2. a directory of the nineteen existing reporting scopes;
3. launch points into comparison only inside an existing scope.

## Verified inventory

The published `data-products-v1.7.0` baseline contains:

- 72 active configurations;
- five model families;
- nineteen reporting scopes;
- 114 pairs generated only inside those scopes;
- complete current catalogue-price coverage for all 72 configurations;
- 124 technical comparison facets and 110 equipment facets;
- one scope assigned to every active configuration.

### Model families

| Model | Configurations | Versions | Exclusive scopes | Shared scopes | Current catalogue range |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sandero | 4 | 2 | 1 | 1 | 68,000–80,500 PLN |
| Sandero Stepway | 5 | 3 | 1 | 1 | 71,700–89,400 PLN |
| Duster | 27 | 5 | 8 | 0 | 82,000–123,600 PLN |
| Jogger | 22 | 4 | 4 | 0 | 77,900–118,050 PLN |
| Bigster | 14 | 4 | 4 | 0 | 101,400–137,600 PLN |

The price range is an aggregate of exact latest recorded catalogue prices with full coverage, not a ranking or value judgement.

## Existing mixed-model scope

Eighteen scopes contain one model family. The established `sandero_ecog120_manual` scope contains five exact Eco-G 120 manual configurations from both Sandero and Sandero Stepway and creates ten pairs under one completeness and evidence contract.

That scope is preserved exactly. Its existence does not establish comparability between other models, powertrains or reporting scopes.

## Selected view

### Layer 1 — model-family overview

Each model card may show only source-stable navigation metadata:

- model name and generation;
- body type and segment codes;
- number of active configurations and versions;
- exact current catalogue-price minimum and maximum with coverage count;
- recorded seat values, transmissions and powertrain labels;
- links to the reporting scopes containing that model.

An empty recorded-seat set remains `not stated`. Bigster and Duster must not be shown as zero-seat or assumed five-seat cars.

### Layer 2 — reporting-scope directory

The directory contains exactly nineteen cards. Every card shows its existing configuration count and homogeneous contract. The Sandero/Stepway manual card is visibly marked as shared between two model families.

### Layer 3 — existing comparison launch

Selecting a scope opens or generates only its existing within-scope comparison. Selecting model cards never synthesizes a pair.

## Rejected alternatives

### Global common-attribute matrix

Rejected because the intersection of attribute names does not prove equal measurement basis, fuel context, selected gear, cargo state, observation date or completeness denominator.

### Unrestricted cross-model pairing

Rejected because it bypasses the one-to-one mapping of configurations to reporting scopes and would introduce unsupported comparison semantics.

### Normalized model ranking

Rejected because the repository contains evidence, not consumer preference weights. Ranking and recommendations remain explicit non-goals of the public release contract.

## Implementation boundary

The next package, `Cross-Model Comparison View Foundation`, will add deterministic JSON and standalone HTML by reusing:

- the browser catalogue from `configuration_shortlist_html`;
- scope discovery from `configuration_comparison_bundle`;
- the existing official model-media registry;
- the current release and offline workspace pipeline.

It will not change master data, schema, reporting scopes or comparison calculations.

## Acceptance contract

- exactly five model cards and nineteen scope cards;
- all 72 active configurations represented once in the scope directory;
- complete price-coverage counts remain visible;
- the one mixed Sandero/Stepway scope is explicit and unchanged;
- Bigster and Duster seat values remain unknown unless directly recorded;
- no new pair, score, winner, recommendation or inferred value;
- deterministic JSON and fully offline standalone HTML.
