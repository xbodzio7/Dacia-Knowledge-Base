# Post-v1.9.0 Cross-Model Navigation Reconciliation

Date: 2026-07-31

Status: **complete**

## Historical result

The original Cross-Model Navigation Usability Review was completed on 27 July 2026. PR #296 then implemented its selected recommendation: a conditional fifth primary workspace card titled **Models and comparison scopes** for the verified member:

```text
contents/cross-model/cross-model-comparison-view.html
```

Releases without that member retain the older four-card layout. The implementation did not alter public assets or comparison semantics.

## Current v1.9.0 state

The independently audited public workspace contains:

- 78 active configurations;
- 20 independent reporting scopes;
- 129 within-scope pairs;
- 80 cross-model comparison paths;
- two cross-model navigation paths;
- 88 local links in the workspace index;
- 60 local links in the cross-model HTML.

The workspace index already exposes the cross-model navigation card and every existing scope report while preserving singleton and no-cross-scope boundaries.

## Remaining discoverability gap

The browser workspace is correct, but three repository-facing surfaces are not aligned:

1. `ENTRY_POINTS` in the release downloader omits the verified cross-model HTML member.
2. The terminal summary does not print a direct cross-model navigation path.
3. The consumer guide still describes four primary products and does not document the cross-model navigation product.

This is a bounded usability inconsistency. It is not a source-data, comparison-engine or release-asset defect.

## Selected implementation

**Cross-Model Download Discoverability Alignment**

The package will:

- add `cross_model_html` to the verified release-download entry points;
- print it as `Cross-model navigation` in the CLI summary;
- update the consumer guide to describe five primary products when cross-model HTML is present;
- extend existing download tests without adding a new test case;
- preserve the current workspace-index card and all comparison semantics.

## Boundary

The package will not modify:

- workspace-index layout or card rendering;
- cross-model HTML or JSON;
- source or master data;
- reporting scopes or pair generation;
- public v1.9.0 assets;
- ranking, recommendation or inference behavior.

Decision: `ALIGN_CROSS_MODEL_DOWNLOAD_DISCOVERABILITY`.
