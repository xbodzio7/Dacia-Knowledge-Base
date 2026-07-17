# Configuration Comparison Pair Summary

## Milestone review

The reporting milestone now provides:

- full structured JSON and Markdown comparison reports,
- a 305-row flat differences CSV,
- domain, item-code and exact-context filters,
- a 109-row item and context catalog,
- a manifest-verified Quality artifact bundle.

The remaining usability gap is pair-level analysis. A consumer can inspect every difference row, but cannot sort or rank configuration pairs without parsing nested JSON or aggregating the differences CSV while separately accounting for equal and not-comparable states.

## Candidate ranking

1. **Pair Summary CSV** — small deterministic surface, direct spreadsheet value, reuses existing summary semantics.
2. Full comparison matrix CSV — broader but substantially larger and overlaps the JSON report.
3. Excel export — valuable but introduces a dependency and workbook contract.
4. Model-level comparison — requires broader source-backed model coverage.

The Pair Summary CSV was selected because it closes the pair-level analysis gap without adding comparison semantics.

## Command

```bash
python tools/dkb.py configuration-comparison-pair-summary \
  --csv ../configuration-comparison-pair-summary.csv
```

Optional filters are shared with the report collector:

```bash
python tools/dkb.py configuration-comparison-pair-summary \
  --pair-type same_version_different_transmission \
  --csv ../same-version-transmission-pairs.csv
```

## Row contract

The output has one row per selected configuration pair and 24 columns:

- pair code and pair type,
- left and right configuration, version and transmission,
- comparisons, equal, different and not-comparable counts for prices,
- the same four counters for technical values,
- the same four counters for equipment,
- total comparisons, equal, different and not-comparable counts.

The command reads the existing `pair["summary"]` values and only flattens them. It does not recalculate or reinterpret comparison states.

## Verified full snapshot

The full active scope contains:

- 21 configuration pairs,
- 115 comparisons per pair,
- 2,415 total comparison cells,
- 305 total differences.

Pair types are distributed as:

| Pair type | Pairs |
| --- | ---: |
| `different_version_same_transmission` | 11 |
| `different_version_different_transmission` | 8 |
| `same_version_different_transmission` | 2 |
| `same_version_same_transmission` | 0 |

The sum of price, technical and equipment differences in the pair summary must exactly match the aggregate counts in `configuration-comparison.json`.

## Quality artifact

The Python 3.13 workflow publishes:

```text
configuration-comparison-pair-summary.csv
```

inside the existing `dacia-knowledge-base-build` artifact. The file is included in `artifact-manifest.json`, so its presence, size and SHA-256 are verified with the rest of the bundle.

Artifact name, archive layout, retention and existing files remain unchanged.

## Regression contract

`tests/configuration_comparison_pair_summary_contract.py` verifies:

- flattening of the existing fixture summary,
- deterministic CSV and stable 24-column schema,
- header-only output for an empty pair filter,
- CLI output,
- 21-pair full-snapshot count,
- pair-type distribution,
- 115 comparisons per pair,
- aggregate parity with the full comparison report.

The contract runs explicitly on Python 3.10 and Windows without changing the established 410-test documentation baseline.

## Scope boundary

This package does not change:

- master data,
- comparison collection or state semantics,
- JSON, Markdown or difference CSV,
- existing filters,
- item catalog columns,
- artifact names, paths or retention,
- evidence classifications.
