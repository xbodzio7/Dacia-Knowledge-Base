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
* Dedicated dictionary for technical attribute categories.
* Cross-file validation of attribute category references.
* Execution of declarative validation rules against attributes.
* Separate reporting of data-rule errors and warnings.
* SQLite parity verification for tables and row counts.
* Unified `sqlite-verify` CLI command.
* Full SQLite schema and row-content comparison with source CSV files.
* Regression tests for atomic SQLite build safety and failure recovery.
* Regression tests for CSV search, statistics, CLI routing, encoding normalization and Markdown reporting.
* Unified `quality` CLI command for the complete local quality gate.
* Unit tests for quality-step orchestration and failure propagation.
* Source registry for seven official Sandero and Sandero Stepway configuration documents.
* Source-to-model, source-to-version and source-to-configuration relationships.
* Five Sandero and Sandero Stepway trim records.
* Seven source-backed Eco-G 120 configuration records.
* PLN currency catalogue entry.
* Seven dated Polish catalogue gross price observations.
* Configuration-level technical observation dataset with date and source traceability.
* Thirty-five basic technical observations for seven Sandero configurations.
* Forty-nine performance, towing and weight observations.
* Eighty-four source-backed technical observations in total.
* Cross-file reference and status rules for the new source-backed data tables.

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
* Cross-file search exports use aligned columns and exclude their own output file from scanning.
* Dataset statistics analyze only source CSV files under `data/master`.
* Entity catalogs and data dictionaries analyze only source CSV files under `data/master`.
* Search and reporting tools accept UTF-8 CSV files with an optional BOM.
* Cross-file validation now covers 29 declared relationships.
* Lifecycle and catalogue status validation now covers 18 declared rules.
* The verified master-data baseline now contains 32 CSV files and 678 rows.
* SQLite verification now covers 32 tables and 678 rows.

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
* Synchronized `ROADMAP.md` and `SESSION_STATE.md` with the completed tooling and quality baseline.
* Replaced outdated tooling placeholders with the next source-backed data expansion phase.
* Normalized project state documents to standard Markdown syntax.
* Synchronized project documentation with the Sandero source, version, configuration and price packages merged through PRs #3–#6.
* Synchronized project documentation with the technical observation packages merged through PRs #8 and #9.
