# Portfolio Source Coverage Matrix

Date: 2026-08-04

Package ID: `portfolio_source_coverage_matrix_001`

Status: **complete**

## Result

A deterministic reporting product projects every active provenance source used by current active configurations into JSON, CSV and standalone HTML.

Each row is bounded by one exact registered `source_code` and preserves:

- source type, title, publisher, market, document date and status;
- exact registered external reference and local file path when present;
- exact registered SHA-256;
- relationship types and relationship count;
- exact covered configuration identities;
- exact covered active version identities;
- exact covered model-family identities and names.

## Verified baseline

- 33 used active provenance sources;
- 251 explicit source-to-configuration relationships preserved exactly once;
- 81 active configurations covered by provenance;
- 22 active canonical versions;
- 6 active model families;
- 0 active configurations without provenance;
- the canonical repository baseline remains 1862 tests because source-matrix checks extend the existing family-product regression method.

## Formats

- `data/reporting/portfolio_source_coverage_matrix.json` — structured source-bounded projection with explicit non-scoring and non-inference flags;
- `data/reporting/portfolio_source_coverage_matrix.csv` — stable flat export with one row per used source and pipe-delimited coverage lists;
- `data/reporting/portfolio_source_coverage_matrix.html` — standalone source-to-family/version/configuration coverage table with no script, image or external dependency.

## Safety boundary

The product changes no source or master data, schema, model or architecture. It creates no source quality, authority or preference score, performs no ranking or recommendation and infers no missing value. Coverage is derived only from exact registered source metadata and explicit `source_configurations` relationships.

## Verification

```bash
python -m unittest -q tests.test_portfolio_model_family_summary
python tools/portfolio_source_coverage_matrix.py \
  --json data/reporting/portfolio_source_coverage_matrix.json \
  --csv data/reporting/portfolio_source_coverage_matrix.csv \
  --html data/reporting/portfolio_source_coverage_matrix.html
python tools/dkb.py project-state --check
```
