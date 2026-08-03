# Post-v1.13.0 Release Priority Selection Review

Date: 2026-08-03

Package ID: `post_v1_13_0_release_priority_selection_review_001`

Status: **complete**

## Canonical evidence reviewed

- immutable `data-products-v1.13.0` publication receipt, exact source SHA, double-build identity and successful public-download verification;
- `existing_configuration_missing_data_analysis.json`, which records seven exhausted candidates and zero eligible source-backed candidates;
- 22 active canonical versions in `data/master/versions.csv` across the six current model families;
- the completed public family summary and family comparison matrix, which aggregate 81 active configurations to six family rows;
- the roadmap requirements to compare models and versions beyond current configuration surfaces and provide further stable external formats.

## Finding

No source-backed import can be selected from the currently registered evidence without reopening an exhausted candidate, expanding source scope or inferring a missing value.

The new public family matrix solves family-level comparison, but version/trim comparison remains available only indirectly through individual configurations and scopes. The canonical version registry already defines 22 active version rows, and every active configuration is assigned to one of them. This creates a bounded reporting opportunity without data mutation.

## Selection

The next package is **Portfolio Model Version Comparison Matrix** — `portfolio_model_version_comparison_matrix_001`.

It will create deterministic JSON, CSV and standalone HTML outputs with one row per active canonical version. Rows will project only recorded canonical identifiers and version-bounded aggregates from existing configurations, prices, seat states, transmissions, powertrain labels, reporting-scope membership and explicit source provenance.

## Acceptance boundary

The selected package must:

- include exactly the 22 active canonical versions and all 81 active configurations;
- preserve exact model and version codes and names;
- derive configuration counts, recorded price ranges, seat states, transmissions and powertrain labels only from existing canonical records;
- preserve existing reporting-scope membership and explicit source-to-configuration provenance without creating new pairs;
- retain `not_stated` wherever a version has no recorded value;
- produce deterministic JSON, CSV and standalone HTML;
- perform no source-data, master-data, schema, model or architecture mutation;
- create no configuration pair, cross-scope pair, ranking, recommendation or inferred value.

## Rejected alternatives

- **Source-backed import:** rejected because the eligible candidate count remains zero.
- **Another family-level product:** rejected because v1.13.0 already exposes the family summary and comparison matrix directly.
- **Cross-version ranking or recommendation:** rejected because the current model supports comparison, not preference inference.
- **New source or domain expansion:** rejected because it requires a separate evidence-intake or architecture decision.
