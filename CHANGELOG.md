# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Added

* Self-contained interactive configuration shortlist HTML with a full source-backed browser catalog and CLI-defined initial filters.
* JavaScript/Python semantic parity tests for metadata, price, seat and equipment shortlist filters.
* Evidence-aware configuration shortlist CLI with model, version, powertrain, transmission, price, seat and equipment filters.
* Deterministic JSON, Markdown and CSV shortlist artifacts with explicit unknown and exclusion reporting.
* Self-contained interactive HTML configuration comparison reports with offline filtering, source provenance and evidence-aware states.
* GitHub Actions publication of current Sandero browser reports with a SHA-256 artifact manifest.
* Source-backed Jogger equipment availability with 1,166 records across 53 canonical attributes and explicit standard, optional and unavailable semantics.
* Jogger Hybrid 155 total system power modeled as a dedicated attribute with six source-backed 116 kW observations.
* Jogger MY26 total LPG vessel and filling capacities modeled as separate attributes with 20 source-backed LPG observations.
* Jogger MY26 cargo measurements modeled as two VDA height-specific attributes with 44 source-backed observations.
* Jogger MY26 minimum kerb weight modeled as a dedicated attribute with 22 source-backed five-/seven-seat observations.
* Jogger MY26 gearbox reconciliation with 38 exact configuration observations and current mt6, EDC6 and e-DHT 155 model associations.
* Thirty-two exact Jogger injection-type observations with explicit petrol/LPG contexts and controlled existing-enum mappings.
* Exact repository archival of the official Polish Jogger MY26 PDF with verified SHA-256.
* Source-backed Jogger catalogue foundation with 4 versions, 22 configurations, 22 prices and explicit five-/seven-seat observations.
* 312 exact Jogger page-6 technical observations in 17 declarative import specifications with fuel and seat-count contexts.
* Regression coverage for the Jogger source hash, group denominators, context preservation and deferred ranges.
* Explicit Duster Eco-G 120 reporting subset with complete technical, equipment, price and source coverage plus six deterministic trim comparisons.
* Source-backed Duster III equipment availability with 1,392 records across 58 canonical attributes and explicit standard, optional and unavailable semantics.
* Source-backed Duster III technical import with 392 observations across 17 canonical attributes, explicit fuel context and conservative exclusion of trim-ambiguous values.
* Duster III catalogue gross prices for all 24 source-supported configurations, dated 2026-02-06 and separated from promotional discount and financing claims.
* Source-backed Duster III catalogue bootstrap with 5 active versions, 24 explicit version/powertrain configurations and complete source relationships.
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
* Safe package workflow commands for branch creation, review and finish checks.
* Integration tests for package workflow behavior in temporary Git repositories.
* Durable `package-publish` command for exact manifest-driven staging, commit, finish and explicitly authorized push.
* Versioned quality receipts bound to branch, base SHA, commit subject, exact paths, an isolated Git tree and raw file bytes.
* Stable `handoff.json` and complete publication logs for machine-verifiable package transfer.
* Regression coverage for receipt rejection, one-byte changes, exact staging, failed finish, failed push, safe resume and Polish UTF-8 paths.
* Source registry for seven official Sandero and Sandero Stepway configuration documents.
* Source-to-model, source-to-version and source-to-configuration relationships.
* Five Sandero and Sandero Stepway trim records.
* Seven source-backed Eco-G 120 configuration records.
* PLN currency catalogue entry.
* Seven dated Polish catalogue gross price observations.
* Configuration-level technical observation dataset with date and source traceability.
* Thirty-five basic technical observations for seven Sandero configurations.
* Forty-nine performance, towing and weight observations.
* Thirty-five source-backed dimensional observations.
* Twenty-one cargo-capacity and tyre-repair-kit observations.
* Optional observation-level `fuel_type_code` context referencing the fuel-type dictionary.
* Twenty-eight dated WLTP fuel-consumption and CO2-emission observations.
* Separate LPG and petrol context for fuel-dependent observations.
* One hundred sixty-eight source-backed technical observations in total.
* Architecture decision D-014 for observation-level fuel context.
* Architecture decision D-015 for configuration-level equipment availability.
* Architecture decision D-016 for configuration-level wheel and upholstery values.
* Architecture decision D-017 for evidence-gated commercial packages and options.
* Architecture decision D-018 for axle-neutral standard tyre specifications.
* Explicit separation of wheel size, material, commercial design and finish.
* Conservative source-conflict policy for Stepway Essential wheel descriptions.
* Controlled dictionary for equipment availability statuses.
* Header-only `configuration_attribute_availability.csv` relation implementing D-015.
* Four cross-file references for configuration-level equipment availability.
* Regression coverage for the equipment availability schema and SQLite discovery.
* Twenty-five canonical boolean attributes for functional equipment.
* Three hundred source-backed equipment availability observations for seven Sandero configurations.
* Source-page and original-wording provenance for every imported equipment observation.
* Regression coverage for equipment counts, statuses, uniqueness and configuration differences.
* Seventeen canonical boolean attributes for explicit passive-safety equipment.
* One hundred nineteen source-backed passive-safety observations across seven configurations.
* Regression coverage for passive-safety counts, source wording, statuses and package boundaries.
* Two canonical string attributes for wheel design and upholstery variant.
* Twenty-nine source-backed wheel and upholstery values across seven configurations.
* Regression coverage for normalized values, provenance, conflict boundaries and non-boolean modeling.
* Exterior attribute category and canonical `exterior_color` string attribute.
* Seven source-backed exterior-colour values for the current Sandero configurations.
* Regression coverage for source mapping, provenance, zero-price boundaries and non-boolean colour modeling.
* Canonical `standard_tyre_specification` string attribute in the `Wheels` category.
* Seven source-backed standard-tyre-specification values for the current Sandero configurations.
* Regression coverage for source mapping, provenance, axle-neutral semantics, rating boundaries and separation from rim size.
* Seven source-backed number-of-doors values for the current Sandero configurations.
* Regression coverage for source mapping, provenance, total-versus-side-door semantics and package boundaries.
* Controlled `euro_6e_bis` emission-standard dictionary value.
* Regression coverage for exact emission-standard variants and the model/import boundary.
* Seven source-backed `Euro 6e BIS` emission-standard values for the current Sandero configurations.
* Regression coverage for source mapping, exact enum semantics, provenance and package boundaries.
* Acoustics attribute category, `dB` unit and canonical `noise_level_at_50_kmh` decimal attribute.
* Regression coverage for speed-specific noise semantics and the model/import boundary.
* Seven source-backed 50 km/h noise-level values for the current Sandero configurations.
* Regression coverage for source mapping, exact speed semantics, provenance and package boundaries.
* Seven source-backed front-wheel-drive values for the current Sandero configurations.
* Regression coverage for controlled drive-type semantics, source mapping, provenance and duplicate-string boundaries.
* Canonical `maximum_payload` integer attribute in the existing `Weights` category using the existing `kg` unit.
* Regression coverage for source-stated payload semantics, mass-concept boundaries and the model/import split.
* Seven source-backed maximum-payload values for the current Sandero configurations.
* Regression coverage for exact payload values, source mapping, provenance, mass boundaries and package isolation.
* Versioned declarative JSON specifications and a repository-owned importer for planning, atomic application and exact verification of configuration values.
* Shared contract tests for all declarative import specifications, registered source mappings, SHA-256 hashes and identifier uniqueness.
* Twenty-eight source-backed engine-power and engine-torque values with separate petrol and LPG context.
* Architecture decision D-022 and the canonical integer `total_valve_count` attribute for source-stated total engine valves.
* Seven source-backed `total_valve_count = 12` values with empty fuel context and exact page-6 provenance.
* Fourteen source-backed `acceleration_0_100` values with separate LPG and petrol context and exact page-5 provenance.
* Versioned resolution planning for 69 active configuration-gap decisions after the evidence-backed import.
* One source-backed `wheel_design = ERALIA` value imported as ID 310 through the eleventh declarative specification without a model change.
* Explicit closure of 44 `not_stated` and 25 `out_of_scope` decisions with zero remaining candidates, zero planned rows and automatic import disabled.
* Versioned source-page review rules for all 44 active evidence-review targets.
* SHA-256-verified review of 19 relevant source pages across seven registered PDFs.
* Active source-page results: 0 `found`, 44 `not_stated`, 0 `ambiguous`, 25 unchanged `out_of_scope` decisions and zero candidate values.
* Versioned configuration-gap evidence decisions matched one-to-one with the 69-entry triage queue.
* Conservative classifications that do not convert absent source statements into negative data.
* Resolution planning routes the next package to the configuration-gap closure documentation milestone.
* Deterministic, non-prioritized verification queue for configuration gaps.
* One-to-one consistency checks between completeness and source-coverage gaps.
* Source-verification tasks retaining document dates, paths and SHA-256 hashes with automatic import disabled.
* Deterministic source-registration, area, section and record coverage reports.
* Source metadata verification retaining document dates, paths and SHA-256 hashes.
* Separate `source_missing` and `record_missing` states for source-backed gaps.
* Explicit, versioned denominator specification for configuration-data completeness.
* Deterministic JSON and Markdown completeness reports grouped by configuration, category and source.
* Deterministic JSON and Markdown configuration comparison reports for all 21 active configuration pairs.
* Separate price, technical-value and equipment-availability comparison domains.
* Explicit `not_comparable` handling for missing, `not_stated`, `out_of_scope`, `ambiguous` and `not_applicable` states.
* Pair classification for version and transmission comparisons while preserving source-backed `not_available` differences.
* Optional deterministic configuration-comparison filtering by existing version/transmission pair type.
* Filtered reports recalculate selected pairs, selected configurations and all domain summaries while keeping the unfiltered 21-pair report as the default.
* Deterministic flat CSV export containing only actual configuration differences.
* Difference rows retain pair metadata, domain context, both recorded values, dates and source codes.
* Optional deterministic filtering of the flat difference CSV by price, technical or equipment domain.
* Difference-domain filtering composes with pair-type filtering while leaving JSON, Markdown and the full CSV unchanged by default.
* Optional exact item-code filtering for the flat configuration-difference CSV.
* Item-code validation uses the full active comparison report before pair and domain filtering.
* Separate reporting for missing records, `unknown`, `not_available` and declared `not_applicable` slots.
* Deterministic `documentation-baseline` command for current project counters.
* Machine-readable JSON and human-readable Markdown baseline reports.
* Managed documentation blocks for README, changelog, roadmap and session state.
* Fourteen source-backed `standing_km` values with separate LPG and petrol context and exact page-5 provenance.
* Regression coverage for the optional fuel-context relationship.
* Cross-file reference and status rules for the new source-backed data tables.

