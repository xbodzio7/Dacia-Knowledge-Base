# Data Products v1.8.1 Publication

Date: 2026-07-27

## Published identity

- GitHub Release: `data-products-v1.8.1`
- Release ID: `360138130`
- Published at: `2026-07-26T23:05:03Z`
- Exact tag target and source commit: `0b7009fd1950693e347638a6b96756aeefb43b8a`
- Source preparation Pull Request: `#290`
- Preflight Pull Request: `#291`, run `30223603489`
- Publication Pull Request: `#292`, run `30224467755`
- Independent audit Pull Request: `#293`, run `30225040623`

The final tag resolves exactly to the squash-merged preparation commit above. The release is neither a draft nor a prerelease.

## Public assets

| Asset | Asset ID | Size | SHA-256 |
| --- | ---: | ---: | --- |
| `SHA256SUMS` | `490767593` | 213 bytes | `ca59fb187c8fbdcbacf7c62d0c65559a8f604defc5634b1d7fe257df7f7e668e` |
| `dacia-knowledge-base-data-products-v1.8.1.zip` | `490767591` | 62,141,954 bytes | `3bb8ba7c48195651bbe24cae042560273c5e4083467c01b203bb07dab7401bc5` |
| `data-product-release-manifest.json` | `490767592` | 20,607 bytes | `f4ed40ed7e469876c80ee95c6b1ad18fcf6c86f215934ab5942373f2889a54fd` |

GitHub API digests match the independently calculated SHA-256 values for all three downloaded assets.

## Release contents

- 72 active configurations;
- 19 independent reporting scopes;
- 114 within-scope configuration pairs;
- 1,695 recorded differences;
- 85 deterministic archive members;
- 124 technical comparison facets;
- 110 equipment facets;
- JSON, Markdown, CSV, HTML and XLSX products.

Every active configuration remains in exactly one reporting scope. The release creates no cross-scope pair, ranking, recommendation or inferred value.

## Patch behavior

The patch restores buyer-facing equipment filtering in the public shortlist without changing catalogue data:

- 108 equipment choices are initially visible;
- searching for `kamera` leaves one visible choice;
- selecting the rear-view camera returns 66 of 72 configurations;
- missing, unknown and explicitly unavailable evidence remains excluded;
- model choices are ordered by minimum current catalogue price: Sandero, Sandero Stepway, Jogger, Duster and Bigster.

## Public workspace audit

The independent audit downloaded the public release from scratch through the repository downloader and verified:

- three canonical assets with exact IDs, sizes and SHA-256 values;
- 85 verified content files;
- 83 local links in deterministic `index.html`;
- workspace index SHA-256 `653a505102a15dc66d770b82612e18da324c0299162f644b7192628911c54b80`;
- 72 configurations, 19 scopes and 114 within-scope pairs;
- 76 cross-model comparison paths, two navigation paths and 57 local links in the static cross-model HTML;
- `not_stated` seat counts for Bigster and Duster;
- exact public shortlist filter semantics and model price ordering.

Publication audit result: `PASS`.

## Verification

The preflight rebuilt all three assets twice from the exact source commit, proved byte identity, verified 85 unique archive members and ran the real Chromium equipment-filter smoke test.

The publication workflow rebuilt the same candidate, required the recorded sizes and SHA-256 values, created the public tag and release, downloaded all three assets again and compared them byte for byte.

A separate workflow then downloaded the public workspace from scratch, verified the tag-to-commit binding, asset IDs, API digests, content files, links, shortlist behavior, model order and all non-inference boundaries. All 15 final workflows passed on the clean publication and audit Pull Requests.

## Data boundary

This patch release changes interface behavior only. It adds no source observations, no comparison pairs and no inferred values. Older public releases, including `data-products-v1.8.0`, remain immutable.

## Next package

`Cross-Model Navigation Usability Review` — resume the deferred review of consumer discoverability for the published cross-model products, including whether the deterministic workspace index should expose a dedicated entry point, without changing comparison semantics in the review package.

## Immutability

The tag and public assets are immutable. Later corrections, data additions or interface changes must use a new semantic version and must not replace or rewrite `data-products-v1.8.1`.
