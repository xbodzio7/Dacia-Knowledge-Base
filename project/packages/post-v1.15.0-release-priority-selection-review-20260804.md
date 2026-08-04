# Post-v1.15.0 Release Priority Selection Review

## Package

- Package ID: `post_v1_15_0_release_priority_selection_review_001`
- Kind: `priority_selection_review`
- Date: 2026-08-04
- Status: complete

## Purpose

Select exactly one bounded package after publication of `data-products-v1.15.0`, using only canonical repository evidence and without reopening completed release work, inferring missing domain facts or introducing a new architectural direction.

## Evidence reviewed

- `project/state.json` confirms that v1.15.0 publication is complete and explicitly schedules this priority-selection review.
- `data/reporting/verified_pdf_candidate_residual_review_closure.json` proves that all 52 residual-review packages and all 1,266 candidate assignments are complete; the stale Duster continuation note is not an active queue item.
- The public portfolio products now provide family summary, family comparison, model-version comparison and source-coverage surfaces for six families, 22 active versions, 81 configurations, 33 provenance sources and 251 explicit source relationships.
- `project/ROADMAP.md` calls for further deterministic comparisons and useful external formats while preserving source-backed semantics and non-inference.
- The repository has no open Pull Request competing for the next package.

## Selection

The next package is:

- Package ID: `portfolio_powertrain_transmission_matrix_001`
- Kind: `reporting_product`
- Name: `Portfolio Powertrain and Transmission Matrix`
- Boundary: a deterministic JSON, CSV and standalone HTML projection of active configurations grouped by exact recorded powertrain and transmission identities, retaining model-family, version, price and provenance coverage without creating configuration pairs.

## Rationale

This package is the highest-priority unblocked continuation because it:

1. adds a missing consumer comparison axis after family, version and source views;
2. uses only existing active configuration, powertrain, transmission, price and provenance relationships;
3. can represent all 81 active configurations without changing master data or schema;
4. supports practical LPG/manual/automatic comparison across model families without ranking or recommending configurations;
5. is bounded, deterministic and suitable for later release integration as a separate package.

## Explicit non-selections

The review does not select:

- another residual PDF package, because the canonical 52-package queue is complete;
- another v1.15.0 release-integration or publication repair, because publication is complete;
- a new model-family or source intake, because no eligible source-backed candidate currently establishes that priority;
- ranking, recommendation or preferred drivetrain logic;
- inferred powertrain, transmission, price or equipment values.

## Acceptance criteria

This review is complete when:

- the selected package is recorded in `project/state.json` as the sole planned next package;
- generated state documentation reflects the selection;
- no domain data, release asset or architecture file is modified;
- the final head passes project-state validation, the residual-queue completion contract and the complete required CI matrix.

## Result

The post-v1.15.0 priority-selection review is complete. Work may continue with `portfolio_powertrain_transmission_matrix_001` as a standalone reporting product before any release integration decision.
