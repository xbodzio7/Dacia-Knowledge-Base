# Data Products v1.10.0 Accelerated Release Preparation

Date: 2026-08-01

## Purpose

Prepare one accelerated minor release that publishes the current repository data products and the already merged interactive shortlist repairs.

The public `data-products-v1.9.0` remains immutable.

## User-facing interface delta

The release includes the interface repair merged in Pull Request #427:

- one forced dark theme across the interactive shortlist;
- grouped duplicate commercial grade labels while retaining exact version codes;
- model headers that remain visible during vertical scrolling;
- parameter and category labels that remain visible during horizontal scrolling;
- deterministic parameter and configuration column widths;
- a sticky category label cell instead of an oversized category colspan cell.

The release also retains the existing pair-type filter and multi-configuration comparison behavior.

## Data delta

The release uses the current source-backed repository state after v1.9.0, including the Spring catalogue foundation and subsequent exact technical and equipment observations.

No cross-scope pair, ranking, recommendation or inferred value is introduced.

## Execution policy

This package activates `accelerated_milestone_closure`:

- focused tests during implementation;
- batched deterministic repairs;
- one final complete Pull Request quality matrix;
- exact-commit, double-build publication after merge;
- immutable release assets;
- publication receipt and workflow self-removal.

## Target

- version: `1.10.0`;
- tag: `data-products-v1.10.0`;
- archive: `dacia-knowledge-base-data-products-v1.10.0.zip`;
- public assets: archive, manifest and SHA256SUMS.

## Acceptance criteria

- project documentation describes the accelerated mode and its safety boundaries;
- release notes describe the interface repair and current source-backed portfolio;
- focused interface and release tests pass;
- the final Pull Request head passes the complete repository quality matrix;
- post-merge publication builds twice from the exact merge SHA and proves byte identity;
- the offline workspace verifies successfully;
- the public release is created only once and is then recorded in canonical state.

## Historical contract repair

Five completed Sandero Stepway source-gap verifiers now validate their durable data, generated analysis and minimum canonical baseline without requiring `project/state.json` to remain frozen on their former current or next package. This keeps completed package contracts valid while the canonical state advances to release preparation and later milestones.

## Publication trigger

The publisher workflow is already installed on `main`. This follow-up changes the release package record so GitHub processes the exact-commit publication workflow from an existing default-branch definition rather than from the commit that introduced the workflow itself.
