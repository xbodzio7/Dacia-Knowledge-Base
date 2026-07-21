# Python 3.10 Retirement Readiness

Date: 2026-07-21

## Purpose

Determine whether Python 3.10 can be removed from the repository support contract now, and define the evidence and sequencing required for a safe retirement before upstream end of support.

## Upstream lifecycle

Python 3.10 is in security-fixes-only maintenance and reaches upstream end of support in October 2026.

Python 3.13 and Python 3.14 remain in regular bugfix maintenance. The repository has already verified:

- compile, unit, orchestration-contract and canonical-state checks on Python 3.13;
- the complete quality, reporting and artifact gate on Python 3.14;
- Windows package-state validation on Python 3.14.

## Repository support contract

Python 3.10 is not only an internal CI lane.

`pyproject.toml` currently declares:

```toml
requires-python = ">=3.10"
```

The Ruff configuration also declares:

```toml
target-version = "py310"
```

The repository-wide `Quality` workflow contains an explicit Python 3.10 compatibility lane. README commands use the generic `python` executable and do not currently state a minimum supported version or a deprecation schedule.

## Readiness result

**Python 3.10 must not be removed immediately.**

Removing only the CI lane would create an inconsistent repository contract because package metadata and lint target would continue to promise Python 3.10 compatibility.

Changing all three surfaces at once without prior notice would be a user-visible breaking change for anyone running the repository tools with Python 3.10.

## Required retirement sequence

A safe retirement requires two distinct packages.

### 1. Python 3.10 deprecation notice

The repository must first publish a clear runtime-support statement that:

- Python 3.10 remains supported during the transition period;
- Python 3.13 is the intended next minimum supported runtime;
- Python 3.14 is the primary full-quality and Windows validation runtime;
- Python 3.10 support is planned to end no later than its upstream October 2026 end-of-support boundary;
- the actual minimum-version change will occur in a separate Pull Request.

This notice must be visible from README and preserved in durable project documentation.

### 2. Python 3.10 retirement implementation

Only after the notice package is merged may a later implementation package:

- change `requires-python` from `>=3.10` to `>=3.13`;
- change Ruff `target-version` from `py310` to `py313`;
- remove Python 3.10 from the `Quality` matrix;
- retain Python 3.13 as the lower-bound compatibility lane;
- retain Python 3.14 as the complete quality and artifact lane;
- update user-facing runtime documentation;
- run the complete fifteen-workflow validation portfolio.

## Removal criteria

The implementation package is authorized only when all of the following remain true:

1. Python 3.13 compile, unit, orchestration-contract and state checks are green.
2. Python 3.14 completes the full quality, reporting and artifact gate.
3. Windows package-state validation is green on Python 3.14.
4. No source, test or tool depends on Python 3.10-only behavior.
5. The deprecation notice has been merged and is visible to repository users.
6. Package metadata, lint target, CI matrix and documentation change together in one logical package.
7. Public `data-products-v1.0.0` remains independently verifiable and unchanged.

## Unchanged scope

This readiness review does not change:

- `requires-python` or Ruff target version;
- the Python 3.10 CI lane;
- Python source code or tests;
- source data, product semantics or generated artifacts;
- the immutable public release;
- the verified 667-test baseline.

## Decision

The repository is technically capable of moving its lower bound to Python 3.13, but it is not procedurally ready to remove Python 3.10 today.

The next package is **Python 3.10 Deprecation Notice**. The actual removal remains a separate later package after that notice is published.
