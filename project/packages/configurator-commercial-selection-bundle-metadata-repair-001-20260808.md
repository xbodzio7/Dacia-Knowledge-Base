# Configurator Commercial Selection Bundle Metadata Repair 001

Date: 2026-08-08  
Baseline main: `2398893cf0dc123ec9d82766c70d4cfa7cb1db05`

## Purpose

Restore repository traceability after PR #609 merged the commercial-selection comparison-bundle parser and package record but did not include the direct parser regression or canonical-state synchronization described by the original package record.

## Scope

This repair changes no production logic and no master data. It:

- adds direct regression coverage inside the existing comparison-bundle selection test method, preserving the 1885-test discovery baseline;
- verifies preservation of source-specific `commercial_selection` metadata;
- verifies rejection of `compatibility_inference_performed=true`;
- corrects the original #609 package record to list the files that PR actually changed and records its green Quality run #3980;
- synchronizes `project/state.json` and generated `project/STATE_SUMMARY.md`;
- leaves `New Spring Current Shop Retry Cycle 002` as the next planned package, now eligible on 2026-08-08.

## Acceptance criteria

- no production-code or `data/master` changes;
- existing `test_selection_combines_direct_and_shortlist_codes` covers both preserved commercial metadata and the unsafe-inference rejection path;
- no new discovered `test_*` method;
- canonical baseline remains 1885;
- project-state check passes;
- complete Quality matrix passes on the final PR head;
- PR is merged only after all required workflows are green.

## Files

- `tests/test_configuration_comparison_bundle.py`
- `project/packages/configurator-commercial-selection-bundle-metadata-001-20260807.md`
- `project/packages/configurator-commercial-selection-bundle-metadata-repair-001-20260808.md`
- `project/state.json`
- `project/STATE_SUMMARY.md`
