# Portfolio Model Family Comparison Matrix Release Integration

Date: 2026-08-03

Package ID: `portfolio_model_family_comparison_matrix_release_integration_001`

Status: **complete**

## Result

Every newly built versioned data-product archive now includes the verified portfolio model-family comparison matrix in JSON, CSV and standalone HTML under `model-families/`.

The integration is a deterministic layer over the existing portfolio family-summary release path. It preserves all previously integrated family-summary members byte for byte and copies the three matrix outputs byte for byte from `data/reporting`.

## Manifest contract

Newly built manifests declare:

- `portfolio_model_family_comparison_matrix_generated: true`;
- formats `JSON`, `CSV` and `HTML`;
- directory `model-families`;
- a sorted, hashed inventory containing all three matrix members.

The top-level public release contract remains exactly three assets: the ZIP archive, `data-product-release-manifest.json` and `SHA256SUMS`.

## Offline workspace

The verified downloader exposes the optional entry point `model_family_comparison_matrix_html` when the archive contains the matrix HTML. The workspace index then adds a dedicated **Model family comparison matrix** card.

Older immutable releases remain valid: when the optional matrix member is absent, no matrix entry point or card is created and all existing required entry points continue to verify.

## Verification boundary

The extended seven-test release-integration suite verifies:

- both family-summary and family-matrix manifest declarations;
- all six family product files copied byte for byte;
- exact matrix source identity and semantic boundary flags;
- canonical release verification;
- direct summary and matrix entry points;
- deterministic workspace-index bytes and full offline workspace verification;
- two independent byte-identical builds;
- the unified release CLI using the matrix-integrated build path.

No source data, master data, reporting scope, configuration pair, ranking, recommendation or inferred value changes.

## Next package

Prepare immutable Data Products `v1.13.0` from the verified integration merge state. The minor version reflects the new public archive members and optional consumer entry point while preserving backward compatibility.
