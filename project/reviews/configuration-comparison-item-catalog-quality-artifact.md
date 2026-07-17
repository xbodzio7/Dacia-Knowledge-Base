# Configuration Comparison Item Catalog Quality Artifact

## Decision

Publish the existing configuration-comparison item catalog as part of the standard GitHub Actions Quality artifact.

## Rationale

The comparison differences CSV supports filters by pair type, domain and item code. The item catalog is the discovery surface that explains which codes are valid, which contexts exist and how many comparisons fall into each state.

Before this package, the catalog command was available locally but was not included in the standard CI artifact bundle. Users inspecting a Quality run could download the comparison report and differences without receiving the corresponding code catalogue.

## Implementation

The Python 3.13 Quality job now runs:

```bash
python tools/dkb.py configuration-comparison-item-catalog \
  --csv "${RUNNER_TEMP}/configuration-comparison-item-catalog.csv"
```

after the full quality gate.

The generated file is uploaded in the existing `dacia-knowledge-base-build` artifact with the other seven-day reporting outputs.

## Artifact contract

The file name is:

```text
configuration-comparison-item-catalog.csv
```

It retains the existing deterministic columns:

- `domain`,
- `item_code`,
- `item_name`,
- `category`,
- `context_count`,
- `contexts`,
- `comparison_count`,
- `equal_count`,
- `different_count`,
- `not_comparable_count`.

The command remains the single implementation of catalog generation. The workflow does not duplicate report logic or hard-code the current 109-row baseline.

## Verified artifact

Quality run #176 published artifact `dacia-knowledge-base-build` with digest recorded by GitHub Actions. Inspection of the downloaded ZIP confirmed:

- exactly one `_temp/configuration-comparison-item-catalog.csv`,
- 109 data rows plus the CSV header,
- the expected ten-column header including `contexts`.

## Failure behavior

- catalog-generation failure fails the Python 3.13 job;
- missing catalog output fails artifact upload through `if-no-files-found: error`;
- the artifact remains retained for seven days;
- Python 3.10 and Windows contracts remain unchanged.

## Scope boundary

This package does not change:

- master data,
- comparison semantics,
- catalog row ordering or columns,
- local `quality` command stages,
- existing artifact names or retention,
- evidence classifications.
