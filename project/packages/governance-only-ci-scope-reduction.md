# Governance-Only CI Scope Reduction

## Goal

Reduce unnecessary Pull Request workflow execution for changes that are strictly limited to durable project governance, while preserving the repository-wide `Quality` gate and every specialized validation path for product-affecting changes.

## Evidence

Two consecutive governance-only Pull Requests, #169 and #170, each changed only:

- `project/state.json`,
- `project/STATE_SUMMARY.md`,
- one document under `project/reviews/`.

Both Pull Requests triggered all 15 current workflows. Every run succeeded, but fourteen specialized product and reporting workflows repeated expensive generation and cross-platform verification that could not be affected by those three governance surfaces.

## Implemented contract

`.github/workflows/quality.yml` remains unchanged and continues to run for every Pull Request.

The following fourteen specialized workflows now ignore a Pull Request only when every changed path belongs to the governance-only set:

1. `configuration-selection-export.yml`,
2. `data-product-release.yml`,
3. `data-product-release-download.yml`,
4. `configuration-comparison-workbook.yml`,
5. `configuration-comparison-bundle.yml`,
6. `configuration-shortlist.yml`,
7. `configuration-shortlist-html.yml`,
8. `configuration-comparison-html.yml`,
9. `sandero-ecog120-manual-reporting.yml`,
10. `sandero-stepway-ecog120-automatic-reporting.yml`,
11. `jogger-ecog120-manual-reporting.yml`,
12. `jogger-ecog120-automatic-reporting.yml`,
13. `jogger-tce110-manual-reporting.yml`,
14. `jogger-hybrid155-automatic-reporting.yml`.

The shared ignored set is:

```yaml
paths-ignore:
  - project/state.json
  - project/STATE_SUMMARY.md
  - project/reviews/**
```

GitHub applies `paths-ignore` only when all changed paths match the ignored patterns. Therefore any Pull Request that also changes code, data, tests, workflow files, package documents, README, changelog or another repository surface continues to select the relevant specialized workflows.

## Preserved behavior

The package does not change:

- workflow names,
- jobs or matrices,
- operating systems or Python versions,
- permissions,
- `workflow_dispatch` triggers,
- test commands,
- generated artifacts,
- retention policies,
- release publication guards,
- public release identity,
- source data or product semantics.

`Versioned Data Product Release` retains its main-branch publication requirement and immutable tag/release rejection logic.

`Verified Data Product Release Download` retains Linux and Windows download, independent verification, offline workspace verification, corruption rejection and byte-identical index comparison.

`Configuration Comparison Workbook` retains Linux and Windows generation and byte-identical workbook verification.

## Validation plan

Because this implementation modifies every specialized workflow file, the implementation Pull Request must select and pass the complete current 15-workflow set.

A separate `Governance-Only CI Verification` package will then create a Pull Request changing only:

- `project/state.json`,
- `project/STATE_SUMMARY.md`,
- one document under `project/reviews/`.

That verification Pull Request must select exactly one workflow, `Quality`, and `Quality` must pass on Python 3.10, Python 3.13 and Windows.

## Boundary

This is a CI selection correction. It does not weaken validation for any code, data, product, test, workflow or documentation change outside the three explicit governance-only paths.
