# Archived legacy validation utilities

These scripts are retained for historical provenance only and are not part of the current validation entry points.

- `validate.py`: early CSV readability/header check.
- `validate_data.py`: early duplicate-ID, empty-ID and CSV-header checks.

Current supported validation is provided by:
- `python tools/dkb.py validate` and `tools/validate_dkb.py` for repository-wide validation;
- `tools/validators/csv_validator.py` for strict CSV parsing and structural checks;
- `python tools/dkb.py package-preflight` for package input validation.

Do not invoke the archived scripts as current project commands.
