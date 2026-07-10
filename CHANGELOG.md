\# Changelog



All notable changes to this project will be documented in this file.



\## Unreleased



\### Added



\* Reproducible and atomic SQLite database builder.

\* Optional SQLite output path through `--output`.

\* CSV encoding inspection and Windows-1250 to UTF-8 normalization tool.

\* Unified CLI commands for SQLite builds and encoding normalization.



\### Changed



\* The unified CLI now propagates command exit codes.

\* All project CSV files are stored as valid UTF-8.

\* Command usage documentation reflects the current tooling.

\* Generated SQLite databases are treated as disposable local artifacts.



\### Removed



\* Generated `dacia\_knowledge\_base.db` from version control.



\### Documentation



\* Standardized AI-assisted development workflow.

\* Documented validation, normalization, SQLite export, search and reporting commands.
