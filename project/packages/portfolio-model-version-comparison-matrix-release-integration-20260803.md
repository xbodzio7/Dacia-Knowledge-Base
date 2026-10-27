# Portfolio Model Version Comparison Matrix Release Integration

Date: 2026-08-03

Package ID: `portfolio_model_version_comparison_matrix_release_integration_001`

Status: **complete**

## Result

Every newly built versioned data-product archive now includes the verified portfolio model-version comparison matrix in JSON, CSV and standalone HTML under `model-versions/`.

The integration is a deterministic layer over the existing family-summary and family-comparison release path. It preserves all previously integrated archive members byte for byte and copies the three version-matrix outputs byte for byte from `data/reporting`.

## Manifest contract

Newly built manifests declare:

- `portfolio_model_version_comparison_matrix_generated: true`;
- formats `JSON`, `CSV` and `HTML`;
- directory `model-versions`;
- a sorted, hashed inventory containing all three version-matrix members.

The top-level public release contract remains exactly three assets: the ZIP archive, `data-product-release-manifest.json` and `SHA256SUMS`.

## Offline workspace

The verified downloader exposes the optional entry point `model_version_comparison_matrix_html` when the archive contains the version-matrix HTML. The workspace index then adds a dedicated **Model version comparison matrix** card, and the download CLI prints the direct path.

Older immutable releases remain valid: when the optional member is absent, no version-matrix entry point or card is created and all existing required and optional family entry points continue to verify.

## Verification boundary

The existing seven-test release-integration suite verifies:

- manifest declarations for the family summary, family matrix and version matrix;
- all nine product files copied byte for byte;
- exact version-matrix invariants: 6 families, 22 versions, 81 configurations, 22 scopes, 33 sources, 251 explicit relationships and zero missing provenance;
- all non-pairing, non-ranking and non-inference flags;
- canonical release verification;
- direct family-summary, family-matrix and version-matrix entry points;
- all three dedicated workspace cards;
- deterministic workspace-index bytes and full offline workspace verification;
- two independent byte-identical builds;
- the unified release CLI using the version-matrix-integrated build path.

The canonical repository baseline remains 1862 tests.

## Boundaries

No source data, master data, reporting scope, configuration pair, cross-scope pair, ranking, recommendation or inferred value changes.

## Next package

Prepare immutable Data Products `v1.14.0` from the verified integration merge state. The minor version reflects the new public archive members and optional consumer entry point while preserving backward compatibility.
