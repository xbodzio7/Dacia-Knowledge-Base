# Data Products v1.1.1 Publication

Date: 2026-07-22

## Published identity

- GitHub Release: `data-products-v1.1.1`
- Release ID: `358341344`
- Published at: `2026-07-22T21:42:16Z`
- Exact tag target and source commit: `b333f74e8426993e797a79c2e8621bd2f0f7bf4e`
- Source Pull Request: `#201`
- Verified Pull Request head: `63b7b622f5a55d35f1283877737b55c6bee78451`
- Quality workflow: `#1149`

The tag resolves exactly to the merged `main` commit above. The release is final, not a draft and not a prerelease.

## Public assets

| Asset | Size | SHA-256 |
| --- | ---: | --- |
| `dacia-knowledge-base-data-products-v1.1.1.zip` | 45,161,275 bytes | `273fa6f507aa3e0143c650b0d1236effeb3129ac999be775ce9566a10b2553d0` |
| `data-product-release-manifest.json` | 18,215 bytes | `c67c500044acbd9731e7a26a10583f69ec7cc446047571cc3d8b7011b2bb455d` |
| `SHA256SUMS` | 213 bytes | `e163ae071e24233e6879059b0fc37c30ba14472a74327c21a260f66f7797dd36` |

GitHub's recorded API digests match the independently calculated SHA-256 values for all three uploaded assets.

## Release contents

- 67 active configurations;
- 17 independent comparison scopes;
- 75 deterministic archive members;
- complete shortlist in JSON, Markdown, CSV and self-contained HTML;
- comparison bundles, provenance and the existing deterministic workbook;
- performance correction for equipment selection without any data or comparison-semantic changes.

## Verification

The exact HTML from the release archive was exercised in Chromium with seven consecutive equipment selections. No JavaScript errors occurred; synchronous click processing measured approximately 8-17 ms.

All 15 Pull Request workflows passed on the final source commit. The public assets were then downloaded again from the published GitHub Release and accepted by `data-product-release --verify`. Publication audit result: `PASS`.

## Immutability

The release assets and tag are immutable. Later corrections or extensions must use a new semantic version and must not replace or rewrite `data-products-v1.1.1`.
