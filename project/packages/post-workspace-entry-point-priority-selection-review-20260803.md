# Post-Workspace Entry Point Priority Selection Review

Date: 2026-08-03

Package ID: `post_workspace_entry_point_priority_selection_review_001`

Status: **complete**

## Evidence reviewed

- immutable Data Products `v1.12.0` publication and receipt;
- the model-family release integration delivered before `v1.12.0`;
- the direct model-family download entry point and dedicated offline workspace card delivered after publication in PR #486;
- the repository rule that an immutable release must not be rewritten;
- the requirement that user-facing interface changes agreed for a release must be present in the published consumer workspace.

## Finding

`v1.12.0` contains the model-family report assets, but its published consumer workspace predates the direct `model_family_summary_html` entry point and the dedicated **Model family summary** card. The repository implementation is now complete on `main`, but the immutable `v1.12.0` archive cannot be modified.

## Selection

The next package is **Data Products v1.12.1 Corrective Release Preparation**.

It will publish the existing, already verified `main` state as a patch release so that the downloadable workspace contains the previously agreed direct model-family interface. It must use an exact source SHA, byte-identical double build, verified public download and offline workspace verification.

## Boundaries

The corrective release must not change source data, report semantics, reporting scopes, comparison pairs, rankings, recommendations or inferred values. It must not rewrite or replace `v1.12.0`.
