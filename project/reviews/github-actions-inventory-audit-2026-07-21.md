# GitHub Actions Inventory Audit

Date: 2026-07-21

## Scope

Audit the persistent external GitHub-maintained action references in the fifteen Pull Request workflow files after the Python 3.14 migration and the setup-python v7, setup-node v7 and download-artifact v8 upgrades.

The temporary audit workflow was explicitly excluded from the scanned workflow set and removed before final review.

## Method

The audit parsed every `.github/workflows/*.yml` file in the persistent fifteen-workflow portfolio and required each supported external action reference to match:

- the `actions/<name>` repository form;
- a full 40-character hexadecimal commit SHA;
- a same-line human-readable major-version comment.

It also rejected movable action references and required every occurrence of a given action to use one consistent SHA and version comment.

## Verified inventory

| Action | References | Immutable commit | Version comment |
| --- | ---: | --- | --- |
| `actions/checkout` | 18 | `3d3c42e5aac5ba805825da76410c181273ba90b1` | `v7` |
| `actions/setup-python` | 18 | `5fda3b95a4ea91299a34e894583c3862153e4b97` | `v7` |
| `actions/setup-node` | 2 | `820762786026740c76f36085b0efc47a31fe5020` | `v7` |
| `actions/upload-artifact` | 15 | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` | `v7` |
| `actions/download-artifact` | 5 | `3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c` | `v8` |

Total: **58 references across 15 workflow files**.

## Correction analysis

The original pinning document reported 63 references. The five-reference difference was caused by including the temporary implementation helper in the pre-removal inventory. That helper contained exactly one occurrence of each of the five actions and was not present in the final merged workflow portfolio.

Subtracting those five temporary occurrences produces the persistent counts independently confirmed by this audit.

## Upgrade completion

The current inventory includes:

- setup-python v7 from merged PR #183;
- setup-node v7 from merged PR #184;
- download-artifact v8.0.1 from merged PR #185.

The replacement Pull Requests preserved the exact target commits proposed by Dependabot while rebasing the changes onto the current repository state.

## Validation boundary

This report changes no workflow, action reference, runtime, product source, generated artifact or public release. The final package must retain:

- green Python 3.10 and Python 3.13 compatibility lanes;
- the complete Python 3.14 quality and artifact gate;
- green Windows package-state validation;
- byte-identical workbook and workspace-index checks;
- independent verification of immutable public `data-products-v1.0.0`.

## Result

The repository has a reproducible, helper-free and internally consistent inventory of 58 immutable GitHub Actions references. The corrected package documentation and canonical project state now match the actual persistent workflow portfolio.
