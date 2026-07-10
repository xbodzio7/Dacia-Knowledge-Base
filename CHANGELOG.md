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

### Changed

* The unified CLI now propagates command exit codes.
* All project CSV files are stored as valid UTF-8.
* Command usage documentation reflects the current tooling.
* Generated SQLite databases are treated as disposable local artifacts.
* Project validation is automatically executed for pushes and Pull Requests.
* Changelog formatting uses standard Markdown syntax.
* The main validator reports cross-file reference errors.
* GitHub Actions runs the unit test suite on Python 3.10 and 3.13.

### Removed

* Generated `dacia_knowledge_base.db` from version control.

### Documentation

* Standardized AI-assisted development workflow.
* Documented validation, normalization, SQLite export, search and reporting commands.
* Documented the automated GitHub Actions quality workflow.
