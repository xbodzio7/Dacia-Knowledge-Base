# Vehicle Change History — Implementation Plan

**Project:** Dacia Knowledge Base (DKB)  
**Status:** Proposed plan; implementation not yet started  
**Date:** 2026-11-06  
**Scope:** Official Polish Dacia price lists (cenniki) first

## 1. Objective

Provide a reliable, source-traceable history of changes in Dacia model ranges and configurations. A user should be able to answer:

- When did a catalogue price change, and by how much?
- Which configuration, grade, engine/fuel and transmission did the change affect?
- When did an option or package price or availability state change?
- Which technical or equipment values differ between dated official price lists?
- Which apparent changes cannot be established because one of the compared sources does not cover the same scope?

The history must distinguish catalogue facts from discounts, financing, lease campaigns and other temporary commercial messages.

## 2. Design principles

1. **Reuse canonical observations.** Existing dated, source-linked master records are the primary inputs. Do not copy the same facts into a second manually maintained master table.
2. **Compare like with like.** A comparison key must preserve market, model year, model, exact configuration, grade, engine/fuel, transmission, seating and the relevant attribute or commercial item.
3. **Require two-sided evidence for a change.** A change is established only when the earlier and later sources both explicitly cover the same comparison scope, or when the later source explicitly states an addition/removal or unavailability.
4. **Never infer removal from omission.** A row missing from a later document is not a discontinued configuration or unavailable option unless the document explicitly establishes that state.
5. **Keep dates distinct.** Record document publication date, price/effective date and the validity date of individual campaigns separately. Do not assume they are identical.
6. **Preserve source notation and context.** Retain page/table, printed value, unit/currency, legend/footnote interpretation and any normalization.
7. **Separate catalogue and promotional history.** Discounts, finance benefits, lease examples, warranties and accessory campaigns must not be represented as catalogue-price changes.
8. **Deterministic and reproducible.** Reports must be generated from versioned sources/master data and be stable across supported environments.
9. **No destructive overwrite.** A later observation supplements or supersedes an earlier dated observation; it does not erase historical evidence.

## 3. Proposed event model

The first implementation should be a **derived reporting layer**, not a new master-data table. Each event should contain the following logical fields:

| Field | Meaning |
| --- | --- |
| event_id | Stable deterministic identifier derived from the comparison key and source pair |
| change_type | price, commercial_item, equipment_availability, technical_value, configuration_scope or commercial_offer |
| market / model_year | Exact market and model-year scope |
| model_code / configuration_code | Exact canonical model/configuration when applicable |
| grade_code | Grade/version scope when explicitly available |
| subject_code | Attribute, commercial item, price type or configuration subject |
| previous_source_code / current_source_code | Exact source identities being compared |
| previous_document_date / current_document_date | Publication/document dates |
| previous_effective_date / current_effective_date | Validity dates of the observations |
| previous_value / current_value | Typed or faithfully represented prior/current values |
| unit / currency | Unit or currency, where applicable |
| previous_status / current_status | For states such as standard, optional or explicitly unavailable |
| delta_value / delta_percent | Calculated only for comparable numeric values |
| previous_evidence / current_evidence | Page, table/section and source-row or cell reference |
| disposition | changed, added_explicitly, removed_explicitly, unchanged, not_comparable, source_conflict or unresolved |
| notes | Qualification, normalization and reason for any limitation |

The final serialization and exact field names are subject to a small schema-design review during implementation. This plan does not approve a new master schema.

## 4. Comparison semantics

- **Price:** compare only the same configuration, market, currency and price type. Calculate absolute and percentage deltas only when both values are explicit and comparable.
- **Equipment:** compare the same canonical attribute and exact configuration. Distinguish standard, optional and explicitly unavailable. An unrecorded cell is unknown coverage, not a negative state.
- **Options/packages:** compare the same commercial item, configuration, currency and validity scope. A changed price and a changed availability state are separate event dimensions.
- **Technical values:** compare the same attribute, unit and context (including fuel, seats, measurement basis or other modeled qualifiers). Preserve conflicting observations rather than overwriting them.
- **Configuration range:** report an addition or removal only when both source inventories establish the relevant scope or the source explicitly states the lifecycle event. Otherwise report coverage as not comparable.
- **Commercial offers:** keep discounts, financing, lease, warranty and service campaigns in a separate category with their own validity intervals and terms.

## 5. Planned implementation stages

### Stage A — Sandero/Sandero Stepway historical price timeline

Use the official Polish cenniks already registered in DKB, after verifying their exact source coverage and dates. Start with catalogue prices and the dated option/package matrix. Produce a report showing:

- source chronology and source-coverage status;
- each exact configuration's price timeline;
- changes in PLN and percent;
- unchanged observations confirmed by both sources;
- explicit source gaps and non-comparable intervals.

The known November 2026 +500 PLN change is a test case, not a hard-coded assumption.

### Stage B — Equipment and technical history

Extend the same comparison engine to source-backed equipment availability and technical observations. Preserve exact configuration and contextual dimensions. Report source conflicts and non-comparable rows rather than forcing a single current value.

### Stage C — Other model families

Apply the same process to Duster, Jogger and Bigster only after their relevant official cennik source pairs have been reconciled. Keep each market/model-year/date boundary explicit.

### Stage D — User-facing outputs

Generate deterministic JSON and Markdown first. Add CSV or a searchable HTML view only if it materially improves use. Reports should allow filtering by model, configuration, change type and effective date, and should link each event back to its source evidence.

## 6. Initial acceptance criteria

The first Sandero/Sandero Stepway price-history package is accepted only when:

- the exact source set and coverage state are recorded;
- every comparable configuration/price pair has one disposition;
- the 15 price increases effective 2026-11-02 (+500 PLN each) are reproduced from source observations rather than hard-coded;
- the four unchanged Hybrid 155 prices are classified as unchanged, without duplicate master rows;
- source gaps and date mismatches are visible and are not interpreted as changes;
- numeric deltas are correct and deterministic;
- every event links to both source identities and page-level evidence;
- catalogue prices are not mixed with promotions, finance or lease examples;
- focused tests and the full repository quality gate pass on the exact final SHA;
- an independent source-to-report check confirms the events against the original cennik pages.

## 7. Open design questions to resolve before implementation

1. Whether a later dedicated configuration lifecycle relation is needed to represent explicitly introduced/discontinued configurations independently of price observations.
2. Whether commercial offers should remain a separate reporting family or receive a dedicated typed model after the current cennik backlog is complete.
3. Whether the reporting artifact should be one per source pair or one consolidated timeline with pair-level provenance.

These questions must be resolved from actual source coverage and existing data-model capabilities. Do not introduce a broad event-sourcing architecture or duplicate master table without demonstrated need.

## 8. Boundaries

- This is a plan only; it does not alter master data, import specifications, validators or the canonical schema.
- Official Polish cenniks remain the active source priority. Brochures and configurator sources are deferred until the cennik backlog is reconciled.
- No data may be inferred from an absent row, an unlabelled column, a promotional headline or a date belonging to another section of the document.
- The plan does not mark any source as fully assimilated; source coverage must be verified independently under the source-assimilation standard.

## 9. Next implementation package

After the active cennik reconciliation PRs are resolved, implement Stage A as one bounded reporting package. It should consume the existing source registry and dated master observations, produce a source-pair reconciliation artifact and a user-readable Sandero/Sandero Stepway price timeline, and add focused regression tests. The package should not modify master data unless the independent source-to-master reconciliation identifies a separate, explicitly scoped correction.
