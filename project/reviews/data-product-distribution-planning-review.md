# Data Product Distribution Planning Review

## Decision status

`COMPLETE`

The existing offline data products will be distributed through manually published, versioned GitHub Releases. Actions artifacts remain short-lived CI evidence and are not the stable user delivery channel.

## Current delivery inventory

The repository already generates source-backed offline products in JSON, Markdown, CSV, HTML, SQLite and XLSX forms. The user-facing workflow includes configuration discovery, shortlist filtering, browser selection export, homogeneous comparison bundles and the six-sheet comparison workbook.

Current dedicated workflows publish these outputs with `actions/upload-artifact` and seven-day retention. This is appropriate for Pull Request verification, but it does not provide a durable versioned download surface.

The distribution package must reuse existing generators and manifests. It must not create a second comparison engine, a second shortlist contract or a new data snapshot.

## Options considered

| Channel | Strengths | Limitations | Decision |
| --- | --- | --- | --- |
| GitHub Releases | Durable versioned downloads, supports every current file type, stable release pages, repository-native permissions and checksummed assets | Requires an explicit publication contract and narrowly scoped write permission | **Select** |
| GitHub Actions artifacts | Already implemented and useful for CI evidence | Seven-day retention, run-oriented discovery and no durable release identity | Retain for CI only |
| GitHub Pages | Strong browser access for HTML | Does not naturally distribute JSON, CSV, SQLite or XLSX; requires a separate deployment surface and mutable site semantics | Defer |
| Commit generated products to `main` | Direct repository visibility | Duplicates generated outputs, expands history and mixes source with publications | Reject |
| External object storage or package registry | Flexible hosting | Adds credentials, service lifecycle, cost and a new distribution dependency | Reject |

## Selected release identity

- Release tags use `data-products-vMAJOR.MINOR.PATCH`.
- Publication is initiated manually through `workflow_dispatch` from `main`.
- The requested version must be a normalized semantic version and must not already exist as a tag or release.
- The release tag points to the exact tested `main` commit used to build the assets.
- Existing releases and assets are never overwritten, deleted or replaced by the workflow.
- GitHub release timestamps remain platform metadata; generated assets contain no runtime timestamp.

This identity separates product-release versions from source-document dates. Source observation dates remain inside the existing reports and workbook.

## Canonical release assets

Each release publishes exactly three top-level assets:

1. `dacia-knowledge-base-data-products-vMAJOR.MINOR.PATCH.zip`;
2. `data-product-release-manifest.json`;
3. `SHA256SUMS`.

The ZIP contains:

- `shortlist/` with the complete active-configuration JSON, Markdown, CSV and self-contained HTML;
- `comparison-bundle/` generated from that complete shortlist selection, preserving all independent reporting scopes, singleton handling, companion reports, bundle manifest and six-sheet XLSX workbook;
- `RELEASE_NOTES.md` with the release version, tested commit and a concise inventory;

The release workflow does not publish the Quality log or internal gap-review working reports as user products. Those remain available through the existing Quality artifact.

The release manifest remains a standalone asset and records the final ZIP hash. It is not copied into the ZIP because that would create an impossible self-reference between the manifest and the archive containing it.

## Manifest contract

The deterministic release manifest records:

- schema version;
- data-product release version;
- tested repository commit SHA;
- selected configuration count and independent scope count;
- relative path, media type, byte size and SHA-256 for every file inside the ZIP;
- ZIP filename, byte size and SHA-256;
- absence of cross-scope pairs, ranking, recommendations and inferred values.

Entries are ordered by relative path. JSON uses stable formatting and contains no runtime timestamp, workflow run ID or temporary path.

`SHA256SUMS` contains hashes for the ZIP and standalone manifest in filename order.

## Publication workflow boundary

The implementation workflow will have two stages.

### Build and verify

- run on Pull Requests and manual dispatch with read-only repository permissions;
- execute focused distribution tests and the existing bundle/shortlist tests;
- generate the complete shortlist and full-portfolio comparison bundle from the checked-out commit;
- assemble the deterministic ZIP, manifest and checksums;
- verify every recorded file path, size and hash;
- publish temporary Actions artifacts for review.

### Publish release

- run only for manual dispatch on `main` after the build stage succeeds;
- grant `contents: write` only to the publication job;
- reject non-`main` refs, malformed versions and existing tags/releases before any write;
- create the tag and release at the tested commit and upload the three exact verified assets;
- use the repository-provided `GITHUB_TOKEN` without external credentials;
- never mutate a previously published release.

No scheduled, push-triggered or automatic release is selected for the first implementation package.

## Validation contract

The implementation must verify:

1. semantic release-version validation;
2. complete 53-configuration shortlist generation;
3. one-to-one mapping into the current independent reporting scopes;
4. full bundle and workbook generation without cross-scope pairs;
5. fixed release directory and archive layout;
6. manifest parity with every packaged file;
7. stable media types, sizes and SHA-256 hashes;
8. deterministic repeated generation for the same version and commit;
9. ZIP safety with relative paths only and no duplicate entries;
10. absence of formulas, network resources and volatile asset timestamps;
11. read-only PR validation and publication-job permission isolation;
12. fail-closed behavior for existing versions or non-`main` publication attempts.

## Rejected scope expansion

This review does not introduce:

- new source documents or master-data rows;
- new shortlist, comparison or evidence semantics;
- cross-scope comparisons;
- ranking, scoring or recommendations;
- inferred values;
- a public web application;
- an external hosting service;
- automatic release publication on every merge.

## Next package

The next package is **Versioned Data Product Release Publication**.

It will implement the deterministic release assembler, semantic version validation, manifest and checksum generation, focused tests, a read-only validation workflow, the manual GitHub Release publication job, documentation and canonical state synchronization.