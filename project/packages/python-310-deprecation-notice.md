# Python 3.10 Deprecation Notice

Date: 2026-07-21

## Purpose

Publish a clear user-facing transition policy before changing the repository's minimum supported Python version.

## Current contract

This package preserves the current formal requirement:

```toml
requires-python = ">=3.10"
```

Python 3.10 remains supported and continues to have a dedicated compatibility lane in the repository-wide `Quality` workflow.

## Published notice

README now states that:

- the current minimum remains Python 3.10;
- Python 3.10 support is deprecated;
- support will end before or with upstream end of support in October 2026;
- Python 3.13 is the intended next minimum;
- Python 3.14 is recommended for new environments;
- the actual minimum-version change will occur in a separate package.

The durable guide `project/guides/python-runtime-support.md` records the complete support policy, verified runtime lanes and coordinated retirement requirements.

## Verified runtime policy

| Runtime | Role during transition |
| --- | --- |
| Python 3.10 | Current minimum and temporary compatibility lane |
| Python 3.13 | Intended next minimum and compatibility lane |
| Python 3.14 | Primary complete quality, reporting and artifact lane |
| Python 3.14 on Windows | Package publishing and canonical-state validation |

## Unchanged technical surfaces

This notice does not change:

- `requires-python = ">=3.10"`;
- Ruff `target-version = "py310"`;
- the Python 3.10 CI lane;
- Python source code or tests;
- workflow runtime versions or commands;
- source data, product semantics or generated products;
- immutable public `data-products-v1.0.0`;
- the verified 667-test baseline.

## Later retirement package

The planned **Python 3.10 Retirement Implementation** must change all support surfaces together:

1. package metadata to `requires-python = ">=3.13"`;
2. Ruff target to `py313`;
3. the Quality matrix by removing Python 3.10;
4. README and runtime-support guide to state the new active minimum;
5. any tests or contracts that explicitly validate the support floor.

It must retain Python 3.13 compatibility, the complete Python 3.14 gate, Windows validation and all fifteen normal Pull Request workflows.

## Result

Repository users receive advance notice of the planned support-floor change while Python 3.10 remains fully supported during the transition period.
