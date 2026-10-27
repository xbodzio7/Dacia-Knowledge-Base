# Portfolio Model Family Comparison Matrix

Date: 2026-08-03

Package ID: `portfolio_model_family_comparison_matrix_001`

Status: **complete**

## Result

A deterministic comparison product now projects the six verified portfolio model families into JSON, CSV and standalone HTML outputs.

The matrix contains one row per canonical family and preserves only fields already present in `portfolio_model_family_summary.json`:

- configuration and version counts;
- recorded catalog-price state and range;
- recorded seat state and values;
- transmission and powertrain labels;
- reporting-scope counts split into exclusive and shared membership;
- explicit source, relationship and configuration provenance coverage;
- earliest and latest registered source dates.

## Verified baseline

- 6 model families;
- 81 active configurations;
- 22 unique reporting scopes;
- 33 provenance sources;
- 251 source-to-configuration relationships;
- 0 configurations without provenance;
- Duster and Bigster seat values remain `not_stated`;
- the canonical repository baseline remains 1862 tests because matrix assertions extend the existing family-product suite.

## Formats

- `data/reporting/portfolio_model_family_comparison_matrix.json` — structured projection with explicit semantic flags;
- `data/reporting/portfolio_model_family_comparison_matrix.csv` — stable flat export with pipe-delimited list fields;
- `data/reporting/portfolio_model_family_comparison_matrix.html` — standalone side-by-side table with no script, image or external dependency.

## Safety boundary

The product creates no configuration pair or cross-scope pair, performs no ranking or recommendation and infers no missing value. It changes no source data, master data, schema, model or architecture.

## Verification

```bash
python -m unittest -q tests.test_portfolio_model_family_summary
python tools/portfolio_model_family_comparison_matrix.py \
  --json data/reporting/portfolio_model_family_comparison_matrix.json \
  --csv data/reporting/portfolio_model_family_comparison_matrix.csv \
  --html data/reporting/portfolio_model_family_comparison_matrix.html
python tools/dkb.py project-state --check
```
