# Portfolio Source Coverage Matrix Release Integration

Date: 2026-08-04

Package ID: `portfolio_source_coverage_matrix_release_integration_001`

Status: **complete**

## Result

Every newly built versioned data-product archive now includes the verified portfolio source coverage matrix in JSON, CSV and standalone HTML under `source-coverage/`.

The integration is a deterministic layer over the existing family-summary, family-comparison and model-version release path. It preserves all previously integrated archive members byte for byte and copies the three source-coverage outputs byte for byte from `data/reporting`.

## Manifest contract

Newly built manifests declare:

- `portfolio_source_coverage_matrix_generated: true`;
- formats `JSON`, `CSV` and `HTML`;
- directory `source-coverage`;
- a sorted, hashed inventory containing all three source-coverage members.

The top-level public release contract remains exactly three assets: the ZIP archive, `data-product-release-manifest.json` and `SHA256SUMS`.

## Offline workspace

The verified downloader exposes the optional entry point `source_coverage_matrix_html` when the archive contains the source-coverage HTML. The workspace index then adds a dedicated **Source coverage matrix** card, and the download CLI prints the direct path.

Older immutable releases remain valid: when the optional member is absent, no source-coverage entry point or card is created and all existing required and optional family and version entry points continue to verify.

## Verification boundary

The existing seven-test release-integration suite verifies:

- manifest declarations for the family summary, family matrix, version matrix and source coverage matrix;
- all twelve product files copied byte for byte;
- exact source-coverage invariants: 33 active sources, 251 explicit relationships, 81 configurations, 22 versions, six model families and zero missing provenance;
- exact registered source identity and SHA-256 retention;
- all non-scoring, non-ranking, non-recommendation and non-inference flags;
- canonical release verification;
- direct family-summary, family-matrix, version-matrix and source-coverage entry points;
- all four dedicated workspace cards;
- deterministic workspace-index bytes and full offline workspace verification;
- two independent byte-identical builds;
- the unified release CLI using the source-coverage-integrated build path.

The canonical repository baseline remains 1862 tests.

## Boundaries

No source data, master data, reporting scope, configuration pair, cross-scope pair, source quality score, ranking, recommendation or inferred value changes.

## Next package

Prepare immutable Data Products `v1.15.0` from the verified integration merge state. The minor version reflects the new public archive members and optional consumer entry point while preserving backward compatibility.
