# Governance-Only CI Verification

## Purpose

Verify the `Governance-Only CI Scope Reduction` package through a real Pull Request whose complete changed-file set is limited to the three explicitly ignored governance surfaces.

## Candidate changed-file set

This verification package changes only:

- `project/state.json`,
- `project/STATE_SUMMARY.md`,
- `project/reviews/governance-only-ci-verification-2026-07-20.md`.

No workflow, package document, source data, Python code, tests, README, changelog or release asset is changed.

## Expected workflow selection

The Pull Request must select exactly one workflow:

- `Quality`.

The following fourteen specialized workflows must not be selected:

1. `Configuration Selection Export`,
2. `Versioned Data Product Release`,
3. `Verified Data Product Release Download`,
4. `Configuration Comparison Workbook`,
5. `Configuration Comparison Bundle`,
6. `Configuration Shortlist`,
7. `Configuration Shortlist HTML`,
8. `Configuration Comparison HTML`,
9. `Sandero Eco-G 120 Manual Reporting`,
10. `Sandero Stepway Eco-G 120 Automatic Reporting`,
11. `Jogger Eco-G 120 Manual Reporting`,
12. `Jogger Eco-G 120 Automatic Reporting`,
13. `Jogger TCe 110 Manual Reporting`,
14. `Jogger Hybrid 155 Automatic Reporting`.

## Quality acceptance criteria

`Quality` must complete successfully for:

- Python 3.10 unit, orchestration and canonical-state checks,
- Python 3.13 full quality and artifact generation,
- Windows package publishing and canonical-state checks.

## Interpretation

If exactly `Quality` is selected and it passes, the CI scope reduction is proven operational:

- governance-only maintenance retains a complete repository-wide safety gate,
- specialized product workflows are not executed when their inputs and behavior cannot change,
- any future change outside the three ignored paths continues to select the specialized workflows according to GitHub path-filter semantics.

## Boundary

The verification does not change the 667-test baseline, source data, product behavior, workflow definitions, release assets or immutable `data-products-v1.0.0` identity.

After successful verification, the project remains in `Maintenance Mode` and moves to `Maintenance Watch`, where new work must be selected from concrete bug, security, dependency, CI reliability, compatibility or documentation evidence.
