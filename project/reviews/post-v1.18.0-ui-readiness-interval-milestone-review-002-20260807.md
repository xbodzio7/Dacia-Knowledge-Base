# Post-v1.18.0 UI Readiness Interval Milestone Review 002

Date: 2026-08-07  
Base commit: `b2b95cc2db67bec641d0a1a9e84c90ab87902b0e`  
Package ID: `post_v1_18_ui_readiness_interval_milestone_review_002`

## Decision status

`COMPLETE`

The five-package interval since milestone review PR #593 is complete. The interval preserved the New Spring accessory evidence boundary while adding a source-bounded appearance layer that can support a Dacia-configurator-like UI without converting representative or partial observations into complete catalogues.

No package in the interval changed `data/master`.

## Reviewed package interval

| Package | Result | Persistent boundary |
| --- | --- | --- |
| `new_spring_confirmed_card_price_capture_001` | 16 already-confirmed official Polish Dacia Shop cards reviewed; 2 additional exact current prices captured; repository-wide exact current price matches increased to 14 | 14 confirmed cards still lack captured catalogue prices; separate 28-item unresolved queue was not retried |
| `configurator_ui_appearance_data_001` | created a UI-facing appearance catalogue and exact-current choice table; complete visible colour lists and prices recorded for six exact default states | exact state data never transfers across grade, powertrain, transmission, drive, seat count or phase; model packshots are not exact appearance renders |
| `configurator_ui_grade_appearance_coverage_001` | all 21 current grade surfaces now have a representative exact selected wheel/upholstery appearance record; 14 grade pages have explicit current appearance facts; two grade surfaces had complete visible grade Design lists | representative saved appearance is not a grade-wide standard; generic highlights remain generic; incomplete Design panels remain partial |
| `jogger_essential_7seat_exact_appearance_capture_001` | dedicated official seven-seat Jogger configurator added one complete exact surface with 3 colours, 1 wheel and 1 upholstery | seven-seat evidence is independent and is not projected from the five-seat Jogger; displayed special-offer vehicle price is not canonical catalogue pricing |
| `bigster_essential_grade_design_completion_001` | Bigster Essential added a third complete current grade-level Design surface: 3 colours, 1 wheel and 1 upholstery across the two engines explicitly shown on the same grade page | grade-level Design prices are unknown; exact mild hybrid-G 140 prices are not projected to mild hybrid 140 |

## Verified New Spring accessory state

The New Spring accessory price-list scope still contains 56 exact references.

After the confirmed-card price package:

- 28 official Polish Dacia Shop cards are confirmed;
- 14 confirmed cards have exact current-price matches;
- 14 confirmed cards still lack a captured current catalogue price;
- 28 references remain unresolved;
- 0 price mismatches are established;
- the unresolved queue remains `data/reporting/official_new_spring_accessory_current_shop_unresolved_queue_20260807.csv`;
- the 28 unresolved references are not eligible for the next homogeneous retry before 2026-08-08.

Missing current shop price is not a mismatch. Unresolved shop identity is not evidence of withdrawal, incompatibility or unavailability.

## Configurator UI readiness after the interval

### Models and grades

- six current model families are covered;
- all 21 current grade surfaces have at least one source-backed representative exact appearance observation;
- official model-level packshots exist for all six model families, including Spring;
- model packshots remain model-level visual assets rather than exact colour/wheel/upholstery renders.

### Exact appearance choices

Strict complete exact-current appearance coverage is now 7 of 81 active configuration surfaces:

1. `sandero_iii_essential_tce100_manual`;
2. `sandero_stepway_iii_essential_tce110_manual`;
3. `duster_iii_essential_ecog120_4x2_manual`;
4. `jogger_essential_5seat_ecog120_manual`;
5. `jogger_essential_7seat_ecog120_manual`;
6. `bigster_essential_mildhybridg140_4x2_manual`;
7. `spring_essential_electric70_automatic`.

For those exact states the UI may expose the complete captured colour list and exact visible colour prices. `CAT-GAP-002` remains open for the other 74 active surfaces.

### Grade-level Design

Complete visible current grade-level Design lists are captured for 3 of 21 grade surfaces:

- Sandero Journey;
- Bigster Expression;
- Bigster Essential.

The remaining 18 grade surfaces are not promoted to complete alternative-choice catalogues. They may still expose source-backed representative selected appearance and explicit grade highlights.

### Wheels and upholstery

All 21 current grade surfaces have at least one exact representative wheel and upholstery observation. This is sufficient to render an evidence-labelled representative appearance on grade cards.

It is not sufficient to claim that the observed wheel/upholstery is the only available choice or universally standard across every powertrain unless an independent grade-level source proves that scope.

### Packages and options

The existing master commercial layer already contains substantial exact configuration mappings for named packages and standalone options. A concurrent open PR #598, `data(reporting): add configurator commercial choice readiness`, inventories this layer as:

- 34 non-appearance commercial items after excluding six Spring paint items;
- 167 selector-offer mappings;
- 162 priced selector offers;
- 5 valid but unpriced Spring offers;
- 88 package/option composition attribute rows;
- all six model families represented.

