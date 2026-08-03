# Data Products v1.12.1 Publication Test Contract Fix

Date: 2026-08-03

## Purpose

Correct the bounded v1.12.1 publisher so its focused pre-publication suite references only tests that are part of the canonical repository baseline.

## Failure evidence

Publication workflow run `30845446061` checked out exact source SHA `7adf8747ab415ddbd1b0629bec84aafd00a13185` and failed before release creation because it attempted to import the absent transient package test `tests.test_portfolio_model_family_workspace_entry_point`.

## Verification retained

The publisher still runs the corrective-release test, portfolio model-family release integration, canonical release tests and public-download tests. It additionally performs two byte-identical builds, canonical release verification, direct offline workspace extraction, the model-family entry-point and card assertions, full workspace verification, immutable GitHub release creation, public re-download byte comparison and receipt recording.

## Boundaries

This package changes no source data, generated release assets, report semantics, release version, comparison behavior, ranking, recommendation or inferred value. The canonical test baseline remains 1862.
