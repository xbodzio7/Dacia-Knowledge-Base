# GitHub Actions Immutable SHA Pinning

Date: 2026-07-20

## Purpose

Remove movable third-party execution references from the repository's Pull Request automation while preserving the exact action versions and all existing workflow behavior.

## Implemented change

All external GitHub-maintained action references in the fifteen Pull Request workflows now use full immutable commit SHAs. Human-readable major-version comments remain beside each pin.

| Action | Immutable commit | Version comment |
| --- | --- | --- |
| `actions/checkout` | `3d3c42e5aac5ba805825da76410c181273ba90b1` | `v7` |
| `actions/setup-python` | `ece7cb06caefa5fff74198d8649806c4678c61a1` | `v6` |
| `actions/setup-node` | `249970729cb0ef3589644e2896645e5dc5ba9c38` | `v6` |
| `actions/upload-artifact` | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` | `v7` |
| `actions/download-artifact` | `37930b1c2abaa49bbe596cd826c3c89aef350131` | `v7` |

## Replacement inventory

The deterministic rewrite replaced 63 movable references:

- 19 `actions/checkout@v7` references;
- 19 `actions/setup-python@v6` references;
- 3 `actions/setup-node@v6` references;
- 16 `actions/upload-artifact@v7` references;
- 6 `actions/download-artifact@v7` references.

The affected workflow portfolio remains:

- unrestricted repository-wide `Quality`;
- configuration shortlist, shortlist HTML and selection export;
- comparison HTML, bundle and cross-platform workbook;
- versioned release and verified public release download;
- two Sandero reporting workflows;
- four Jogger reporting workflows.

## Preserved behavior

The package does not change:

- workflow event selection or governance-only path exclusions;
- permissions, concurrency groups, jobs or matrices;
- Python, Node.js or operating-system versions;
- commands, test targets or generated artifacts;
- artifact names, paths, checksums or retention periods;
- release publication guards;
- source data, product semantics or the immutable `data-products-v1.0.0` release.

## Validation contract

Because all fifteen workflow files changed, every current Pull Request workflow must be selected on the final candidate.

Required evidence:

1. `Quality` succeeds on Python 3.10.
2. The full Python 3.13 quality and artifact gate succeeds.
3. Windows package publishing and canonical-state checks succeed.
4. Every discovery, selection, comparison and reporting workflow succeeds.
5. The release candidate workflow succeeds without publication.
6. The verified release-download workflow independently downloads and verifies public `v1.0.0` on Linux and Windows.
7. No temporary workflow remains in the final diff.

## Separate maintenance item

README reporting-portfolio drift remains tracked as issue #173. It is not combined with this security package.

## Result

GitHub Actions execution dependencies are now immutable at the repository level while their reviewed major-version intent remains visible. Future action updates must be explicit commit changes rather than silent tag movement.
