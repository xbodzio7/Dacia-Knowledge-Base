# Cross-Model Workspace Entry Point

Date: 2026-07-27

## Goal

Make the existing public cross-model HTML discoverable from the generated local workspace landing page without changing or republishing `data-products-v1.8.1`.

## Implementation

`tools/reporting/data_product_workspace_index.py` now recognizes the exact verified release member:

```text
cross-model/cross-model-comparison-view.html
```

When that member exists in the external manifest and the corresponding local file exists under `contents/`, the `Start here` section receives one additional card:

- title: `Models and comparison scopes`;
- description: `Browse model families and open only existing scope reports.`;
- target: `contents/cross-model/cross-model-comparison-view.html`.

The card uses the same manifest membership, safe-path, local-file and URL-encoding helpers as the other primary products.

## Compatibility

Releases without the cross-model member retain the original four-card layout. A manifest that declares the member without a corresponding extracted file is rejected transactionally.

The synthetic fixture remains a member-absent compatibility case. Dedicated checks add a member-present case and a declared-but-missing failure case.

## Public v1.8.1 smoke

The standard `Verified Data Product Release Download` workflow now downloads immutable `data-products-v1.8.1` on Linux and Windows. It requires:

- the existing exact source commit;
- five primary cards;
- 84 local links;
- the exact cross-model local path;
- all local targets to exist;
- byte-identical generated `index.html` across operating systems.

The historical publication audit remains immutable at 83 links because it records the downloader behavior at publication time. Regenerating a workspace with the newer downloader adds the local entry point without rewriting any release asset.

## Boundaries

No public tag or asset changes. No master-data or schema change. No comparison-engine change. No cross-scope pair, ranking, recommendation or inferred value is created.

## Next package

`Post-Cross-Model Workspace Priority Selection Review` — select the next highest-value package after the complete public-release and workspace discoverability flow.
