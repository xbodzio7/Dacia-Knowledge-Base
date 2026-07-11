# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Added

* Reproducible and atomic SQLite database builder.
* Optional SQLite output path through `--output`.
* CSV encoding inspection and Windows-1250 to UTF-8 normalization tool.
* Unified CLI commands for SQLite builds and encoding normalization.
* GitHub Actions workflow for automated data quality checks.
* Automated SQLite integrity verification on Python 3.10 and 3.13.
* Temporary CI artifacts containing the generated SQLite database and validation report.
* Cross-file reference validation for models, engines, gearboxes and lookup tables.
* Unit tests for CSV reference validation.
* Strict UTF-8 CSV structure validation with header and row checks.
* Unit tests for malformed CSV files and encoding failures.
* Repository-wide uniqueness validation for `id` and `code` columns.
* Unit tests for duplicate and missing CSV key values.
* CLI integration test for the complete validation command.
* Validation of production and availability year ranges.
* Unit tests for malformed, missing and reversed year ranges.
* Validation of status vocabularies and lifecycle consistency.
* Unit tests for invalid statuses and lifecycle mismatches.
* Validation of association availability against parent lifetimes.
* Unit tests for association ranges outside parent lifetimes.
* Validation of duplicate and overlapping association intervals.
* Unit tests for repeated association interval conflicts.
* Validation of declarative rule contracts against the current schema.
* Unit tests for invalid rule fields, syntax, severity and targets.

### Changed

* The unified CLI now propagates command exit codes.
* All project CSV files are stored as valid UTF-8.
* Command usage documentation reflects the current tooling.
* Generated SQLite databases are treated as disposable local artifacts.
* Project validation is automatically executed for pushes and Pull Requests.
* Changelog formatting uses standard Markdown syntax.
* The main validator reports cross-file reference errors.
* GitHub Actions runs the unit test suite on Python 3.10 and 3.13.
* The CSV validator no longer accepts legacy Windows-1250 input.
* Generated validation reports are treated as disposable local and CI artifacts.
* The attribute-only uniqueness check now covers every master CSV table.

### Fixed

* Restored the executable validation entry point after it was accidentally emptied.
* Validation CI now detects commands that return success without running the validator.

### Removed

* Generated `dacia_knowledge_base.db` from version control.
* Generated `reports/validation_report.md` from version control.

### Documentation

* Standardized AI-assisted development workflow.
* Documented validation, normalization, SQLite export, search and reporting commands.
* Documented the automated GitHub Actions quality workflow.
