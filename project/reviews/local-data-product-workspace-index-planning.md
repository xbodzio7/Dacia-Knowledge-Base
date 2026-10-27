# Local Data Product Workspace Index Planning Review

## Scope

This review selects a deterministic local landing-page contract for a workspace created by `data-product-release-download`. It does not modify the immutable public `data-products-v1.0.0`, republish assets or expand source data.

## Current workspace

A verified download creates:

- `assets/` with the original ZIP, external manifest and `SHA256SUMS`,
- `contents/` with 59 validated release members,
- direct CLI output for shortlist HTML, comparison workbook, bundle manifest and release notes.

The user still needs terminal output or archive knowledge to navigate the workspace after the command finishes. The comparison bundle already exposes scope groups and artifact paths through `comparison-bundle-manifest.json`.

## Options considered

### Add a guide to a future release archive

This would improve only a later release and would not help the already immutable `v1.0.0`. It also couples navigation presentation to release publication. Defer.

### Generate a Markdown or text index

This is portable but does not provide reliable clickable navigation to HTML, XLSX and per-scope artifacts across common desktop environments. It remains suitable as release notes, not as the primary landing page.

### Create platform-specific shortcuts or symlinks

Windows shortcut files, Unix symlinks and desktop launchers are not portable, add execution-policy differences and complicate deterministic validation. Reject.

### Generate a static local HTML index

A repository-owned HTML renderer can run only after release verification and extraction. It can link existing local files using relative paths, summarize release identity and inventory, expose every comparison scope, and work offline without changing the release.

## Decision

Select **Local Data Product Workspace Index HTML** as the next package.

The downloader will generate `index.html` at the workspace root after all release members and required entry points have been verified.

## Contract

The page will:

- be deterministic for the same verified release; no generation timestamp, hostname, absolute path or random identifier,
- be fully self-contained with embedded CSS and no JavaScript or external resources,
- preserve the exact release version, tag, commit, snapshot date, configuration count, scope count and public release URL,
- provide primary cards for shortlist HTML, comparison workbook, bundle manifest and release notes,
- render one section per comparison scope in deterministic manifest order,
- distinguish comparable scopes from singleton scopes,
- link existing scope JSON, Markdown, CSV and HTML reports when present,
- display pair, difference and artifact counts already recorded by the bundle manifest,
- include provenance links to the original three files under `assets/`,
- use only normalized relative paths from already verified manifests,
- HTML-escape every rendered value and percent-encode path segments for `href` attributes,
- reject a missing or malformed comparison bundle manifest instead of silently creating a partial index,
- write the index transactionally before the final workspace rename,
- report `index.html` as the first CLI entry point while retaining the existing four direct paths.

## Data boundaries

The renderer will read only:

- verified release metadata returned by the downloader,
- `data-product-release-manifest.json`,
- `contents/comparison-bundle/comparison-bundle-manifest.json`.

It will not open or reinterpret individual comparison values, rank configurations, recommend products, infer missing data or create cross-scope comparisons.

## Validation plan

Tests should cover deterministic bytes, release summary escaping, relative URL encoding, four primary cards, all 13 current scopes, comparable and singleton rendering, optional report links, malformed bundle manifests, unsafe paths, missing artifacts, transactional cleanup, CLI output and a read-only Linux/Windows live smoke against public `v1.0.0`.

The live workflow should confirm that `index.html` contains no external URL dependencies except the displayed GitHub Release link, opens all local href targets that are expected to be files, and remains byte-identical between Linux and Windows for the same release.

## Outcome

The next package will convert the verified local workspace from a collection of correctly extracted files into one offline, inspectable entry point. It improves consumption of the existing public release without changing its bytes or the source-data portfolio.

The selected contract is final for this review package and requires no change to the public release identity or assets.
