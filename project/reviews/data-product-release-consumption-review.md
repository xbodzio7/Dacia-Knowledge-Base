# Data Product Release Consumption Review

## Scope

This review evaluates how an external user discovers, downloads, verifies and starts using the immutable public release `data-products-v1.0.0`. It does not change source data, release assets or the release identity.

## Evidence reviewed

- the public release record in `project/releases/data-products-v1.0.0.md`,
- the README command table and versioned-distribution section,
- `tools/data_product_release.py`,
- the deterministic release builder and verifier,
- the archive inventory and existing release regression tests.

## Findings

### Discoverability

The release is linked from the README, but only inside the long technical section about versioned distribution. The main command table describes `data-product-release` as a build and verification command and does not present a direct consumer workflow.

### Download

A user must currently use the GitHub Release page or an external `gh`/browser workflow and manually select three coordinated assets:

1. the versioned ZIP,
2. `data-product-release-manifest.json`,
3. `SHA256SUMS`.

The repository has no command that resolves an explicit release version, validates the canonical asset set and downloads it transactionally.

### Verification

The existing verifier is strong once all three files are already co-located. It validates the manifest schema, release identity, archive name, sizes, SHA-256 values, deterministic ZIP metadata, every archive member and the external checksum file. It does not fetch GitHub release metadata or prove that the release tag resolves to the manifest commit.

### First use

The ZIP contains useful entry points, especially:

- `shortlist/configuration-shortlist.html`,
- `comparison-bundle/configuration-comparison-workbook.xlsx`,
- `comparison-bundle/comparison-bundle-manifest.json`.

However, the current release notes describe inventory and provenance rather than an extraction and opening workflow. A user must inspect the archive to find these files.

## Options considered

### Documentation-only quick start

A top-level README section would improve discovery but would not remove manual asset selection, identity checks or extraction risk. Retain as supporting documentation, not the primary package.

### Add a new start page to a future archive

A top-level consumer guide inside the ZIP would improve future releases, but cannot improve the already immutable `v1.0.0` and would require another public release. Defer until the download path is stable.

### GitHub Pages portal

A portal would introduce a second delivery channel and duplicate the release contract. It is outside the current minimal utilization step.

### Verified download and extraction CLI

A repository-owned consumer command can improve the existing release without changing it. It can require an explicit immutable version, fetch the canonical release metadata and three assets, verify the tag target and all existing hashes, extract only validated members and print ready-to-open HTML/XLSX paths.

## Decision

Select **Verified Data Product Release Download CLI** as the next package.

The command name will be `data-product-release-download` and the initial contract will:

- require an explicit normalized `MAJOR.MINOR.PATCH` version; no mutable `latest` alias,
- target the public `xbodzio7/Dacia-Knowledge-Base` release channel,
- use only the Python standard library and require no GitHub authentication for public downloads,
- optionally use `GITHUB_TOKEN` when present without making it mandatory,
- accept only the canonical tag and three canonical asset names,
- resolve the release tag to an exact commit and require equality with the manifest commit,
- download into a temporary directory and refuse to overwrite a non-empty destination,
- reuse `verify_release_assets` before extraction,
- extract validated archive members by normalized paths without `extractall`,
- create separate `assets/` and `contents/` directories,
- print the shortlist HTML, comparison workbook, bundle manifest and release notes entry points,
- avoid rankings, recommendations, inferred values and any source-data changes.

## Validation plan for the next package

Regression coverage should include explicit version validation, public API metadata parsing, canonical asset enforcement, optional token headers, redirects and streamed downloads, annotated/lightweight tag resolution, tag/manifest mismatch rejection, hash failures, transactional cleanup, non-empty destination protection, safe extraction, entry-point reporting and unified `dkb.py` routing. Network calls in unit tests must be mocked; a focused read-only workflow may verify the immutable public `v1.0.0` on Linux and Windows.

## Outcome

The release itself is technically complete and trustworthy. The highest-value remaining friction is the gap between a release URL and a verified, ready-to-open local workspace. The selected package closes that gap without republishing or expanding the data portfolio.
