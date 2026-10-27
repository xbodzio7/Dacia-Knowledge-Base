# Data Products v1.12.1 Workspace Index Contract Fix

Date: 2026-08-03

## Failure evidence

Visible publication run `30847263581` completed the focused tests, canonical state check and two byte-identical v1.12.1 builds from exact SHA `1c87eed4410303b842ccb8ea1205d1790fc30d9a`. It then failed before release creation because the written workspace index contained the verified model-family card while the renderer used by offline verification did not.

## Root cause

`tools/reporting/data_product_workspace_index.py` augmented only `write_workspace_index()`. `data_product_workspace_verify` reconstructs expected bytes through `render_workspace_index()`, so a verified release containing `model-families/portfolio_model_family_summary.html` produced two different canonical index representations.

## Repair

The model-family augmentation is now a single deterministic rendering step shared by `render_workspace_index()` and `write_workspace_index()`. The existing release-integration test materializes a complete workspace, asserts the direct family entry point and card, checks renderer/write byte identity and runs the full offline verifier. The test count remains 1862.

## Boundaries

No source data, release member, report semantic, release version, ranking, recommendation or inferred value changes. No tag or GitHub Release existed when this repair was prepared.
