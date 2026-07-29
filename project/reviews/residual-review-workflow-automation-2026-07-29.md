# Residual Review Workflow Automation

Date: 2026-07-29  
Package: `workflow_residual_review_bundle_001`  
Status: complete

## Result

The residual PDF review workflow no longer depends on a handoff prompt or a complete repository ZIP to recover the current package boundary. `project/state.json` now carries the package ID, exact path manifest and, for `residual_review` packages, the canonical source, page, candidate counts, chunk boundary and report locations.

`python tools/residual_review_bundle.py --output-directory ../residual-review-bundle` now:

- resolves the active or next residual package from canonical state unless an explicit package ID is supplied;
- reads the exact package from `verified_pdf_candidate_residual_gap_prioritization.json`;
- verifies the registered source path, byte count and SHA-256 against the brochure source receipt;
- reproduces the ordered candidate block with exact candidate IDs and exact text;
- extracts only the assigned page with layout preservation;
- renders only the assigned page to a 200 DPI PNG for visual review;
- writes a checksum manifest for every generated bundle member.

The `Residual Review Bundle` GitHub Actions workflow exposes the same result as a downloadable artifact. This is the canonical fallback when a GitHub connector can read repository text but cannot materialize binary PDF blobs.

## Existing workflow reuse

The proposed generic commands `package-scaffold`, `package-check` and `package-finalize` were not added. Their responsibilities already exist without duplication:

- `package-start` synchronizes `main` and creates the branch;
- `package-review` verifies the exact path manifest, diff and quality;
- `package-finish` verifies the one-commit package contract;
- `project-state --apply` synchronizes canonical state and generated documentation;
- `package-publish` publishes the manifest-driven package.

Adding aliases with overlapping meanings would increase maintenance and make the operational contract less clear.

## Scope boundary

No files under `data/master/**` or `data/imports/**` changed. The bundle is review input only and never creates evidence links, import specifications or master-data records.

The next package remains **Sandero Equipment Page 19 Unresolved Review — Chunk 1** (`residual_gap_051`).
