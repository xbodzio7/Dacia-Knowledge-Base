# Data Products v1.19.1 Visible Publication Trigger

Date: 2026-08-08

## Purpose

This branch exists only to expose the already-authorized bounded Data Products v1.19.1 publisher to a visible Pull Request event.

The exact publication source is:

`e3a43a999a40f920bceab655cdfdac5856119a07`

The activation Pull Request is not intended to merge. Its workflow checks out the exact base SHA above, independently validates the v1.19.1 release contract, performs two byte-identical builds, verifies the complete offline workspace, creates exactly three public assets, downloads and verifies those assets again, records a durable publication receipt and canonical state transition directly on `main`, and removes the temporary publisher tooling.

## Safety boundary

The workflow runs only when all of these conditions remain true:

- the Pull Request head repository is this repository;
- the head branch is exactly `agent/data-products-v1-19-1-visible-trigger-001`;
- the Pull Request base SHA is exactly `e3a43a999a40f920bceab655cdfdac5856119a07`.

The publisher itself additionally refuses to publish if `main` moves before release creation, if `data-products-v1.19.1` already exists, if the established v1.19.0 or v1.18.0 tag target changes, if deterministic double-build or workspace verification fails, or if the source-bounded configurator/Spring Type 2 evidence contracts differ.

## Merge policy

Do not merge this Pull Request. After successful publication and independent verification, close it without merge.
