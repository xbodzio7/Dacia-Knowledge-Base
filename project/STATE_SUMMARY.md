# Project State Summary

> Generated from `project/state.json`. Do not edit manually.

## Repository

- Repository: `xbodzio7/Dacia-Knowledge-Base`
- Default branch: `main`
- Source of truth: repository
- Main SHA tracking: dynamic
- State updated: 2026-07-26

## Phase

**Data Products v1.8.1 Release Preparation**

## Reference delivery

- Package: Equipment Filter Regression and Model Price Ordering
- Pull Request: #289
- Verified head: `c425b3997c11132e7c325b843e9e13f44a5a9105`
- Quality run: #2040

## Verified baseline

- Tests: 1038
- Master CSV files: 46
- Master rows: 9688
- Configuration values: 2949
- Configuration import specifications: 117
- Configuration value ranges: 244
- Configuration range import specifications: 20
- Availability records: 4754
- Canonical attributes: 385
- Attribute categories: 30

## Current package

**Data Products v1.8.1 Release Preparation** — `complete`

Prepare and verify an immutable patch-release candidate containing the restored equipment filtering and cheapest-to-most-expensive model ordering without changing source-backed data or rewriting older public releases.

## Next package

**Data Products v1.8.1 Preflight** — `planned`

Build the v1.8.1 assets twice from the exact squash-merged preparation commit, prove byte identity, verify the real Chromium equipment-filter behavior and all release contracts, and record final identities without publishing.

## Autonomy

Mode: `autonomous_until_action_required`

Standing authorization covers package branches, manifest-scoped edits, tests and quality, package commits, pushes, Pull Requests, in-scope CI repairs, green merges, state updates and generated documentation.

Work stops only for a real source, access, authentication, policy, architecture, scope, destructive-operation or unresolved-evidence boundary. The stop message must begin with `ACTION_REQUIRED`.

## Review policy

- Review-only Pull Requests: exception only
- Milestone review interval: 5 logical packages
- One logical package per Pull Request: yes
- Automatic remote-branch deletion: no
