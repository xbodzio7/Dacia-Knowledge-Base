# Project State Summary

> Generated from `project/state.json`. Do not edit manually.

## Repository

- Repository: `xbodzio7/Dacia-Knowledge-Base`
- Default branch: `main`
- Source of truth: repository
- Main SHA tracking: dynamic
- State updated: 2026-08-08

## Phase

**Data Products v1.19.1 Release Preparation**

## Reference delivery

- Package: Spring Type 2 Current Selector Reconciliation
- Pull Request: #617
- Verified head: `324221d889e22c8be43e131bd60f7ef14328df52`
- Quality run: #31246369245

## Verified baseline

- Tests: 1885
- Master CSV files: 47
- Master rows: 11770
- Configuration values: 3604
- Configuration import specifications: 139
- Configuration value ranges: 316
- Configuration range import specifications: 24
- Availability records: 5911
- Canonical attributes: 387
- Attribute categories: 30

## Current package

**Data Products v1.19.1 Release Preparation** — `complete`

Prepare a reproducible v1.19.1 patch release candidate that delivers the bounded Spring Type 2 current-selector correction on top of immutable v1.19.0, using the established exact-source deterministic release pipeline and stopping before public tag or release creation.

## Next package

**Data Products v1.19.1 Publication** — `planned`

Publish immutable Data Products v1.19.1 from an exact verified source SHA with byte-identical double build, offline-workspace verification, public-download verification and a durable publication receipt while preserving v1.19.0 immutability.

## Autonomy

Mode: `autonomous_until_action_required`

Standing authorization covers package branches, manifest-scoped edits, tests and quality, package commits, pushes, Pull Requests, in-scope CI repairs, green merges, state updates and generated documentation.

Work stops only for a real source, access, authentication, policy, architecture, scope, destructive-operation or unresolved-evidence boundary. The stop message must begin with `ACTION_REQUIRED`.

## Review policy

- Review-only Pull Requests: exception only
- Milestone review interval: 5 logical packages
- One logical package per Pull Request: yes
- Automatic remote-branch deletion: no
