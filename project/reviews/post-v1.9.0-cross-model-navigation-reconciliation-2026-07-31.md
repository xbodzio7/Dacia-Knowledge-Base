# Post-v1.9.0 Cross-Model Navigation Reconciliation

Date: 2026-07-31

## Reconciliation result

The previously deferred cross-model workspace question is no longer open. The original review was completed in PR #295 and the conditional workspace card was implemented in PR #296.

Current code correctly adds the card **Models and comparison scopes** only when the exact verified cross-model HTML member exists. The v1.9.0 public audit confirms that the generated cross-model product and all local links are valid.

## Remaining issue

Discoverability is inconsistent outside the browser workspace:

- the downloader result does not name the cross-model HTML as an entry point;
- the CLI summary does not print its path;
- the consumer guide does not describe it and still states that the landing page contains four primary products.

## Decision

Select `Cross-Model Download Discoverability Alignment` as the next package.

The implementation must reuse the already verified member, extend existing tests and update documentation. It must not change the workspace card, generated cross-model products, comparison scopes, public release assets or semantic boundaries.
