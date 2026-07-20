# Verified Data Product Release Download CLI

## Status

Implementation package for the `Data Product Utilization` phase.

## Goal

Turn one explicit immutable GitHub Release version into a verified, safely extracted local workspace without changing the public release or source data.

## Command

```bash
python tools/dkb.py data-product-release-download \
  --version 1.0.0 \
  --output-directory ../dkb-data-products-v1.0.0
```

The version is mandatory and must be normalized `MAJOR.MINOR.PATCH`. There is no mutable `latest` alias.

## Public identity contract

The command is intentionally bound to `xbodzio7/Dacia-Knowledge-Base` and resolves `data-products-vMAJOR.MINOR.PATCH` through the GitHub REST API. It rejects drafts, prereleases, a mismatched tag name, duplicate assets, missing assets, extra assets and unexpected download URLs.

Exactly three public assets are accepted:

- `dacia-knowledge-base-data-products-vMAJOR.MINOR.PATCH.zip`,
- `data-product-release-manifest.json`,
- `SHA256SUMS`.

The public repository requires no authentication. When `GITHUB_TOKEN` is present it is sent only to GitHub API requests and never to public asset URLs.

## Verification and extraction

The downloader resolves lightweight or annotated Git tags to an exact commit. After all three files are streamed into a temporary `assets/` directory, the existing `verify_release_assets` contract validates:

- schema and release identity,
- archive name, size and SHA-256,
- every member path, media type, size and SHA-256,
- deterministic ZIP metadata,
- the external `SHA256SUMS` file.

The manifest commit must equal the resolved tag commit. Only then are archive members written individually into `contents/` using normalized validated paths. The implementation does not call `ZipFile.extractall`.

The destination must be new or empty. Any metadata, network, identity, hash or extraction failure removes the temporary build and does not overwrite a non-empty destination.

## Ready-to-open entry points

A successful command prints paths to:

- `contents/shortlist/configuration-shortlist.html`,
- `contents/comparison-bundle/configuration-comparison-workbook.xlsx`,
- `contents/comparison-bundle/comparison-bundle-manifest.json`,
- `contents/RELEASE_NOTES.md`.

The local workspace keeps the original three files under `assets/` for independent re-verification.

## Validation

Unit tests use a small synthetic deterministic release and mocked HTTP responses. They cover public metadata, optional authentication headers, canonical asset enforcement, lightweight and annotated tags, tag/manifest mismatch, corrupt assets, destination safety, transactional cleanup, entry points, CLI output, unified routing and workflow permissions.

The focused GitHub Actions workflow also downloads the immutable public `v1.0.0` on Linux and Windows, independently re-runs `data-product-release --verify` against commit `653ddacf9dcaeefa356f53e3c00e71666f5c5b3e`, and checks all four local entry points.

The shared deterministic ZIP writer orders files by normalized POSIX member name, so synthetic and future release manifests keep the same inventory order on Linux and Windows.

## Non-goals

- selecting a mutable latest release,
- downloading arbitrary repositories or URLs,
- modifying or republishing `v1.0.0`,
- ranking or recommending configurations,
- inferring missing values,
- expanding the source-data portfolio.
