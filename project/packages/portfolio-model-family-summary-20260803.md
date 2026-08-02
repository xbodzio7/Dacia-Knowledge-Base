# Portfolio Model Family Summary

Date: 2026-08-03

Package ID: `portfolio_model_family_summary_001`

Status: **complete**

## Result

The package adds deterministic JSON, Markdown and standalone HTML summaries for the current source-backed portfolio:

- 6 canonical model families;
- 81 active configurations;
- 22 existing reporting scopes;
- 130 existing within-scope pairs;
- 33 distinct provenance sources;
- 251 explicit source-to-configuration relationships;
- zero configurations without provenance.

Each family preserves exact configuration codes, price coverage, recorded seat states, powertrain and transmission labels, exclusive/shared reporting scopes, source codes, source types, document dates, covered configurations and source SHA-256 values.

## Formats

- `data/reporting/portfolio_model_family_summary.json`;
- `data/reporting/portfolio_model_family_summary.md`;
- `data/reporting/portfolio_model_family_summary.html`.

The HTML output is standalone and contains no script, remote image or runtime network dependency.

## Safety boundary

The package does not create cross-scope pairs, rank models, recommend configurations, infer missing values or modify master data. Existing unknown states remain explicit.

## Next package

`portfolio_model_family_summary_release_integration_001` will integrate the verified outputs into the versioned release archive, public-download verification and offline workspace navigation.

## Verification

```bash
python tools/generate_portfolio_model_family_summary_package_20260803.py --verify
python -m unittest tests.test_portfolio_model_family_summary
python tools/dkb.py project-state --check
python tools/dkb.py quality --concise
```
