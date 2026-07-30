# Project State Summary

> Generated from `project/state.json`. Do not edit manually.

## Repository

- Repository: `xbodzio7/Dacia-Knowledge-Base`
- Default branch: `main`
- Source of truth: repository
- Main SHA tracking: dynamic
- State updated: 2026-07-30

## Phase

**Jogger Page 19 Minimum Kerb Weight Source Observations**

## Reference delivery

- Package: Jogger Technical Page 19 Reviewed Fact Reconciliation
- Pull Request: #392
- Verified head: `1eaa92e09e312117597474ffd8410b8abe54632e`
- Quality run: #2544

## Verified baseline

- Tests: 1640
- Master CSV files: 46
- Master rows: 11242
- Configuration values: 3383
- Configuration import specifications: 128
- Configuration value ranges: 278
- Configuration range import specifications: 22
- Availability records: 5770
- Canonical attributes: 385
- Attribute categories: 30

## Current package

**Jogger Page 19 Minimum Kerb Weight Source Observations** — `complete`

Add 22 source-specific minimum kerb weight observations from Jogger brochure page 19 for all current five- and seven-seat configurations where the printed values exactly match later official observations, without importing either mislabeled mass block.

## Next package

**Jogger Page 19 Fuel and LPG Capacity Source Observations** — `planned`

Preserve source-specific 50 L petrol-tank observations for all 22 current Jogger configurations and separate 50 L total plus 40 L filling-capacity LPG observations for the ten current Eco-G 120 configurations, without collapsing distinct capacity semantics.

## Autonomy

Mode: `autonomous_until_action_required`

Standing authorization covers package branches, manifest-scoped edits, tests and quality, package commits, pushes, Pull Requests, in-scope CI repairs, green merges, state updates and generated documentation.

Work stops only for a real source, access, authentication, policy, architecture, scope, destructive-operation or unresolved-evidence boundary. The stop message must begin with `ACTION_REQUIRED`.

## Review policy

- Review-only Pull Requests: exception only
- Milestone review interval: 5 logical packages
- One logical package per Pull Request: yes
- Automatic remote-branch deletion: no
