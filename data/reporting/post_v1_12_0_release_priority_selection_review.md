# Post-v1.12.0 Release Priority Selection Review

Status: **complete**

## Canonical evidence

- immutable release: `data-products-v1.12.0`;
- source commit: `0e8901fdb42d4bc3e415ce3347117040205fa652`;
- double-build byte identity: PASS;
- offline workspace verification: PASS;
- public download byte identity: PASS.

## Selected package

**Portfolio Model Family Workspace Entry Point** — `portfolio_model_family_workspace_entry_point_001`

Expose the verified portfolio model-family HTML as a direct backward-compatible download entry point and dedicated offline workspace card, without changing release contents, source data or comparison semantics.

## Rationale

The family HTML is already present and verified in `v1.12.0`, but consumers reach it indirectly through the cross-model page. A direct optional entry point improves discoverability while preserving compatibility with older releases.

## Preserved boundaries

- no source or master data changes;
- no cross-scope pairs;
- no ranking or recommendations;
- no inferred values;
- no mutation of published releases.
