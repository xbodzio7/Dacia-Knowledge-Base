# Cross-Model Comparison View Closure Review

Date: 2026-07-26

## Decision

The `Cross-Model Comparison View Foundation` milestone is closed.

The repository now generates a deterministic machine-readable inventory and a standalone static navigation page over five model families and nineteen existing reporting scopes. The products preserve every established comparison boundary and introduce no new pair calculation.

## Verified product

The closure contract verifies:

- five model-family cards;
- nineteen reporting-scope cards;
- seventy-two active configurations mapped exactly once;
- one hundred fourteen pairs, all generated inside existing scopes;
- eighteen single-model scopes;
- the existing mixed `sandero_ecog120_manual` scope unchanged at five configurations, ten pairs and fifty-six technical slots;
- complete recorded catalogue-price coverage for all seventy-two configurations.

## Outputs

The deterministic release contains:

- `cross-model/cross-model-comparison-view.json`;
- `cross-model/cross-model-comparison-view.html`.

Their addition increases the release archive inventory from eighty-three to eighty-five members.

The JSON contains seventy-six exact comparison-report paths across nineteen scopes and two navigation paths. The HTML exposes fifty-seven local file launches: HTML, JSON and CSV differences for every existing scope.

Every local file target must exist in the generated release archive. Paths may not escape the release workspace.

## Offline and deterministic behavior

The HTML is self-contained, uses no JavaScript and has no runtime image dependency. It may contain official model-page provenance links, but all product navigation works locally from the extracted release workspace.

Repeated generation from unchanged repository data must produce byte-identical JSON and HTML.

## Unknown handling

Bigster and Duster have no exact recorded seat values in the current catalog. Their machine-readable state remains `not_stated`, and the HTML displays `nie podano`.

The product may not substitute zero seats, assume five seats or otherwise infer a missing model fact.

## Semantic boundary

The closure verifies that the product records and preserves:

- `cross_scope_pairs_generated = false`;
- `ranking_generated = false`;
- `recommendations_generated = false`;
- `inferred_values_generated = false`.

The milestone changes no master CSV data, schema or comparison engine.

## CLI

The unified command remains:

```bash
python tools/dkb.py cross-model-comparison-view \
  --json ../cross-model-comparison-view.json \
  --html ../cross-model-comparison-view.html
```

At least one output is required, and either or both formats may be generated.

## Repository baseline

The closed milestone retains:

- 46 master CSV files;
- 9688 master rows;
- 2949 scalar configuration values;
- 244 configuration-value ranges;
- 4754 equipment-availability records;
- 385 attributes.

The closure package raises the automated-test baseline to 998.

## Next package

`Post-Cross-Model Priority Selection Review` — rank the highest-value next reporting, data, import and tooling candidates using repository readiness and evidence constraints, without implementing a candidate in the review package.
