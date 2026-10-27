# Configuration Comparison Bundle CLI

## Goal

Connect explicit shortlist selections to the existing source-backed comparison engine without creating cross-model, cross-powertrain or otherwise heterogeneous comparison denominators.

## Command

```bash
python tools/dkb.py configuration-comparison-bundle \
  --shortlist-json ../configuration-shortlist.json \
  --configuration-code duster_iii_expression_ecog100_4x2_manual \
  --output-directory ../comparison-bundle
```

Direct configuration codes and shortlist JSON reports may be combined. Their union is deduplicated deterministically.

## Scope grouping

The command discovers the 13 current independent reporting scopes and validates that every active configuration is mapped exactly once. Selected codes are grouped by their existing completeness specification.

- groups with at least two selected configurations generate comparisons;
- groups containing one selected configuration are recorded as singletons;
- configurations from different groups are never paired;
- unknown or unmapped codes fail before output publication.

## Evidence contract

For every comparable group the engine creates temporary specifications containing only the selected configurations:

- the completeness `configurations` list is filtered;
- the evidence `decisions` list is filtered by configuration code;
- technical and equipment denominators remain unchanged;
- the existing comparison engine and all existing renderers are invoked without modified comparison semantics.

This preserves strict evidence validation, including Sandero scopes where an unfiltered evidence file correctly rejects decisions referring to configurations outside the selected subset.

## Outputs

Each comparable scope produces:

- a complete JSON comparison report;
- a readable Markdown comparison report;
- a flat CSV containing actual differences;
- a self-contained interactive HTML comparison report.

The output directory also contains `comparison-bundle-manifest.json` with:

- selection sources and deduplication counts;
- selected configuration codes;
- comparable and singleton groups;
- pair and difference counts;
- evidence summaries and report dates;
- relative file paths, sizes and SHA-256 digests;
- `cross_scope_pairs_generated: false`.

## Transactional publication

All validation and report generation occurs in a temporary sibling directory. The requested output directory is published only after every group succeeds. A non-empty output directory is never overwritten, and failures remove all temporary files.

## Delivery

The `Configuration Comparison Bundle` workflow generates the existing automatic-under-100000 PLN shortlist, adds one Duster singleton and publishes:

- one Jogger comparison;
- one Sandero comparison;
- one explicit Duster singleton entry;
- eight report files and the bundle manifest.

The workflow verifies every recorded file size and SHA-256 before upload.

## Scope boundary

The package does not add cross-scope pairs, new denominators, ranking, preference scoring, inferred values, weakened evidence validation, singleton comparisons or browser-side report generation.
