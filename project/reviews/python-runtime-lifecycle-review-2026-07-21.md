# Python Runtime Lifecycle Review

Date: 2026-07-21

## Purpose

Review the repository's Python CI baseline against the current upstream Python support lifecycle before changing runtime versions in product workflows.

## Repository evidence

The repository-wide `Quality` workflow currently:

- tests Python 3.10 and Python 3.13 on Linux;
- runs compile, unit, orchestration-contract and canonical-state checks on Python 3.10;
- runs the full quality and generated-artifact gate on Python 3.13;
- runs the Windows package workflow on Python 3.13.

No current Pull Request workflow verifies Python 3.14.

## Upstream lifecycle evidence

As of this review:

- Python 3.14 is the current stable feature line and receives regular bugfix releases;
- Python 3.13 remains in regular bugfix support;
- Python 3.10 receives security fixes only and reaches end of support in October 2026.

## Decision

The next compatibility package will verify Python 3.14 in the repository-wide `Quality` workflow before any wider workflow migration.

The verification package will:

1. add Python 3.14 to the Linux quality matrix;
2. run the full quality and generated-artifact gate on Python 3.14;
3. retain Python 3.10 as the temporary lower-bound compatibility lane;
4. retain Python 3.13 as an intermediate compatibility lane during the transition;
5. move the Windows package workflow to Python 3.14 only after the Linux full gate is represented in the same Pull Request;
6. require the complete existing Pull Request workflow portfolio to remain green.

## Python 3.10 boundary

This review does not remove Python 3.10 support. Its retirement requires a separate evidence-backed package no later than the upstream October 2026 end-of-support boundary.

Until then, Python 3.10 remains useful as the repository's lower-bound syntax and unit-test lane.

## Unchanged scope

This review does not change:

- source data or product semantics;
- Python source code;
- workflow files or runtime versions;
- generated artifacts or release assets;
- the immutable `data-products-v1.0.0` release;
- the verified 667-test baseline.

## Result

The repository has an explicit, staged runtime transition path: first prove the complete product gate on Python 3.14, then consider broader workflow migration, while tracking Python 3.10 retirement as a separate maintenance boundary.
