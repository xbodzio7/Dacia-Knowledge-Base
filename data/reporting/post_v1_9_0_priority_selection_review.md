# Post-v1.9.0 Priority Selection Review

Date: 2026-07-31

Status: **complete**

## Trigger

The immutable `data-products-v1.9.0` release and its independent public audit are complete. PR #414 recorded the durable publication identity and passed Quality run #2726. No other Pull Request was open when this review began.

## Current product state

The public workspace contains:

- 78 active configurations;
- 20 independent reporting scopes;
- 129 within-scope pairs;
- 2,180 recorded differences;
- 89 deterministic archive members;
- 88 local links in the workspace index;
- 80 cross-model comparison paths;
- two cross-model navigation paths;
- 60 local links in the cross-model HTML.

The release preserves all scope, non-ranking, non-recommendation and non-inference boundaries.

## Candidates considered

### Cross-Model Navigation Usability Review — selected

This review was explicitly deferred after `data-products-v1.8.1`. It asks whether consumers can discover the published cross-model products from the deterministic workspace index and whether a dedicated entry point is justified.

It is the highest-readiness package because:

- the public product and audit already exist;
- v1.9.0 increased the product to 78 configurations and 20 scopes;
- the roadmap explicitly prioritizes report usability without changing data semantics;
- the package can remain review-only and produce one bounded implementation recommendation.

### Verified PDF residual continuation — deferred

The completed release sequence must not reopen closed residual boundaries. No new registered source or evidence decision was identified that would make another residual package import-ready.

### Additional model or source expansion — deferred

Spring and further model expansion remain valid strategic directions, but the next bounded package first requires an explicit source-selection and intake decision.

### Immediate data-products release — deferred

No post-v1.9.0 data delta, confirmed interface defect or completed implementation package currently justifies another immutable release.

## Selected next package

**Cross-Model Navigation Usability Review**

Goal: review consumer discoverability of the published cross-model products and deterministic offline workspace, determine whether the workspace index needs a dedicated cross-model entry point, and define the smallest testable implementation package without changing comparison semantics.

The review will answer:

1. Can a consumer discover the cross-model view directly from the workspace index?
2. Can model families and reporting scopes be reached without knowing generated paths?
3. Do labels and provenance explain the scope-preserving boundary clearly?
4. What is the smallest implementation package that improves discoverability?

## Boundary

This package will not modify source data, master data, reporting scopes, generated comparisons, public v1.9.0 assets or interface code. It will not generate cross-scope pairs, ranking, recommendations or inferred values.

Decision: `SELECT_CROSS_MODEL_NAVIGATION_USABILITY_REVIEW`.
