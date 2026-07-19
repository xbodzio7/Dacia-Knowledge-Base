# Project State Summary

> Generated from `project/state.json`. Do not edit manually.

## Repository

- Repository: `xbodzio7/Dacia-Knowledge-Base`
- Default branch: `main`
- Source of truth: repository
- Main SHA tracking: dynamic
- State updated: 2026-07-19

## Phase

**Source-Backed Model Expansion**

## Reference delivery

- Package: Jogger Minimum Kerb Weight Modeling and Import
- Pull Request: #112
- Verified head: `de9f8b2c409db2d76bb2b14cfa75a7aa6c55a7a8`
- Quality run: #472

## Verified baseline

- Tests: 476
- Master CSV files: 34
- Master rows: 3753
- Configuration values: 1128
- Configuration import specifications: 65
- Availability records: 1811
- Canonical attributes: 352
- Attribute categories: 30

## Current package

**Jogger Cargo Measurement Modeling and Import** — `active`

Add two measurement-specific VDA cargo attributes and materialize 44 exact page-6 observations while keeping generic boot-capacity concepts unchanged.

## Next package

**Jogger LPG Capacity Modeling Review** — `planned`

Separate total LPG vessel capacity from filling capacity before importing the source-stated 50/40 L pairs for all active Eco-G configurations.

## Autonomy

Mode: `autonomous_until_action_required`

Standing authorization covers package branches, manifest-scoped edits, tests and quality, package commits, pushes, Pull Requests, in-scope CI repairs, green merges, state updates and generated documentation.

Work stops only for a real source, access, authentication, policy, architecture, scope, destructive-operation or unresolved-evidence boundary. The stop message must begin with `ACTION_REQUIRED`.

## Review policy

- Review-only Pull Requests: exception only
- Milestone review interval: 5 logical packages
- One logical package per Pull Request: yes
- Automatic remote-branch deletion: no
