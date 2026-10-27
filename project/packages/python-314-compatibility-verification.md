# Python 3.14 Compatibility Verification

Date: 2026-07-21

## Purpose

Verify the complete repository quality and package workflow on Python 3.14 while retaining explicit transition coverage for Python 3.10 and Python 3.13.

## Implemented runtime matrix

The Linux `Quality` matrix now contains:

- Python 3.10;
- Python 3.13;
- Python 3.14.

Python 3.10 and Python 3.13 run the lightweight compatibility lane:

- source compilation;
- the complete unit-test discovery suite;
- orchestration contract tests;
- canonical project-state validation.

Python 3.14 runs the complete product gate:

- PDF extraction backend verification;
- the full `tools/dkb.py quality` gate;
- comparison catalogs and summaries;
- all seven Duster reporting artifact groups;
- quality artifact manifest generation;
- deterministic artifact upload.

The Windows package workflow now also uses Python 3.14 for package publishing tests and canonical-state validation.

## Deterministic change inventory

The workflow rewrite:

- adds one Python 3.14 matrix entry;
- generalizes four Python 3.10-only conditions to run on every non-3.14 compatibility lane;
- moves thirteen full-gate conditions from Python 3.13 to Python 3.14;
- changes one Windows runtime declaration from Python 3.13 to Python 3.14.

## Preserved behavior

This package does not change:

- Python source code or test definitions;
- test discovery patterns or contract-test selection;
- quality commands, reporting specifications or source dates;
- artifact names, paths or retention periods;
- workflow permissions, triggers or concurrency;
- source data, product semantics or release assets;
- the immutable `data-products-v1.0.0` release;
- the verified 667-test baseline.

## Validation contract

The final Pull Request must demonstrate:

1. Python 3.10 compatibility checks succeed.
2. Python 3.13 compatibility checks succeed.
3. Python 3.14 completes the full quality and artifact gate.
4. Windows completes package publishing and canonical-state checks on Python 3.14.
5. Every specialized Pull Request workflow remains green.
6. Public `data-products-v1.0.0` download and offline verification remain green on Linux and Windows.
7. No temporary generator remains in the final diff.

## Python 3.10 boundary

Python 3.10 remains a temporary lower-bound lane. Its removal is not part of this package and requires a separate retirement-readiness review before the upstream October 2026 end-of-support boundary.

## Result

The repository's complete quality and package baseline is now exercised on the current stable Python 3.14 line, with explicit compatibility coverage retained for Python 3.10 and Python 3.13 during the transition.
