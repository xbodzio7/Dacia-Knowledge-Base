# Data Products v1.15.0 Release Preparation

Date: 2026-08-04

Package ID: `data_products_v1_15_0_release_preparation_001`

Status: **complete**

## Release scope

Prepare the first immutable release containing the portfolio source coverage matrix and its direct offline workspace entry point.

Version `1.15.0` is a backward-compatible minor release because it adds three public archive members and one optional consumer entry point without changing existing members, required entry points or report semantics.

## Product contents

The release includes the verified source coverage matrix in JSON, CSV and standalone HTML alongside the existing model-version matrix, family comparison matrix and family summary.

The source coverage matrix preserves:

- 33 active provenance sources used by the current portfolio;
- 251 explicit source-to-configuration relationships exactly once;
- 81 active configurations;
- 22 active canonical versions;
- 6 canonical model families;
- zero configurations without provenance;
- exact registered external or local source identity and SHA-256;
- no source quality score, source ranking, recommendation or inferred value.

## Release notes contract

The archive contains exactly one `## v1.15.0 portfolio source coverage matrix` section. It documents the twelve byte-identical product files, optional `source_coverage_matrix_html` entry point, dedicated workspace card, preserved older releases and immutable public `data-products-v1.14.1`.

## Verified preparation evidence

PR #523 and Quality run #30948182292 verified the release preparation code on the final integration head `4efa1de557018c3b945bf0df4d07bd974d9e9377`:

- all 1862 canonical tests passed on Python 3.10 and 3.13;
- the full quality and generated-artifact gate passed on Python 3.14;
- the Windows package workflow passed, including canonical project-state validation;
- the versioned release workflow built and verified a `v1.15.0` candidate;
- the verified downloader passed on Linux and Windows;
- independently rendered workspace-index bytes matched across operating systems;
- the seven-test integration suite proved two independent byte-identical builds;
- the complete extracted workspace verified offline with all four optional portfolio entry points and cards.

## Publication contract

Publication must:

- use the exact publication merge SHA, not the integration or preparation head;
- prove `data-products-v1.15.0` tag and release absence before mutation;
- build independently into two empty directories;
- require complete byte identity of archive, manifest and checksums;
- verify the canonical release manifest and every archive member;
- extract and verify the complete offline workspace;
- require all four family, version and source-coverage entry points and dedicated cards;
- create exactly three immutable public assets;
- download those assets and compare them byte for byte;
- verify the public download again before recording the receipt;
- preserve `data-products-v1.14.1` unchanged.

## Boundaries

No source data, master data, reporting scope, configuration pair, cross-scope pair, source quality score, ranking, recommendation or inferred value changes.

## Next package

`data_products_v1_15_0_publication_001` publishes and records the release only after full Quality and public-download contracts pass on the exact final publication source.