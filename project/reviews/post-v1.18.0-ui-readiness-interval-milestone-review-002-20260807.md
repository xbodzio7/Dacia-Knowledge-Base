# Post-v1.18.0 UI Readiness Interval Milestone Review 002

Date: 2026-08-07  
Base commit: `b2b95cc2db67bec641d0a1a9e84c90ab87902b0e`  
Package ID: `post_v1_18_ui_readiness_interval_milestone_review_002`

## Decision status

`COMPLETE`

The required five-package interval after milestone review PR #593 is complete. The interval preserved the New Spring evidence queue while materially advancing the source-bounded data contract needed for a Dacia-configurator-like interface.

## Reviewed package interval

| PR | Package | Result | Persistent boundary |
| --- | --- | --- | --- |
| #594 | `new_spring_confirmed_card_price_capture_001` | 16 confirmed Dacia Shop cards revisited; 2 new catalogue prices captured; repository-wide exact current-price matches increased to 14; 14 confirmed cards still lack captured price | exact part number and official Polish Dacia Shop only; 28 unresolved cards not retried before date gate |
| #595 | `configurator_ui_appearance_data_001` | six current default model surfaces normalized into exact UI-facing colour/wheel/upholstery choice data; official model-packshot layer retained | no projection across grade, powertrain, transmission, drive, seat count or phase; `CAT-GAP-002` remains open |
| #596 | `configurator_ui_grade_appearance_coverage_001` | all 21 current grade surfaces receive representative exact selected appearance; 14 grade pages expose explicit appearance facts; two complete visible grade-design surfaces recorded | representative exact appearance is not grade-wide proof; incomplete lists remain incomplete |
| #597 | `jogger_essential_7seat_exact_appearance_capture_001` | exact-complete appearance coverage increased from 6 to 7 of 81 active configuration surfaces using direct seven-seat evidence | no transfer from five-seat Jogger; special-offer vehicle price not promoted to catalogue price |
| #599 | `bigster_essential_grade_design_completion_001` | complete visible grade-level Design coverage increased from 2 to 3 of 21 grade surfaces | grade-level choice list does not authorize transfer of exact LPG-state prices to mild hybrid 140 |

## Verified closure state

The verified master baseline remains unchanged across the five-package interval:

- 1885 automated tests;
- 47 master CSV files;
- 11770 master rows;
- 3604 configuration values;
- 316 configuration value ranges;
- 5911 availability records;
- 387 canonical attributes in 30 categories.

No package in this interval changed `data/master`.

### New Spring Shop

Repository-wide New Spring Shop status after #594 remains:

- 56 exact price-list references;
- 28 confirmed official Polish Dacia Shop cards;
- 14 exact current-price matches;
- 14 confirmed cards without a captured catalogue price;
- 28 unresolved cards;
- 0 price mismatches.

The 28 unresolved exact references remain gated for the next homogeneous retry no earlier than 2026-08-08 unless new direct evidence appears first.

### Configurator appearance readiness

The interval establishes a usable bounded appearance contract rather than a fabricated portfolio-wide catalogue:

- six current model-family default configurator states have complete visible exact current appearance choices;
- a dedicated seven-seat Jogger state raises strict exact-complete coverage to 7 of 81 active configuration surfaces;
- all 21 current grade surfaces have a representative exact selected wheel and upholstery observation;
- 14 of 21 grade pages expose at least one current explicit appearance fact in the captured grade layer;
- complete visible grade-level Design lists are recorded for Sandero Journey, Bigster Expression and Bigster Essential;
- model-level official packshots remain separate from exact paint/wheel renders.

`CAT-GAP-002` remains open with 74 active configuration surfaces still lacking a complete exact-current appearance panel under the strict acceptance rule.

## UI readiness decision

The data architecture is now sufficient to begin implementing the configurator-style interface **without waiting for all 81 exact appearance surfaces**, provided the UI obeys the readiness/scope contract:

1. exact selectors are enabled only for scopes with complete exact evidence;
2. complete grade-level Design lists are shown only at their proven grade scope;
3. selected-only observations are rendered as selected/default context, not as full alternative lists;
4. missing choices are never interpreted as unavailable;
5. model packshots are not presented as exact colour/wheel renders;
6. price overlays never cross their configuration or powertrain boundary.

