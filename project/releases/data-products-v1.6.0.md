# Data Products v1.6.0 Publication

Date: 2026-07-24

## Published identity

- GitHub Release: `data-products-v1.6.0`
- Release ID: `359467989`
- Published at: `2026-07-24T18:11:04Z`
- Exact tag target and source commit: `539fba58d1ee2ef538c782b20e049be482d72988`
- Source Pull Request: `#230`
- Verified Pull Request head: `bacd6034c7d471b45948a9028b3f639e8e268854`
- Quality workflow: `#1255`

The tag resolves exactly to the merged `main` commit above. The release is final, not a draft and not a prerelease.

## Public assets

| Asset | Asset ID | Size | SHA-256 |
| --- | ---: | ---: | --- |
| `SHA256SUMS` | `488680880` | 213 bytes | `524b5ed2317c164fd43b7a63e6b8a9a311270cd2f03547c6a1c0e8f0155aa2da` |
| `dacia-knowledge-base-data-products-v1.6.0.zip` | `488680879` | 46,477,887 bytes | `286b7a8324efd8face2c49bb223bb414a2c2d5f8be368a9547c7fe7ab6677c32` |
| `data-product-release-manifest.json` | `488680877` | 19,154 bytes | `02158bc7839ee03eaa51c644817c7c2fc51e06ee551d7747456f97956281f803` |

GitHub's recorded API digests match the independently calculated SHA-256 values for all three downloaded assets.

## Release contents

- 69 active configurations;
- 18 independent comparison scopes;
- 79 deterministic archive members;
- official Dacia Polska photographs for Sandero, Sandero Stepway, Jogger, Duster and Bigster, each with a deterministic offline SVG fallback;
- configurator-style model, version, powertrain and transmission tiles;
- minimum and maximum catalogue price in one horizontal row;
- source-complete dynamic equipment facets that hide universal and incompletely covered features;
- explicit equipment-list search semantics;
- 88 source-backed technical comparison facets;
- 109 equipment facets;
- full basic, technical, fuel-context, range and equipment comparison with a global differences-only view.

## Published-browser audit

The exact `shortlist/configuration-shortlist.html` member extracted from the public release archive was audited after re-downloading the asset from GitHub Release. The embedded catalogue contains 69 configurations, 88 technical comparison facets, 109 equipment facets and five official model-media entries. The published HTML contains the required contracts for `Pokaż tylko różnice`, `Filtruj listę wyposażenia`, the combined minimum/maximum price controls and the offline `vehicle-photo-fallback`.

## Verification

All 15 source Pull Request workflows passed on the final source commit, including 717 tests, Windows, HTML, workbook, comparison, selection-export and versioned-release verification.

The public assets were then downloaded again from the published GitHub Release and accepted by `data-product-release --verify`. Exact sizes, SHA-256 values, GitHub API digests, tag target, release status, archive membership and published browser payload were independently audited. Publication audit result: `PASS`.

## Immutability

The release assets and tag are immutable. Later corrections or extensions must use a new semantic version and must not replace or rewrite `data-products-v1.6.0`.