### Changed

* The unified CLI now propagates command exit codes.
* Repetitive Git package checks are consolidated into three CLI commands while commit, push and merge remain explicit operations.
* Package review and finish commands accept a versioned JSON manifest with exact branch, base SHA, commit subject and path scope.
* Package finish enforces one commit, its exact parent and an exact committed-file manifest when a package manifest is supplied.
* Git path discovery uses byte-exact NUL output while human-readable Git output is decoded deterministically as UTF-8.
* Line-ending policy is declared in `.gitattributes`, and CI runs package workflow tests on Windows.
* Full quality now generates and publishes both configuration-gap-resolution-plan report formats.
* Full quality now generates and publishes configuration-comparison JSON, Markdown and difference-CSV formats.
* Configuration comparison preserves the global evidence summary when pair filtering narrows the displayed comparisons.
* Difference-domain filtering affects only the flat CSV export and does not narrow report summaries or evidence scope.
* Difference item filtering affects only flat CSV rows; known codes may yield header-only output after other filters.
* Full quality now verifies and publishes both configuration-gap-source-review report formats.
* Full quality now generates and publishes both configuration-gap-evidence report formats.
* Full quality now generates and publishes both configuration-gap-triage report formats.
* Full quality now generates and publishes both source-coverage report formats.
* Full quality now generates and publishes both configuration-completeness report formats.
* Full quality now verifies documentation counters against the built SQLite database and publishes both baseline report formats.
* Successful quality output is concise while complete verbose output remains available in a file and failures replay names and tracebacks.
* Python 3.10 keeps compile-and-test compatibility coverage, while Python 3.13 owns full data, SQLite and artifact validation.
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
* Cross-file validation now covers 34 declared relationships.
* Lifecycle and catalogue status validation now covers 19 declared rules.
<!-- dkb:documentation-baseline:changelog:start -->
* The automated test suite now contains 610 tests.
* The verified master-data baseline now contains 37 CSV files and 5155 rows.
* SQLite verification now covers 37 tables and 5155 rows.
* Configuration attribute values now contain 1204 dated records.
* Declarative scalar configuration-value imports now contain 71 versioned JSON specifications.
* Configuration value ranges now contain 144 dated records from 19 range specifications.
* The canonical catalogue now contains 357 attributes in 30 categories.
* Equipment availability now contains 2977 records: 2401 `standard`, 196 `optional`, 380 `not_available` and 0 `unknown`.
<!-- dkb:documentation-baseline:changelog:end -->

