# Local Data Product Workspace Index HTML

## Status

Implementation package for the `Data Product Utilization` phase.

## Goal

Create one deterministic offline landing page for every workspace produced by `data-product-release-download`, without changing the immutable public release or source data.

## Output

After all three public assets are downloaded, verified and safely extracted, the downloader writes `index.html` at the workspace root before the final atomic directory rename. The CLI reports this page as the first entry point.

## Inputs and boundaries

The renderer reads only verified release metadata, the external release manifest and `contents/comparison-bundle/comparison-bundle-manifest.json`. It does not open individual comparison values, rank configurations, recommend products, infer missing observations or create cross-scope comparisons.

## Page contract

The page is self-contained, contains embedded CSS, no JavaScript and no external runtime resources. For the same verified release it produces identical UTF-8 bytes on Linux and Windows. It contains no generation time, hostname, absolute path or random identifier.

It presents:

- release version, tag, commit, snapshot date, configuration and scope counts,
- a canonical link to the public GitHub Release,
- primary cards for shortlist HTML, the comparison workbook, bundle manifest and release notes,
- one ordered card for every comparable or singleton scope,
- source-backed pair, difference and artifact counts from the bundle manifest,
- available JSON, Markdown, CSV and HTML scope reports,
- links to the original ZIP, external manifest and `SHA256SUMS` under `assets/`.

Every local path must be normalized, present in the verified release inventory and exist on disk. Rendered text is HTML-escaped and each relative URL segment is percent-encoded. A malformed manifest, overlapping scope membership, identity mismatch, missing target or unsafe path fails the whole transactional download.

## Validation

A shared synthetic fixture models 53 configurations across 13 independent scopes with one comparable scope and 12 singletons. Regression tests cover deterministic rendering, primary and provenance navigation, scope states, escaping, URL encoding, count and identity mismatches, unsafe or missing paths, local target existence, write parity, downloader cleanup and workflow permissions.

The read-only `Local Data Product Workspace Index` workflow downloads public `data-products-v1.0.0` on Linux and Windows, validates every local link and offline dependency rule, uploads both index files and requires byte-identical output in a separate comparison job.

## Non-goals

- changing or republishing `data-products-v1.0.0`,
- adding a mutable latest alias,
- launching a local server or browser automatically,
- adding JavaScript, external styles or fonts,
- expanding source data.
