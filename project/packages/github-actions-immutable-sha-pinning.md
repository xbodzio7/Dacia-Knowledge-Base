# GitHub Actions Immutable SHA Pinning

Initial implementation: 2026-07-20  
Inventory correction and major-version review: 2026-07-21

## Purpose

Remove movable third-party execution references from the repository's Pull Request automation while keeping every action update explicit, reviewable and reproducible.

## Current implementation

All external GitHub-maintained action references in the fifteen Pull Request workflows use full immutable commit SHAs. Human-readable major-version comments remain beside each pin.

| Action | Immutable commit | Version comment | References |
| --- | --- | --- | ---: |
| `actions/checkout` | `3d3c42e5aac5ba805825da76410c181273ba90b1` | `v7` | 18 |
| `actions/setup-python` | `5fda3b95a4ea91299a34e894583c3862153e4b97` | `v7` | 18 |
| `actions/setup-node` | `820762786026740c76f36085b0efc47a31fe5020` | `v7` | 2 |
| `actions/upload-artifact` | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` | `v7` | 15 |
| `actions/download-artifact` | `3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c` | `v8` | 5 |

The current verified total is **58 immutable action references** across fifteen workflow files.

## Inventory correction

The initial implementation document reported 63 references:

- 19 checkout;
- 19 setup-python;
- 3 setup-node;
- 16 upload-artifact;
- 6 download-artifact.

That count included the temporary implementation helper once for each of the five actions. The helper was removed before merge and was never part of the final fifteen-workflow portfolio.

A clean post-upgrade audit excluding the temporary audit workflow confirmed the correct persistent inventory:

- 18 `actions/checkout` references;
- 18 `actions/setup-python` references;
- 2 `actions/setup-node` references;
- 15 `actions/upload-artifact` references;
- 5 `actions/download-artifact` references.

No movable GitHub-maintained action reference remains.

## Major-version update history

Dependabot identified three major updates after the immutable pinning and update channel were enabled. Each update was reapplied on the current `main` branch and validated independently:

1. PR #183 upgraded all 18 `actions/setup-python` references from v6 to v7.
2. PR #184 upgraded both `actions/setup-node` references from v6 to v7 while retaining Node.js 24.
3. PR #185 upgraded all five `actions/download-artifact` references from v7 to v8.0.1.

The original Dependabot Pull Requests #178, #179 and #180 were superseded because they were based on an older repository state. Their target commits were preserved in the replacement Pull Requests.

`actions/checkout` v7 and `actions/upload-artifact` v7 did not require a further update during this review.

## Affected workflow portfolio

The fifteen-workflow portfolio remains:

- unrestricted repository-wide `Quality`;
- configuration shortlist, shortlist HTML and selection export;
- comparison HTML, bundle and cross-platform workbook;
- versioned release and verified public release download;
- two Sandero reporting workflows;
- four Jogger reporting workflows.

## Preserved behavior

The pinning and subsequent major-version updates do not change:

- workflow event selection or governance-only path exclusions;
- permissions, concurrency groups, jobs or matrices;
- Python, Node.js or operating-system targets except the separately reviewed Python 3.14 compatibility migration;
- commands, test targets or generated products;
- artifact names, paths, checksums or retention periods;
- release publication guards;
- source data, product semantics or the immutable `data-products-v1.0.0` release.

## Validation evidence

The current action portfolio has passed:

1. Python 3.10 compatibility checks.
2. Python 3.13 compatibility checks.
3. The complete Python 3.14 quality, reporting and artifact gate.
4. Windows package publishing and canonical-state checks on Python 3.14.
5. Every discovery, selection, comparison and reporting workflow.
6. Byte-identical Linux and Windows workbook verification using `download-artifact` v8.
7. Independent Linux and Windows download, offline verification and byte-identical index comparison for public `data-products-v1.0.0` using `download-artifact` v8.

## Resolved maintenance item

The README reporting-portfolio drift previously tracked as issue #173 was resolved by merged PR #176.

## Result

GitHub Actions execution dependencies are immutable, current major-version updates have been verified, and the persistent inventory is accurately recorded as 58 references. Future action releases remain explicit Dependabot Pull Requests rather than silent tag movement.
