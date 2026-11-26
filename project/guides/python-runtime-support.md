# Python Runtime Support

Date: 2026-07-21

## Current minimum

Dacia Knowledge Base currently declares Python 3.10 or newer through:

```toml
requires-python = ">=3.10"
```

Python 3.10 remains supported during the deprecation period. The repository continues to compile its sources, run the complete unit-test suite, execute orchestration contracts and validate canonical project state on Python 3.10.

## Verified runtime lanes

The repository-wide quality workflow directly verifies:

| Runtime | Validation role |
| --- | --- |
| Python 3.10 | Temporary lower-bound compatibility lane |
| Python 3.13 | Intended next minimum and compatibility lane |
| Python 3.14 | Primary complete quality, reporting and artifact lane |
| Python 3.14 on Windows | Package publishing and canonical-state validation |

Python versions allowed by package metadata but not listed above are not separate CI lanes.

## Deprecation notice

Support for Python 3.10 is deprecated.

Python 3.10 is in upstream security-fixes-only maintenance and reaches end of support in October 2026. The repository plans to raise its minimum supported runtime to Python 3.13 no later than that upstream boundary.

This notice does not change the current minimum version. Python 3.10 remains supported until a separate retirement Pull Request is merged.

## Planned retirement package

The later coordinated retirement package must change all support surfaces together:

- `requires-python` from `>=3.10` to `>=3.13`;
- Ruff `target-version` from `py310` to `py313`;
- the repository-wide quality matrix by removing Python 3.10;
- README and this support guide;
- any package or consumer documentation that states the minimum runtime.

The package must retain:

- Python 3.13 as the lower-bound compatibility lane;
- Python 3.14 as the complete quality, reporting and artifact lane;
- Windows package-state validation on Python 3.14;
- the complete fifteen-workflow Pull Request validation portfolio;
- independent verification of immutable public `data-products-v1.0.0`.

## Recommendation for new environments

Use Python 3.14 for new local environments. It is the repository's primary fully validated runtime.

Use Python 3.13 when a conservative lower-bound environment is required.

Do not start new long-lived integrations on Python 3.10, because its support is scheduled for removal before or at the upstream October 2026 end-of-support boundary.

## Release boundary

The runtime-support policy applies to repository tools and automation. The existing offline assets in `data-products-v1.0.0` remain immutable and are not rebuilt or altered by this notice.
