# Repository cleanup — phase 6

**Date:** 2026-11-20  
**Base:** `main` at `66626ee8afa81b46a3c7bc5b97662cc6aa9e88bf`

## Archived redundant legacy validators

Moved, without changing their source contents:

- `tools/validate.py` → `Archiwum/old_tools/validate.py`
- `scripts/validate_data.py` → `Archiwum/old_tools/validate_data.py`

The older scripts are superseded by the integrated `tools/dkb.py validate` / `tools/validate_dkb.py` validation path and the strict `tools/validators/csv_validator.py` implementation. The current CLI and dedicated tests exercise the supported validators; the old scripts are not registered as DKB CLI commands or imported by the current validator tests.

Updated `.github/workflows/quality.yml` so Ruff and compileall scan the active `tools/` and `tests/` trees rather than the now-retired `scripts/` directory.

## Safety

- Both legacy source files are preserved verbatim under `Archiwum/old_tools/`.
- Current validators, tests, package preflight and all master data remain unchanged.
- No local tests are claimed; the required CI suite must validate the workflow edit and exact PR head.
