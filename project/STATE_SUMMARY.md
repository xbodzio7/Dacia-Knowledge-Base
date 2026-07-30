# Project State Summary

> Generated from `project/state.json`. Do not edit manually.

## Repository

- Repository: `xbodzio7/Dacia-Knowledge-Base`
- Default branch: `main`
- Source of truth: repository
- Main SHA tracking: dynamic
- State updated: 2026-07-30

## Phase

**Jogger Page 19 Gross Vehicle Weight Source Observations**

## Reference delivery

- Package: Jogger Technical Page 19 Reviewed Fact Reconciliation
- Pull Request: #392
- Verified head: `1eaa92e09e312117597474ffd8410b8abe54632e`
- Quality run: #2544

## Verified baseline

- Tests: 1655
- Master CSV files: 46
- Master rows: 11306
- Configuration values: 3447
- Configuration import specifications: 132
- Configuration value ranges: 278
- Configuration range import specifications: 22
- Availability records: 5770
- Canonical attributes: 385
- Attribute categories: 30

## Current package

**Jogger Page 19 Gross Vehicle Weight Source Observations** — `complete`

Add 22 source-specific gross vehicle weight observations from Jogger brochure page 19 where every printed kilogram value exactly matches the later official source, without importing either adjacent mislabeled mass block.

## Next package

**Jogger Page 19 Non-Hybrid Braked Trailer Weight Source Observations** — `planned`

Add the matching 1200 kg brochure-source braked trailer observations for the 16 current TCe 110 and Eco-G 120 configurations while explicitly excluding all six Hybrid 155 configurations because their later official value is 1000 kg.

## Autonomy

Mode: `autonomous_until_action_required`

Standing authorization covers package branches, manifest-scoped edits, tests and quality, package commits, pushes, Pull Requests, in-scope CI repairs, green merges, state updates and generated documentation.

Work stops only for a real source, access, authentication, policy, architecture, scope, destructive-operation or unresolved-evidence boundary. The stop message must begin with `ACTION_REQUIRED`.

## Review policy

- Review-only Pull Requests: exception only
- Milestone review interval: 5 logical packages
- One logical package per Pull Request: yes
- Automatic remote-branch deletion: no
