# Data Products v1.12.1 Final Visible Publication Trigger

Date: 2026-08-03

## Exact source

The bounded publication workflow is pinned to `6f208ecef49304c2f4bd9c6d46d93074b33aff6f`, the merge commit of the workspace-index rendering contract fix.

## Publication contract

The workflow checks out only that base commit, shares the repository-wide v1.12.1 publication concurrency group, refuses any existing tag or release, runs the canonical focused tests, builds twice with byte identity, verifies the model-family entry point and deterministic workspace index, publishes exactly three immutable assets, verifies public downloads byte for byte and records the receipt and next canonical package.

This activation pull request changes no source data or release semantics and is not intended to merge.
