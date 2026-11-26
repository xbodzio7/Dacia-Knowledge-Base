# Post-v1.12.1 Release Priority Selection Review

Date: 2026-08-03

Package ID: `post_v1_12_1_release_priority_selection_review_001`

Status: **complete**

## Canonical evidence reviewed

- immutable `data-products-v1.12.1` publication receipt, exact source SHA and successful public-download verification;
- `existing_configuration_missing_data_analysis.json`, which still records seven exhausted source-backed candidates and zero eligible candidates;
- the completed portfolio model-family summary covering six families, 81 active configurations, 22 reporting scopes and explicit provenance for every configuration;
- the direct model-family workspace entry point and dedicated offline card delivered in `v1.12.1`;
- the roadmap requirements to select the highest-value next reporting package, extend model/version comparison beyond current configuration surfaces and provide stable external formats.

## Finding

No source-backed import can be selected from the current registered evidence without reopening an exhausted candidate, introducing a new source scope or inferring a missing value.

The current family product provides a detailed summary and one overview table, but the repository does not yet expose a dedicated consumer-facing model-family comparison matrix as an independent deterministic product. The existing family records already contain the bounded facts needed for such a matrix: configuration and version counts, recorded price ranges, seat states, transmissions, powertrain labels, reporting-scope coverage and provenance coverage.

## Selection

The next package is **Portfolio Model Family Comparison Matrix** — `portfolio_model_family_comparison_matrix_001`.

It will create deterministic JSON, CSV and standalone HTML comparison outputs for the six current model families by projecting only fields already present in the verified portfolio model-family summary. The product will compare family-level recorded states side by side and preserve `not_stated` where evidence is absent.

## Acceptance boundary

The selected package must:

- reuse the six canonical model families and all 81 active configurations already represented by the family summary;
- derive its rows only from the verified family-summary product and canonical identifiers;
- preserve exact recorded price ranges, seat states, transmissions, powertrain labels, reporting-scope counts and provenance coverage;
- produce no new configuration pair, cross-scope pair, ranking, recommendation or preferred model;
- perform no source-data, master-data, schema, model or architecture mutation;
- infer no missing seat, price, equipment or technical value;
- remain deterministic and suitable for later release integration as a separate package.

## Rejected alternatives

- **Source-backed import:** rejected because the eligible candidate count remains zero.
- **Residual PDF queue restart from the narrative session note:** rejected because the referenced Duster page-21 chunks were already completed in PRs #327 and #328; narrative history cannot override current repository evidence.
- **New source or model expansion:** rejected because it requires a separate evidence intake or scope decision.
- **Cross-family ranking or recommendation:** rejected because the current model supports comparison, not preference inference.
