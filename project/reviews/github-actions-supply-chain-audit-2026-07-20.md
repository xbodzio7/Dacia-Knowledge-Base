# GitHub Actions Supply-Chain Audit

Date: 2026-07-20

## Purpose

Establish the first evidence-backed security package selected from `Maintenance Watch` without changing source data, product behavior, release assets or reporting semantics.

## Findings

### Mutable action references

The Pull Request workflows use GitHub-maintained actions through movable major-version tags:

- `actions/checkout@v7`
- `actions/setup-python@v6`
- `actions/setup-node@v6`
- `actions/upload-artifact@v7`
- `actions/download-artifact@v7`

A movable tag can be updated to a different commit after repository review. GitHub's secure-use guidance identifies a full-length commit SHA as the immutable reference form and allows repository policy to require it, including for actions authored by GitHub.

### Verified current tag targets

Each current tag was resolved directly in its owning GitHub repository on 2026-07-20:

| Action tag | Verified full commit SHA |
| --- | --- |
| `actions/checkout@v7` | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| `actions/setup-python@v6` | `ece7cb06caefa5fff74198d8649806c4678c61a1` |
| `actions/setup-node@v6` | `249970729cb0ef3589644e2896645e5dc5ba9c38` |
| `actions/upload-artifact@v7` | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` |
| `actions/download-artifact@v7` | `37930b1c2abaa49bbe596cd826c3c89aef350131` |

The selected implementation will preserve the existing major-version intent by replacing only each tag suffix with the exact commit currently addressed by that tag. Inline comments will retain the human-readable major version.

## Workflow scope

The repository currently has fifteen Pull Request workflows:

- the unrestricted `Quality` workflow;
- six configuration discovery, selection and comparison workflows;
- two release workflows;
- two Sandero reporting workflows;
- four Jogger reporting workflows.

The implementation package must update every external `uses:` reference in those workflows. Local commands, permissions, triggers, matrices, artifacts and retention policies remain unchanged.

## Separate documentation finding

The maintenance review also found stale Duster reporting statements in `README.md`. Merged PR #142 completed all thirteen independent reporting scopes, including seven Duster scopes, while the README still describes Duster as waiting for promotion.

The correction is tracked separately as issue #173 because it is an independent documentation package.

## Selected next package

`GitHub Actions Immutable SHA Pinning`

Acceptance criteria:

1. Replace all five movable action tags with the verified full SHAs above.
2. Keep an inline version comment on each reference, for example `# v7`.
3. Change no workflow commands, inputs, permissions, events, matrices or artifact contracts.
4. Run all fifteen workflows because workflow files are changed.
5. Require `Quality` success on Python 3.10, Python 3.13 and Windows.
6. Reverify the immutable public `data-products-v1.0.0` download workflow.

## Deferred scope

This audit does not:

- enable a new repository or organization Actions policy;
- introduce Dependabot or another update service;
- upgrade any action to a different major version;
- modify source data, product code, tests or release assets;
- resolve issue #173 in the same package.
