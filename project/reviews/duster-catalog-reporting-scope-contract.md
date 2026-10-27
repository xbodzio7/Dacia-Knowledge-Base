# Duster Catalog Reporting Scope Contract

## Decision

Option A from the Duster catalogue architecture boundary is accepted.

Source-backed catalogue entities keep the existing `active` status. Reporting tools no longer infer that every active configuration must immediately enter the completeness, source-coverage and comparison denominators.

## Declarative contract

The `configurations` array in the version-1 completeness specification is the explicit reporting subset for the declared `configuration_status`. Existing version-1 specifications that omit `configuration_scope` resolve to `explicit_subset` for compatibility; an explicit value is accepted, and any other value is rejected.

Every selected configuration must exist and have the declared status. Other configurations with that status may remain outside the report.

## Shared validation

`tools/reporting/configuration_scope.py` validates the selected mappings. `tools/reporting/configuration_scope_runtime.py` provides the compatibility adapter and common disclosure fields used by completeness, source coverage and comparison.

The resolver rejects empty or duplicate mappings, missing configurations and selected configurations with a different status. It never silently selects newly added active configurations.

## Disclosure

Generated JSON and Markdown disclose the scope mode, reporting count and codes, repository-wide count for the selected status, and excluded count and codes. Existing compatibility fields remain available.

The seven-configuration Sandero denominator, 21 comparison pairs and 305 difference rows remain unchanged by default.

## Duster consequence

The Duster Catalog Bootstrap may create active, source-backed versions and configurations without fabricating technical values, equipment availability or completeness exceptions. Until a later evidence-backed package extends the reporting specification, those Duster configurations remain visible in master data and are explicitly disclosed as excluded from Sandero reports.

## Evidence boundary

This contract does not create Duster catalogue entities, import observations or prices, introduce another lifecycle status, weaken validation, or auto-enrol configurations based only on `active` status.

## Acceptance criteria

- all three reporting entry points use the shared scope contract;
- active configurations outside the subset are accepted and disclosed;
- invalid selected mappings remain rejected;
- the established 410-test count remains unchanged;
- full Quality and Windows checks pass;
- canonical state resumes at Duster Catalog Bootstrap.
