# Post-v1.19.0 Release Priority Selection Review 001

Date: 2026-08-08  
Base commit: `b7f8e86aa53397cc47bb4848dff73a3933c4365f`  
Package ID: `post_v1_19_0_release_priority_selection_review_001`

## Decision status

`COMPLETE`

Data Products v1.19.0 is published and its durable receipt is present on `main`. This review selects the highest-value bounded follow-up from current repository evidence rather than reopening the completed release or choosing work from historical backlog order.

The canonical discovery baseline remains 1885 tests. This review changes no master data, production code, workflow or source evidence.

## Publication checkpoint

- release tag: `data-products-v1.19.0`;
- exact release source: `c121e600de48576f2da53cba2eb42075b6632504`;
- activation Pull Request: #615, closed without merge after successful publication;
- publication workflow: `31245016492`;
- receipt commit: `b7f8e86aa53397cc47bb4848dff73a3933c4365f`;
- independent double build: verified byte-identical;
- offline workspace: verified;
- public-download verification: byte-identical;
- previous `data-products-v1.18.0` release preserved.

The release checkpoint is complete and is not a candidate for further mutation in this review.

## Priority rule

`project/ROADMAP.md` requires completeness-first, source-backed development and selection by current missing-data/user-impact rather than by backlog age. A candidate is therefore preferred only when it combines useful product impact with evidence already sufficient for a bounded package.

## Candidate assessment

| Candidate | User/data impact | Current evidence state | Decision |
| --- | --- | --- | --- |
| Expand exact appearance coverage | High | strict exact-current coverage reached 7 of 81 surfaces after PR #597, but the remaining non-default states are not reproducibly exposed by the current static retrieval path; grade-level facts must not be promoted into exact configuration palettes | Defer until new direct official state evidence is available |
| Repeat New Spring Shop unresolved retry | Low today | cycle 002 retried all 28 unresolved exact references on 2026-08-08 and produced 0 confirmations and 0 status changes | Defer; another same-day retry is not new evidence |
| Fill all five Spring selector rows currently reported without price | Medium | the five rows are not one homogeneous price gap: three are historical Type 2 brochure option mappings while exact-current canonical evidence says Type 2 is standard; only Techno and DC 40 kW remain genuine unpriced current-candidate questions, and current MY26 Expression prices are not captured | Split the semantic error from the source-blocked price questions |
| Build generic package/option dependency, conflict and orderability graph | Potentially high | repository explicitly says generic rules are not modeled and exact isolated combinations must not be generalized | Defer; would require new evidence/modeling scope |
| Optimize broad specialized CI trigger scopes | Medium operational | bounded and feasible, but lower user-facing correctness value than the Spring selector contradiction | Keep as later tooling work |
| Reconcile Spring Type 2 current selector semantics | High correctness / bounded | exact-current canonical availability already proves the supplied Type 2 cable is `standard` for Essential 70, Expression 70 and Extreme 100, while the UI offer collector still exposes the three older brochure-backed `optional` commercial mappings | **Select** |

## Spring Type 2 evidence conflict

The repository intentionally preserves two different historical/current facts:

1. the 2026-02-19 Spring brochure explicitly listed `spring_type2_charging_cable_option` as a separate option for Essential, Expression and Extreme, with no amount;
2. later exact-current evidence establishes `type2_charging_cable_supplied = standard` for all three current canonical Spring configurations:
   - Essential electric 70 — exact current configurator observation dated 2026-07-31;
   - Expression electric 70 — exact saved official configuration `7OO7LQ` dated 2026-08-02;
   - Extreme electric 100 — exact saved official configuration `WKAWYV` dated 2026-08-02.

PR #461 correctly materialized those three exact-current standard equipment-availability rows. PR #463 correctly preserved the three older brochure-backed commercial mappings as historical observations while fixing the commercial-item membership to `type2_charging_cable_supplied`.

The conflict now exists only in the user-facing current-offer interpretation. `tools/reporting/commercial_offers.py` treats an eligible historical `optional` commercial mapping as a selector offer and does not reconcile it against the later canonical `configuration_attribute_availability` standard state. Consequently, the v1.19.0 commercial-readiness layer counts the three Type 2 rows among five Spring offers with unknown price even though the current exact evidence does not describe Type 2 as a paid/unknown-price option for any of the three current Spring configurations.

This is different from the accepted Duster pattern where a later commercial `standard` row means that a separately priced package was selected on one exact stock vehicle. The Spring Type 2 facts are canonical factory-equipment availability records, not selected-package observations.

## Genuine remaining Spring price questions

After isolating the three Type 2 historical mappings, the two remaining unpriced Spring commercial questions are:

- `spring_techno_package` for Expression electric 70;
- `spring_dc40_charging_option` for Expression electric 70.

The registered MY2025 stock price list contains historical/contextual amounts for those items, but repository policy explicitly forbids transferring those prices to the current MY26 Expression mapping without an exact current source. They therefore remain source-blocked and are not candidates for inferred price filling.

## Selected next package

`spring_type2_current_selector_reconciliation_001`

Name: **Spring Type 2 Current Selector Reconciliation**.

The package should reconcile the current UI/reporting offer view so the three preserved historical brochure-backed Type 2 `optional` mappings are not presented as current selectable Spring offers when the same exact canonical configurations have later source-backed `type2_charging_cable_supplied = standard` availability.

The package must:

- preserve all three historical commercial mapping rows and their February brochure provenance;
- preserve the three exact-current canonical standard-availability rows;
- change only the derived current selector/reporting interpretation needed to remove the contradiction;
- leave the separate domestic-socket cable option unchanged;
- leave Expression Techno and DC 40 kW prices unknown unless new exact-current evidence is introduced by a separate source package;
- avoid a generic package/orderability or cross-item precedence model;
- avoid treating a package as non-selectable merely because one of its component attributes is standard;
- add direct regression coverage for all three Spring configurations and preserve Duster selected-package behavior;
- update the commercial-readiness/current-offer counts deterministically if the implementation changes them;
- preserve the 1885-test discovery baseline unless repository test conventions require otherwise.

A safe implementation is expected to stay in the existing reporting/interface architecture. If implementation would require a new generic temporal-precedence schema or domain rule rather than a bounded exact-evidence reconciliation, that is a separate architecture decision and must stop at the configured `ACTION_REQUIRED` boundary.

## Review conclusion

The strongest next step is a correctness reconciliation, not another source retry. It uses evidence already present in the canonical model, improves the newly published configurator directly, preserves source history and avoids inventing unavailable prices, appearance states or package-compatibility rules.
