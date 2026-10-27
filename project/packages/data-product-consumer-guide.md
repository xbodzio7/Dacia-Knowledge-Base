# Data Product Consumer Guide

## Status

Implementation package for the `Data Product Utilization` phase.

## Goal

Provide one source-backed Polish-language guide for the complete consumer workflow, from an explicit immutable public release through offline navigation and custom comparisons to later lifecycle verification.

## Product

The user-facing guide is:

```text
project/guides/data-product-consumer-guide.md
```

It is intended for people using the repository tools and the public `data-products-v1.0.0` release. It does not duplicate internal package history or introduce a second source of truth for current project state.

## Covered workflow

The guide explains:

- prerequisites and the offline boundary,
- explicit-version download through `data-product-release-download`,
- tag, asset, manifest, checksum and atomic-publication behavior,
- navigation through the root `index.html`,
- shortlist selection and deterministic browser export,
- the existing six-sheet XLSX and scope reports,
- custom `configuration-comparison-bundle` generation from shortlist JSON or explicit codes,
- later read-only `data-product-workspace-verify` use,
- deterministic JSON verification output,
- recovery after detected corruption,
- release provenance and independent checksum control,
- semantic boundaries around missing data, scopes, inference, ranking and recommendations.

## Validation

Six explicit documentation checks require:

- every documented `python tools/dkb.py` command to exist in the unified CLI registry,
- the complete set of consumer products and provenance files to be named,
- exact immutable version examples instead of `latest`,
- read-only and non-inference boundaries,
- a README link to the guide,
- execution of the checks in the read-only Linux/Windows public-release workflow.

The guide checks run before the live public `v1.0.0` download, workspace verification and cross-platform index-byte comparison.

## Non-goals

- creating a second CLI or interactive help system,
- embedding generated release files in the repository,
- changing `data-products-v1.0.0`,
- introducing recommendations or rankings,
- expanding source data.
