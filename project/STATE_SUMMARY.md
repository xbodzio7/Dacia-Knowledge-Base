# Project State Summary

> Generated from `project/state.json`. Do not edit manually.

## Repository

- Repository: `xbodzio7/Dacia-Knowledge-Base`
- Default branch: `main`
- Source of truth: repository
- Main SHA tracking: dynamic
- State updated: 2026-07-26

## Phase

**Equipment Filter Regression and Model Price Ordering**

## Reference delivery

- Package: Data Products v1.8.0 Publication
- Pull Request: #288
- Verified head: `dca8b9fadf0058060fa1a2be17520bc3eedf3fb7`
- Quality run: #2023

## Verified baseline

- Tests: 1030
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

**Equipment Filter Regression and Model Price Ordering** — `complete`

Restore usable equipment filtering and selection after portfolio expansion, preserve explicit missing and unknown evidence semantics, and order model choices from the lowest recorded current catalogue price to the highest.

## Next package

**Data Products v1.8.1 Release Preparation** — `planned`

Prepare and verify a patch release containing the restored equipment filtering and cheapest-to-most-expensive model ordering, without changing source-backed data or rewriting older public releases.

## Autonomy

Mode: `autonomous_until_action_required`

Standing authorization covers package branches, manifest-scoped edits, tests and quality, package commits, pushes, Pull Requests, in-scope CI repairs, green merges, state updates and generated documentation.

Work stops only for a real source, access, authentication, policy, architecture, scope, destructive-operation or unresolved-evidence boundary. The stop message must begin with `ACTION_REQUIRED`.

## Review policy

- Review-only Pull Requests: exception only
- Milestone review interval: 5 logical packages
- One logical package per Pull Request: yes
- Automatic remote-branch deletion: no
