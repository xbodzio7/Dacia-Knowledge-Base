# Post-v1.14.0 Release Priority Selection Review

Date: 2026-08-03

Package ID: `post_v1_14_0_release_priority_selection_review_001`

Status: **complete**

## Canonical evidence reviewed

- immutable `data-products-v1.14.0` publication receipt, exact source SHA, double-build identity and successful public-download verification;
- `existing_configuration_missing_data_analysis.json`, which still records seven exhausted candidates and zero eligible source-backed candidates;
- the completed public family summary, family comparison matrix and 22-row model-version comparison matrix;
- 33 explicit provenance sources and 251 source-to-configuration relationships already verified across all 81 active configurations;
- the roadmap requirement for transparent, stable external products beyond current configuration surfaces.

## Finding

No source-backed import can be selected from currently registered evidence without reopening an exhausted candidate, expanding source scope or inferring a missing value.

The public family and version products expose provenance counts and date ranges, but they do not provide a dedicated consumer-facing view of each registered source and its exact coverage. The repository already contains the bounded relationships needed to project one row per source without changing source or master data.

## Selection

The next package is **Portfolio Source Coverage Matrix** — `portfolio_source_coverage_matrix_001`.

It will create deterministic JSON, CSV and standalone HTML outputs with one row per active source represented by current active configuration provenance. Each row will preserve the exact source identity, document metadata, covered model families, versions, configurations and relationship count.

## Acceptance boundary

The selected package must:

- include exactly the 33 provenance sources used by the 81 active configurations;
- preserve all 251 explicit source-to-configuration relationships exactly once;
- preserve exact source codes, document dates, source types, titles, URLs or registered local identities and SHA-256 values where recorded;
- derive covered model-family, version and configuration lists only from canonical relationships;
- retain source status and recorded metadata without assigning quality, authority or preference scores;
- produce deterministic JSON, CSV and standalone HTML;
- perform no source-data, master-data, schema, model or architecture mutation;
- create no configuration pair, cross-scope pair, ranking, recommendation or inferred value.

## Rejected alternatives

- **Source-backed import:** rejected because the eligible candidate count remains zero.
- **Another family or version matrix:** rejected because v1.14.0 already exposes those levels directly.
- **Source quality ranking:** rejected because authority or quality scoring is not represented canonically and would require inference.
- **New source or domain expansion:** rejected because it requires separate evidence intake or an architecture decision.
