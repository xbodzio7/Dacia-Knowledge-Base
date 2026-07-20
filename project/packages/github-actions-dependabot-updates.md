# GitHub Actions Dependabot Updates

Date: 2026-07-20

## Purpose

Add a controlled update channel for the repository's immutable GitHub Actions commit pins.

## Evidence

The fifteen Pull Request workflows contain 63 external GitHub-maintained action references pinned to full commit SHAs. The repository had no `.github/dependabot.yml` file and no Renovate configuration, so future action releases and security fixes required manual discovery.

GitHub's supported `github-actions` Dependabot ecosystem can inspect workflow references that use repository syntax, including full commit SHAs. Inline version comments remain updateable beside those SHAs.

## Implemented configuration

The new `.github/dependabot.yml` file:

- uses Dependabot configuration version 2;
- monitors the `github-actions` ecosystem from repository directory `/`;
- checks for version updates weekly;
- limits concurrent update Pull Requests to five;
- uses the commit-message prefix `chore(actions)`.

## Security model

Dependabot may propose updated immutable commits, but it does not merge them automatically. Every proposed action update remains an explicit Pull Request and must pass the repository's normal workflow portfolio before merge.

The package preserves the existing supply-chain controls:

- workflow execution continues to use full immutable commit SHAs;
- human-readable major-version comments remain beside each pin;
- action updates remain reviewable diffs rather than silent tag movement;
- repository permissions and workflow behavior are unchanged.

## Unchanged scope

This package does not change:

- any current action commit SHA;
- workflow triggers, jobs, matrices, commands or permissions;
- Python, Node.js or operating-system versions;
- source data, product semantics or generated products;
- the immutable `data-products-v1.0.0` release;
- the verified 667-test baseline.

## Validation contract

1. `.github/dependabot.yml` is valid YAML with Dependabot schema version 2.
2. The only configured package ecosystem is `github-actions`.
3. The monitored directory is `/` and the interval is `weekly`.
4. No automatic merge mechanism is introduced.
5. The final diff contains this package record, Dependabot configuration and canonical state files only.
6. Normal Quality validation succeeds.

## Result

Immutable GitHub Actions references now have a supported, review-first update channel. The repository can receive explicit Pull Requests for new action releases while retaining SHA pinning and existing CI gates.
