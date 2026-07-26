# Data Products v1.8.0 Publication

Date: 2026-07-26

## Published identity

- GitHub Release: `data-products-v1.8.0`
- Release ID: `360115681`
- Published at: `2026-07-26T20:50:24Z`
- Exact tag target and source commit: `becd218228e3f4f0cdd312b0ed836ade487422b1`
- Source preparation Pull Request: `#284`
- Verified source head: `c6d7fab8d20b7b66e38517084060e92c9d9f8a18`
- Quality workflow: `#2004`
- Preflight Pull Request: `#285`, run `30219704364`
- Publication Pull Request: `#286`, run `30219809423`
- Independent audit Pull Request: `#287`, run `30220008441`

The tag resolves exactly to the squash-merged `main` commit above. The release is final, not a draft and not a prerelease.

## Public assets

| Asset | Asset ID | Size | SHA-256 |
| --- | ---: | ---: | --- |
| `SHA256SUMS` | `490686122` | 213 bytes | `8649769104a5b695c2b6e21177c032523fdc0a694ea11931ce95a6a5ae428596` |
| `dacia-knowledge-base-data-products-v1.8.0.zip` | `490686120` | 62,141,187 bytes | `2af02fc148446eb3789ed4e19f32c52e54c484464ca1cdb2ba1048ae02b7cec9` |
| `data-product-release-manifest.json` | `490686121` | 20,606 bytes | `af9366e92543a8aadca5e0a94a43391d202bce71f684bf3d9583913764f0de3b` |

GitHub's API digests match the independently calculated SHA-256 values for all three downloaded assets.

## Release contents

- 72 active configurations;
- 19 independent and comparable reporting scopes;
- 114 within-scope configuration pairs;
- 1,695 recorded differences;
- 85 deterministic archive members;
- JSON, Markdown, CSV, HTML and XLSX products;
- 124 technical comparison facets;
- 110 equipment facets.

Every active configuration belongs to exactly one scope. The release generates no cross-scope pair, ranking, recommendation or inferred value.

## New cross-model products

The release adds:

- `cross-model/cross-model-comparison-view.json`;
- `cross-model/cross-model-comparison-view.html`.

The products provide scope-preserving navigation over five model families and nineteen existing reporting scopes. The JSON contains seventy-six exact comparison-report paths and two navigation paths. The static HTML contains fifty-seven local file links, no JavaScript and no runtime image dependency.

Bigster and Duster seat counts remain `not_stated` and are displayed as `nie podano`. No missing value is replaced with zero or an assumed five-seat value.

## Offline workspace audit

The public downloader materialized the release into the canonical read-only workspace and the independent verifier accepted it:

- three canonical assets;
- 85 verified content files;
- 83 local links in deterministic `index.html`;
- workspace index SHA-256 `ad2074a55e110ac11a518b441cbdc51864d5c7223cba75812c5b719facdf9b24`;
- exact release tag, source commit and snapshot date `2026-07-25`.

The link count and content count measure different contracts. The index contains four primary product links, seventy-six existing scope-report links and three original-asset links. Both cross-model members are verified in `contents` and all of their local targets pass the audit. Whether the main workspace index should expose a dedicated cross-model entry point is deferred to the next usability review rather than changing this immutable release.

## Verification

All 15 source Pull Request workflows passed on the final clean source head, including 1,014 tests, Python 3.10, Python 3.13, the full Python 3.14 quality and artifact gate, Windows, HTML, workbook, comparison, selection-export and versioned-release verification.

The preflight rebuilt the candidate twice from the exact merged `main` commit, proved byte identity, verified both candidates, materialized the canonical offline workspace and established final sizes and SHA-256 values before publication.

The publication workflow rebuilt the same candidate, required those exact identities, created the tag and release, re-downloaded all three public assets and compared them byte for byte.

Finally, an independent workflow downloaded the public release through the repository downloader, verified the tag-to-commit binding, recalculated asset identities, checked all 85 content files, verified the deterministic workspace and audited the complete cross-model JSON and HTML payload. Publication audit result: `PASS`.

## Data boundary

This release publishes the current evidence-backed repository state. It does not resolve deferred exact-configuration evidence, ambiguous source relationships or missing exact Spring sources. Missing evidence remains unknown rather than unavailable, and no comparison crosses an independent reporting scope.

## Immutability

The release assets and tag are immutable. Later corrections, source-backed additions or interface changes must use a new semantic version and must not replace or rewrite `data-products-v1.8.0`.
