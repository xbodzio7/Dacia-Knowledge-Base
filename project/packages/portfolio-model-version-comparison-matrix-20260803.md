# Portfolio Model Version Comparison Matrix

Date: 2026-08-03

Package ID: `portfolio_model_version_comparison_matrix_001`

Status: **complete**

## Result

A deterministic comparison product projects every active canonical Dacia version into JSON, CSV and standalone HTML.

Each row is bounded by one exact `version_code` and aggregates only its existing active configurations:

- exact model and version identifiers and names;
- configuration count and exact configuration codes;
- recorded catalog-price state and range;
- recorded seat state and values;
- transmissions and powertrain labels;
- existing reporting-scope memberships split into single-model and mixed-model scopes;
- explicit source, relationship and configuration provenance coverage;
- earliest and latest registered source dates.

## Verified baseline

- 6 model families;
- 22 active canonical versions;
- 81 active configurations represented exactly once;
- 22 preserved reporting scopes;
- 33 provenance sources;
- 251 source-to-configuration relationships;
- 0 configurations without provenance;
- the canonical repository baseline remains 1862 tests because version-matrix checks extend the existing family-product test method.

## Formats

- `data/reporting/portfolio_model_version_comparison_matrix.json` — structured version-bounded projection with explicit semantic flags;
- `data/reporting/portfolio_model_version_comparison_matrix.csv` — stable flat export with one row per active version and pipe-delimited list fields;
- `data/reporting/portfolio_model_version_comparison_matrix.html` — standalone side-by-side table with no script, image or external dependency.

## Materialization evidence

Bounded workflow run `30853152840` regenerated all three outputs from canonical branch data, integrated the regression checks into the existing ten-method family-product suite, passed the focused tests and canonical project-state check, committed the byte-stable outputs and removed its own workflow from the final package.

## Safety boundary

The product creates no configuration pair or cross-scope pair, performs no ranking or recommendation and infers no missing value. It changes no source data, master data, schema, model or architecture. Unstated values remain `not_stated`.

## Verification

```bash
python -m unittest -q tests.test_portfolio_model_family_summary
python tools/portfolio_model_version_comparison_matrix.py \
  --json data/reporting/portfolio_model_version_comparison_matrix.json \
  --csv data/reporting/portfolio_model_version_comparison_matrix.csv \
  --html data/reporting/portfolio_model_version_comparison_matrix.html
python tools/dkb.py project-state --check
```
