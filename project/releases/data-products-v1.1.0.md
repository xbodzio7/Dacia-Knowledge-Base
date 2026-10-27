# Data Products v1.1.0 Publication

Date: 2026-07-22

## Published identity

- GitHub Release: `data-products-v1.1.0`
- Release ID: `358319723`
- Published at: `2026-07-22T20:54:27Z`
- Exact tag target and source commit: `397958ba740c0b3b9370822d7e1d473c4829c11e`
- Source Pull Request: `#198`
- Verified Pull Request head: `801155a10e0f16787f93c85765eba0e8b3da0b15`
- Quality workflow: `#1139`

The tag resolves exactly to the merged `main` commit above. The release is final, not a draft and not a prerelease.

## Public assets

| Asset | Size | SHA-256 | Asset ID |
| --- | ---: | --- | ---: |
| `dacia-knowledge-base-data-products-v1.1.0.zip` | 45,160,526 bytes | `ce06feb4c81c4dc1a79f5977e9d057aebd0db254b72ede6bee10c2a1a6f453af` | `486410534` |
| `data-product-release-manifest.json` | 18,215 bytes | `9ac6598dde587571203d1c6cea5d7f0b32621cfa16570f2ee9f26e0129ec5ee2` | `486410538` |
| `SHA256SUMS` | 213 bytes | `7943fda211bebc793632d264881e96ac9ceb46d9918569467cf77bda25e3c1f2` | `486410537` |

GitHub's recorded API digests match the independently calculated SHA-256 values for all three uploaded assets.

## Release contents

- 67 active configurations;
- 17 independent comparison scopes;
- 75 deterministic archive members;
- complete shortlist in JSON, Markdown, CSV and self-contained HTML;
- comparison bundles, provenance and the existing deterministic workbook;
- corrected offline HTML selector with clean model labels, dependent version choices, one transmission choice and multiple powertrain choices.

## Verification

The exact HTML from the release candidate was exercised in Chromium. Model/version dependency, transmission selection, multiple powertrains, explicit configuration selection, export and reset all completed without JavaScript errors.

All 15 Pull Request workflows passed on the final HTML-only commit, including `Configuration Shortlist HTML`, `Configuration Selection Export`, `Versioned Data Product Release`, `Configuration Comparison Workbook` and the complete `Quality` workflow on Python 3.10, 3.13 and 3.14 plus Windows.

The public assets were then downloaded again from the published GitHub Release and accepted by the repository's independent `data-product-release --verify` contract. Publication audit result: `PASS`.

## Immutability

The release assets and tag are immutable. Later corrections or extensions must use a new semantic version and must not replace or rewrite `data-products-v1.1.0`.
