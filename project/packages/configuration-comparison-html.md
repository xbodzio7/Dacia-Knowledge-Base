# Interactive Configuration Comparison HTML

## Goal

Turn the existing source-backed configuration comparison engine into a browser-ready data product that can be used without a Python environment, local server or knowledge of the underlying CSV schema.

## Scope

The package adds one deterministic, self-contained HTML representation of an existing configuration comparison report. It does not change comparison denominators, pair selection, evidence classifications or source-backed values.

The HTML report exposes:

- the report date and selected configuration scope;
- aggregate price, technical and equipment comparison counts;
- every pair and every comparison item, including equal and not-comparable results;
- recorded values, interval bounds, equipment states, source codes and observation dates;
- explicit `not_stated`, `out_of_scope`, `ambiguous` and `not_applicable` states;
- client-side filtering by text, domain and comparison result;
- a difference-only view enabled by default;
- responsive and printable presentation.

## Command

```bash
python tools/dkb.py configuration-comparison \
  --completeness-spec data/reporting/sandero_ecog120_manual_completeness.json \
  --evidence-spec data/reporting/sandero_ecog120_manual_gap_evidence.json \
  --as-of 2026-06-26 \
  --html ../sandero-comparison.html
```

`--html` composes with the existing JSON, Markdown, CSV and pair-type outputs. CSV-only domain, item and context filters do not reduce the complete browser report.

## Delivery

The `Configuration Comparison HTML` workflow publishes two current Sandero browser reports and a SHA-256 artifact manifest for every pull request and manual run. The files contain embedded CSS and JavaScript and have no external runtime or network dependencies.

## Guarantees

- deterministic UTF-8 output;
- HTML escaping for all data-derived text;
- no inferred values or hidden gap conversion;
- no external scripts, stylesheets, fonts or analytics;
- existing JSON, Markdown and CSV schemas remain unchanged;
- current reporting workflows and tests remain valid.