### Fixed

* Local quality subprocesses force UTF-8 output on Windows consoles and redirected logs.
* Package workflow Git commands no longer depend on the Windows console code page when displaying Polish paths and diff content.
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
* Synchronized project documentation with the dimensions and cargo-capacity packages merged through PRs #11 and #12.
* Synchronized project documentation after PRs #13 and #14, recorded merge commit `6224875` and closed the Fuel-mode-aware WLTP Observation Analysis package.
* Analyzed coverage of all seven registered Sandero and Sandero Stepway PDF sources.
* Identified configuration-level equipment availability as the next model gap and separated schema implementation from source-data import.
* Documented the implemented equipment availability schema and the separate source-import follow-up package.
* Documented the first functional equipment import and its conservative source-mapping boundary.
* Documented the passive-safety import and deferred wheel and upholstery value modeling.
* Documented the wheel and upholstery value model without importing ambiguous source records.
* Documented the controlled wheel and upholstery value import and the preserved Stepway Essential conflict boundary.
* Analyzed all seven current sources for commercial packages and options and deferred schema work because no named offer records are present.
* Imported `biel alpejska` as a dated exterior-colour value for all seven current configurations while retaining `0 zł` only as source provenance.
* Analyzed the remaining explicit PDF values and selected the axle-neutral standard tyre specification as the next controlled import.
* Imported `205/60 R16 92H` as an axle-neutral dated standard-tyre specification for all seven current configurations.
* Reassessed the remaining explicit Sandero PDF value gaps, rejected already-modeled and non-data candidates, and selected `number_of_doors` for the next controlled import.
* Imported `number_of_doors = 5` as a dated value for all seven current configurations using the existing integer attribute.
* Modeled exact `Euro 6e BIS` semantics as a distinct controlled value and deferred configuration records to a separate import.
* Imported `emission_standard = euro_6e_bis` as a dated value for all seven current configurations.
* Modeled the page-6 50 km/h noise field as a speed-specific `dB` measurement and deferred configuration records to a separate import.
* Imported `noise_level_at_50_kmh = 67` as a dated value for all seven current configurations.
* Reviewed the remaining Sandero technical-value candidates, rejected already-modeled and non-data matches, and selected `drive_type = fwd` for the next controlled import.
* Imported `drive_type = fwd` as a dated value for all seven current configurations using the existing controlled enum.
* Modeled the explicit page-5 maximum-payload field as an independent integer `kg` observation under decision D-021 and deferred configuration records to a separate import.
* Synchronized the documentation milestone after PRs #39–#42.
* Documented declarative configuration-value imports, the petrol/LPG engine-output observations, decision D-022 and the total-valve-count import.
* Imported and documented separate LPG and petrol `acceleration_0_100` observations for all seven current configurations.
* Imported and documented separate LPG and petrol `standing_km` observations for all seven current configurations.
* Reassessed 43 remaining technical-value groups after 309 observations and found no additional group satisfying the complete import contract.
* Documented relevant-page extraction, direct-match evidence and the remaining ambiguity boundary.
* Documented structured-evidence scope, unresolved PDF-page review and the zero-candidate-import result.
* Documented neutral triage ordering, source-verification states and the no-auto-import boundary.
* Documented source registration, section coverage and source-backed gap semantics.
* Documented the explicit configuration-completeness denominator and non-guessing gap semantics.
* Added generated baseline counters and drift-checked current documentation summaries.
* Synchronized README, changelog, roadmap and session state after PRs #44–#45 and closed the current explicit technical-value sweep.
* Planned and imported the source-backed Stepway Essential `wheel_design = ERALIA` value as ID 310 through PRs #53–#54.
* Closed the active configuration-gap cycle at 69 decisions: 44 `not_stated`, 25 `out_of_scope`, zero candidates, zero planned rows and automatic import disabled.
* Synchronized README, changelog, roadmap and session state after PRs #53–#54 and selected a configuration comparison report as the next reporting package.
* Added and documented deterministic configuration comparison as the next reporting capability.
* Reviewed the 21-pair comparison snapshot and selected same-version transmission filtering as the highest-signal follow-up.
* Documented the flat comparison-difference CSV contract and its compatibility with pair-type filtering.
* Reviewed the 305-row difference export and selected domain filtering over configuration filtering as the next reporting package.
* Reviewed the three domain exports and selected exact item-code filtering over configuration filtering.
