# Data Products v1.19.0 Visible Publication Trigger

Date: 2026-08-08

## Purpose

This branch exists only to expose the already-authorized bounded Data Products v1.19.0 publisher to a visible Pull Request event.

The exact publication source is:

`c121e600de48576f2da53cba2eb42075b6632504`

The activation Pull Request is not intended to merge. Its workflow checks out the exact base SHA above, independently validates the v1.19.0 release contract, performs two byte-identical builds, verifies the complete offline workspace, creates exactly three public assets, downloads and verifies those assets again, records a durable publication receipt and canonical state transition directly on `main`, and removes the temporary publisher tooling.

## Safety boundary

The workflow runs only when all of these conditions remain true:

- the Pull Request head repository is this repository;
- the head branch is exactly `agent/data-products-v1-19-0-visible-trigger-001`;
- the Pull Request base SHA is exactly `c121e600de48576f2da53cba2eb42075b6632504`.

The publisher itself additionally refuses to publish if `main` moves before release creation, if `data-products-v1.19.0` already exists, if the established v1.18.0 tag target changes, if deterministic double-build or workspace verification fails, or if the source-bounded configurator/commercial evidence contracts differ.

## Merge policy

Do not merge this Pull Request. After successful public release verification and receipt recording, close it without merge.
