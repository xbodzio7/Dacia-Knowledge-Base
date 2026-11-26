# Vehicle Price and Product-Offer Change History Plan

**Project:** Dacia Knowledge Base (DKB)  
**Status:** Proposed implementation plan  
**Created:** 2026-11-06  
**Scope:** Dated official Polish Dacia price lists (cenniki) first; other documentary sources only after the current cennik-only priority is closed.

## 1. Objective

Provide a reliable, reproducible history of how each Dacia model, grade and exact configuration changes over time. A user should be able to answer:

- What was the catalogue price of this exact configuration on a given effective date?
- When and by how much did its price change?
- Which equipment items or packages changed from standard to optional, became unavailable, or changed price?
- Which configurations or grades were added, withdrawn or explicitly marked unavailable?
- Which changes were catalogue changes and which were temporary commercial/financing campaigns?

The history must be evidence-led and must not infer a change from a missing row.

## 2. Data-model-first principle

Do not introduce a second authoritative event ledger before auditing the existing dated observations. The current model already contains time-oriented structures, including:

- `configuration_prices` — dated catalogue-price observations;
- `commercial_item_configurations` — dated prices and applicability/availability of options and packages;
- `configuration_attribute_availability` — dated standard/optional/not-available equipment states;
- `configuration_attribute_values` and `configuration_attribute_value_ranges` — dated technical observations;
- `sources`, source-to-configuration/version relationships and versioned import specifications — provenance.

**Default implementation:** derive change events deterministically from these source observations and expose them as reports/exports. Add a new master table or event schema only if the audit proves that an essential historical fact cannot be represented without loss in the existing structures. Any such schema change requires a separate documented architecture decision and migration plan.

## 3. Event taxonomy

Keep the following event classes distinct:

1. **Catalogue price:** price introduced, increased, decreased, unchanged confirmation, or explicitly withdrawn. Store gross/net basis, currency, market, exact configuration and effective date.
2. **Equipment state:** standard, optional, package-only, explicitly unavailable, or changed state. Preserve the exact attribute, grade/configuration applicability and source legend.
3. **Option/package commercial terms:** option or package introduced/withdrawn, price changed, applicability changed, or contents changed.
4. **Configuration portfolio:** exact configuration/grade introduced, withdrawn, or explicitly unavailable. A missing matrix cell is not a withdrawal.
5. **Technical specification:** changed dated value/range, with units, fuel context and measurement basis preserved.
6. **Commercial campaign:** discount, finance benefit, lease instalment, insurance or limited-time offer. Never merge these into catalogue price history.

## 4. Required provenance and comparison fields

Every derived event must be traceable to:

- market and model family;
- exact configuration/grade and (where applicable) fuel, gearbox and seat count;
- event class and stable item/attribute code;
- previous observation and new observation, including their dates;
- absolute and percentage delta where meaningful;
- effective date, kept separate from PDF publication/document date and campaign-validity dates;
- source code, source version/hash when available, page number, section/table and exact applicability boundary;
- comparison status: verified change, verified unchanged, explicit withdrawal/unavailability, already represented, deferred, conflict, or insufficient evidence.

A report must never present a comparison as a verified change if either side lacks an exact source-backed observation.

## 5. Date and evidence rules

- Treat the printed effective date of each table/section as authoritative for that section; do not assume every page appended to a PDF shares the cover-page date.
- Keep document date, price-matrix effective date, accessory-list validity, campaign start/end and observation date as separate concepts.
- Compare only like-for-like market, model year, configuration, grade, price basis and item scope.
- An explicit dash or “not available” applies only to the exact cell and scope printed by the source.
- Absence from a source, omission from a selected configuration, or a changed configuration name is not evidence of withdrawal.
- Do not interpolate between dated price lists or infer a missing historical state.
- Preserve conflicts and unresolved applicability as deferred evidence, not as typed master facts.
- Reconcile a newly received source against current main and all earlier source observations before import; do not duplicate unchanged values merely to create an event.

## 6. Implementation stages

### Stage 0 — Existing-model and source-coverage audit

- Inventory the date/provenance fields and constraints in all relevant master tables, import specs and reporting tools.
- Identify whether each event class can be represented without loss.
- Audit existing official cennik sources and their page/section coverage states.
- Produce a gap report with exact examples and a recommendation on whether any schema extension is necessary.

**Exit gate:** no new authoritative table is proposed until this audit is complete.

### Stage 1 — Deterministic change-event derivation

- Build a read-only comparison layer over existing master observations.
- Pair observations only by stable exact identifiers and matching scope.
- Classify changes, unchanged states, explicit unavailability and unresolved comparisons.
- Calculate deltas only for comparable numeric values.
- Emit deterministic JSON and Markdown/CSV outputs with source/page provenance.
- Add regression tests for date ordering, duplicate observations, exact-scope matching, missing-source cases and explicit versus inferred unavailability.

### Stage 2 — User-facing history reports

- Add a model-level timeline and a configuration-level timeline.
- Provide filters for effective date, grade, engine/fuel, gearbox and event class.
- Show old value, new value, absolute/percentage change and source evidence.
- Separate catalogue price, equipment/package and temporary campaign views.
- Preserve an exportable, deterministic snapshot.

### Stage 3 — Verified historical backfill

- Backfill only periods for which exact official cennik files and effective dates are preserved.
- Start with the 2026 Sandero/Sandero Stepway, Jogger, Duster and Bigster cennik series after the current source reconciliation queue is complete.
- Record unchanged states only where an actual dated source confirms them.
- Keep source files and SHA-256 values in the repository whenever the exact bytes are available.

### Stage 4 — Ongoing maintenance

- Add the history comparison to every future cennik reconciliation package.
- Require a before/after summary and source-page evidence in the package receipt.
- Update generated history reports and project state in the same logical package.
- Periodically audit the historical chain for gaps, duplicate observations and inconsistent effective dates.

## 7. Acceptance criteria

The feature is ready only when:

- every displayed event has a source, effective date, exact scope and page/section evidence;
- all comparisons use matching configuration and price/equipment semantics;
- no event is inferred from omission or absence of evidence;
- temporary promotions and financing offers remain separate from catalogue prices;
- unchanged states are distinguishable from missing data;
- the output is deterministic and reproducible from repository data;
- regression tests cover false-positive changes, duplicate sources, date conflicts and configuration changes;
- the history can be regenerated without manually editing generated output.

## 8. Explicit exclusions for the initial implementation

- No brochure or configurator assimilation while the active cennik-only priority remains in force.
- No current-web offer treated as a historical dated fact without a validity date.
- No speculative reconstruction of unavailable old PDFs.
- No redesign of the stable data architecture unless Stage 0 proves a concrete representation gap.
- No automatic claim that a configuration was discontinued merely because it is absent from a later matrix.

## 9. First pilot

Use Sandero/Sandero Stepway 2026 dated cenniks as the first pilot after the current 2026-11-02 source package has passed full source-to-master reconciliation. The pilot must include at least one catalogue-price change, one unchanged price, one equipment-state comparison, one option/package price comparison and a separate commercial-campaign example. Extend to other model families only after the pilot's semantics and tests are accepted.
