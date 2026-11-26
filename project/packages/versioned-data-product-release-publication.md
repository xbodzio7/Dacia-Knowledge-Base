# Versioned Data Product Release Publication

## Package status

`ACTIVE`

This package turns the existing offline products into one deterministic, versioned release candidate and provides a guarded manual GitHub Release publication workflow.

## User-facing command

Build assets for one exact version and repository commit:

```bash
python tools/dkb.py data-product-release \
  --version 1.0.0 \
  --commit-sha 0123456789012345678901234567890123456789 \
  --output-directory ../data-product-release
```

Verify an existing candidate without rebuilding it:

```bash
python tools/dkb.py data-product-release \
  --verify \
  --version 1.0.0 \
  --commit-sha 0123456789012345678901234567890123456789 \
  --output-directory ../data-product-release
```

The output directory must be new or empty. Build failure removes the temporary candidate and never overwrites a nonempty directory.

## Canonical assets

Every candidate contains exactly three top-level files:

- `dacia-knowledge-base-data-products-vMAJOR.MINOR.PATCH.zip`;
- `data-product-release-manifest.json`;
- `SHA256SUMS`.

The external manifest records the final archive name, size and SHA-256. It is intentionally not copied into the archive because a manifest that hashes its containing archive would create a self-reference. `SHA256SUMS` covers the archive and the standalone manifest.

## Archive inventory

The deterministic ZIP contains 59 files for the current repository snapshot:

- `RELEASE_NOTES.md`;
- complete active-configuration shortlist JSON, Markdown, CSV and self-contained HTML;
- one full comparison bundle for all 53 active configurations;
- 13 independent reporting groups, each with JSON, Markdown, differences CSV and self-contained HTML;
- the comparison-bundle manifest;
- the six-sheet XLSX workbook.

All 13 groups remain independent and comparable. No cross-scope pair, ranking, recommendation or inferred value is generated.

## Determinism and safety

- semantic versions use normalized `MAJOR.MINOR.PATCH` without leading zeros;
- repository identity uses an exact lowercase 40-character commit SHA;
- paths are relative, normalized and unique;
- symlinks and traversal paths are rejected;
- ZIP members use a fixed order, timestamp, mode and `ZIP_STORED` compression;
- the manifest inventory is ordered by path and contains no workflow ID, temporary path or runtime timestamp;
- every member's media type, size and SHA-256 is verified after archive creation;
- repeated generation for the same version, commit and repository state is byte-identical.

## Publication workflow

`.github/workflows/data-product-release.yml` has two permission boundaries.

### Pull Request and build validation

- runs with `contents: read`;
- executes the focused release tests;
- builds and independently verifies a release candidate;
- uploads the candidate as a seven-day Actions artifact;
- never creates a tag or release.

### Manual publication

- is available only through `workflow_dispatch`;
- requires execution from `main`;
- grants `contents: write` only to the publication job;
- downloads and re-verifies the exact candidate built for the tested commit;
- rejects an existing release or tag before any write;
- creates `data-products-vMAJOR.MINOR.PATCH` at the tested commit;
- uploads exactly the archive, manifest and `SHA256SUMS`;
- never replaces or mutates a previously published release.

No first public release is created by this package. Selecting and publishing the initial version is an explicit readiness decision because release tags and public assets are durable operations.

## Verification

The focused suite covers:

- version and commit validation;
- 53-configuration shortlist completeness;
- 13-scope bundle completeness;
- fixed 59-member archive inventory;
- path safety and deterministic ZIP metadata;
- manifest, archive and checksum parity;
- self-contained HTML and included XLSX;
- byte-identical repeated generation;
- transactional failure cleanup and non-overwrite behavior;
- direct and unified CLI routing;
- read-only Pull Request validation and isolated publication permissions.

## Boundaries retained

This package changes no master data, source evidence, reporting denominator, comparison state, shortlist filter, workbook cell, cross-scope rule, ranking or recommendation behavior.