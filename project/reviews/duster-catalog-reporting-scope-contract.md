# Duster Catalog Reporting Scope Contract

## Decision

Option A from the Duster catalogue architecture boundary is accepted.

Source-backed catalogue entities keep the existing `active` status. Reporting tools no longer infer that every active configuration must immediately enter the completeness, source-coverage and comparison denominators.

## Declarative contract

`data/reporting/configuration_completeness.json` now requires `configuration_scope` with the value `explicit_subset`.

The `configurations` array is the complete reporting subset for the declared `configuration_status`. Every selected configuration must exist and have that status, but other configurations with the same status may remain outside the report.

## Shared validation

`tools/configuration_reporting_scope.py` centralizes the contract for configuration completeness, source coverage, configuration comparison and derivative artifacts.

The validator rejects missing scope mode, empty mappings, duplicate mappings, missing configurations and selected configurations with a different status. It does not silently select newly added active configurations.

## Disclosure

Generated JSON and Markdown reports disclose the reporting scope mode, the reporting-configuration count, the repository count for the selected status, and the count and codes excluded from the reporting subset.

Existing compatibility fields remain available, and the seven-configuration Sandero denominator, 21 comparison pairs and existing gap semantics remain unchanged by default.

## Duster consequence

The Duster Catalog Bootstrap may now create active source-backed versions and configurations without fabricating technical values, equipment availability or completeness exceptions. Until a later evidence-backed package extends the reporting specification, those Duster configurations remain visible in master data and explicitly disclosed as excluded from Sandero reporting outputs.

## Evidence boundary

This contract does not create Duster versions or configurations, import prices or observations, introduce a second catalogue lifecycle status, weaken validation, or automatically add configurations to reports based only on active status.

## Acceptance criteria

All three reporting entry points use one shared scope resolver; selected configurations outside the declared status are rejected; active configurations outside the explicit subset are accepted and disclosed; the established 410-test count remains unchanged; full Quality and Windows checks pass; canonical state resumes at Duster Catalog Bootstrap.