This removes data completeness as a blocker for the interface shell and progressive enhancement. It does **not** close the evidence gaps required for a fully faithful portfolio-wide configurator.

## Commercial-choice readiness

The existing master already contains a substantial packages/options layer, but the interface still needs an explicit contract distinguishing selector offers, selected-state observations, unknown prices and unsupported multi-choice compatibility.

A prepared bounded package already exists as PR #598: `configurator_ui_commercial_choice_readiness_001`.

It is the highest-value next package because it directly completes the semantic bridge between existing master commercial data and the planned packages/options UI step, while requiring no inferred source facts or master mutation.

The remaining commercial limitation after that package is expected to be generic multi-option dependency/conflict/orderability evidence. A dependency graph must not be invented merely to make the UI behave like the public configurator.

## Workflow review

The accelerated package cadence is working as intended:

- the 16-card Spring price capture was handled as one homogeneous package;
- UI-readiness evidence was split into bounded logical packages rather than one speculative master-data rewrite;
- final quality gates caught and prevented publication of malformed reporting data before merge;
- concurrent `main` advancement was handled by rebasing/reconstructing package commits against the current repository state.

The main remaining workflow inefficiency is CI trigger scope. Reporting-only changes continue to start many specialized model/report workflows unrelated to the changed paths. `Quality` should remain universal; dependency-specific `paths` filters for specialized workflows remain a justified future optimization package after the current UI-readiness work is stabilized.

No second generic orchestration framework is justified.

## Options considered

| Option | Value | Boundary assessment | Decision |
| --- | --- | --- | --- |
| Complete `configurator_ui_commercial_choice_readiness_001` (PR #598) | High: directly enables source-bounded packages/options UI from existing master evidence | no new source inference; reporting/integration only | **Select next** |
| Retry 28 unresolved New Spring Shop refs on 2026-08-07 | Low today | violates the explicit `eligible_on_or_after: 2026-08-08` gate absent new direct evidence | Defer |
| Continue exact appearance capture immediately | High long-term, but not required to begin UI shell | `CAT-GAP-002` remains strict; capture only direct reproducible states | Continue after the selected commercial package / when it is the highest-priority unblocked work |
| Build a generic option dependency/conflict graph now | Premature | current master does not prove generic pairwise rules | Defer until direct evidence supports rules |
| Start a broad UI rewrite before commercial-choice semantics are normalized | Avoidable rework | package/options step would need ad-hoc interpretation | Defer until PR #598 is integrated |
| Optimize specialized CI trigger scopes | Useful engineering acceleration | unrelated to domain evidence and should be a separate tooling package | Candidate after current UI-readiness sequence |

## Next bounded package

`configurator_ui_commercial_choice_readiness_001`

The package is already prepared in PR #598 and must be rebased onto the milestone-review merge before final validation and merge.

Acceptance boundary:

- selector offers come only from explicit mapped `optional` commercial-item rows;
- exact selected-state observations remain distinct from offer availability;
- blank amount remains unknown/not stated, never zero;
- package contents come from source-backed commercial-item attribute memberships;
- no commercial choice is transferred across configuration identity boundaries;
- no arbitrary simultaneous option/package combination is claimed orderable without direct evidence or an explicit rule;
- no master-data mutation;
- full quality gate on the final rebased head.

## Subsequent queue

After the commercial-choice package:

- `new_spring_current_shop_retry_cycle_002` remains the canonical evidence queue once the 2026-08-08 date gate is satisfied;
- while that queue remains time-gated, direct exact-appearance closure work may proceed when it is the highest-priority unblocked package;
- the first actual configurator UI implementation package may begin once the commercial-choice contract is merged, using graceful fallback for incomplete appearance scopes rather than waiting for `CAT-GAP-002` to reach 81/81.

## Automation conclusion

Continue using the existing autonomous package workflow. The next meaningful tooling optimization is specialized CI trigger scoping, not a new orchestration layer. Domain gaps should continue to be closed by direct evidence and explicit readiness metadata rather than inference.