PR #598 is **not part of this five-package reviewed interval** and is not merged by this review. It was created concurrently and modifies `project/state.json` / `project/STATE_SUMMARY.md`, so it must be reconciled with the post-review main state before any merge.

Its evidence boundary is useful and should be retained if/when integrated:

- blank amount means unknown/not stated, never zero;
- exact configuration mappings do not transfer across model/grade/powertrain/transmission/drive/seat/phase;
- exact selected-stock observations are not duplicate selector offers;
- arbitrary combinations of individually valid options/packages must not be declared orderable without direct evidence;
- generic dependency/conflict/orderability rules are not currently modeled.

## What is ready for the planned UI

A Dacia-like interface can now be implemented without waiting for every strict catalogue gap to close, provided it obeys the evidence contract:

1. model selection — ready;
2. grade/version selection — ready;
3. powertrain/transmission selection — ready from canonical configuration data;
4. representative model/grade imagery — ready at model-packshot level;
5. exact colour selector — enable only for exact states with complete choice capture;
6. grade-level colour/wheel/upholstery selector — enable only where a complete grade Design list is captured;
7. otherwise show representative selected appearance plus a clear partial-data state rather than inventing alternatives;
8. named package/option selector — source-backed mappings are substantially present, but simultaneous multi-choice compatibility remains bounded/partial;
9. standard equipment and comparison — already mature in the existing data-product layer;
10. final price — exact base price and individually source-priced choices can be shown; a multi-choice total must not imply verified orderability unless combination rules support it.

## Remaining blockers to a fully equivalent configurator

The interval does **not** establish a complete clone of the official configurator. Remaining source/data boundaries are:

- `CAT-GAP-002`: 74 of 81 exact active surfaces still lack complete exact current colour choice lists with prices or an equivalent explicit current compatibility rule;
- 18 of 21 grade surfaces do not have a complete visible grade-level Design panel captured;
- alternative wheel catalogues remain incomplete for many exact states;
- alternative upholstery catalogues remain incomplete for many exact states;
- generic package/option dependency, conflict and simultaneous-orderability graph is not modeled;
- five mapped Spring commercial choices are valid but still lack captured prices in the concurrent #598 inventory;
- official images are model-level packshots, not a deterministic render matrix for selected colour/wheel/upholstery combinations.

## Source/access boundary

For many non-default grades the official public page exposes only the `Design` section heading or selected state, while the complete interactive panel is not reproducibly available through the current static retrieval channel.

Safe ways to close those exact surfaces remain:

- an official public target-state `conf` URL;
- an official saved-configuration PDF preserving exact state identity and date;
- a repeatable browser capture recording exact grade, powertrain, transmission and every visible choice with price;
- an explicit official current rule proving that the choice list is invariant across the relevant configurations.

Unsafe shortcuts remain forbidden:

- synthesizing opaque `conf` links;
- transferring a default-state palette to another engine or grade;
- treating one selected saved colour/wheel/upholstery as a full choice catalogue;
- interpreting an omitted choice as unavailable without a complete source scope;
- recolouring model packshots and presenting them as official exact renders.

## CI observation

The three UI-readiness reporting packages again triggered many specialized reporting workflows unrelated to the changed model scope because several workflows broadly react to `data/reporting/**`.

This confirms, rather than merely suggests, the previously identified CI trigger-scope optimization opportunity. A future bounded CI package may replace broad specialized triggers with dependency-specific `paths`, while keeping `Quality` universal. It should remain separate from data and UI work.

## Options considered

| Option | Value | Boundary assessment | Decision |
| --- | --- | --- | --- |
| Retry the remaining 28 New Spring Shop references on 2026-08-07 | None today | violates the explicit `eligible_on_or_after: 2026-08-08` boundary | Defer until eligible |
| Merge concurrent PR #598 inside this milestone review | Medium/high UI value | concurrent branch is outside the five-package interval and writes canonical state files; merging it here would mix package boundaries | Do not merge in review; reconcile separately |
| Start the Dacia-like UI shell using the new readiness contracts | High | safe if incomplete selectors are hidden/labelled and no missing data are inferred | Ready as a future UI package |
| Continue exact appearance capture through synthesized configurator deep links | Superficially high | provenance would be unsafe because target-state identity is not reproducible | Reject |
| Optimize specialized CI trigger scopes | Operational value | independently justified by repeated broad workflow activation, but unrelated to appearance data | Separate future package |

## Next bounded package

`new_spring_current_shop_retry_cycle_002`

Status remains `planned` with `eligible_on_or_after: 2026-08-08`.

The package must process all 28 remaining unresolved exact New Spring accessory references as one homogeneous logical package with internal chunks and a same-package consolidated summary. It must preserve unresolved semantics unless new official Polish Dacia Shop exact-part-number evidence is found.

The concurrent configurator-commercial-readiness PR #598 remains an independent candidate for reconciliation after this review. It must not overwrite the post-review canonical state.

## Automation conclusion

The data layer is now sufficiently structured to begin a Dacia-like UI architecture without lowering evidence standards. The next gains in factual completeness require either new exact configurator evidence or the date-gated Spring Shop retry; they cannot be safely manufactured through inference. The most useful tooling improvement remains CI trigger-scope optimization rather than another orchestration framework.
