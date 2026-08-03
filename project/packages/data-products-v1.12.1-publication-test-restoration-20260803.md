# Data Products v1.12.1 Publication Test Restoration

Date: 2026-08-03

## Purpose

Restore the focused portfolio model-family workspace entry-point test that the v1.12.1 publication script requires and that was present in the original workspace-entry-point package history but absent from the current `main` tree.

## Failure evidence

Publication workflow run `30845446061` checked out exact source SHA `7adf8747ab415ddbd1b0629bec84aafd00a13185` and failed before release creation because `tests.test_portfolio_model_family_workspace_entry_point` could not be imported.

## Boundaries

This package changes no source data, generated release asset semantics, release version, comparison behavior, ranking, recommendation, or inferred value. It restores only the missing regression coverage required by the already defined publication contract.
