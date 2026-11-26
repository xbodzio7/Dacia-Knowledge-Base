# Source-First Extraction Workflow

**Project:** Dacia Knowledge Base (DKB)  
**Status:** Active  
**Effective from:** 2026-09-20

## Purpose

This document defines the mandatory operational order for extracting vehicle data from official Dacia price lists, brochures and interactive configurators.

The goal is to prevent a live configurator from becoming an accidental replacement for a dated documentary source and to prevent duplicate extraction of facts that are already covered by the primary source.

## Source priority

For a defined model year, market and validity date, use the following order:

1. **Official dated price list / brochure** — primary source for the historical product state.
2. **Other official dated documentary sources** — used to complete or clarify the primary source when their scope is explicit.
3. **Official interactive configurator** — used after documentary extraction and gap analysis to fill genuine omissions, resolve configuration dependencies, or record current-web differences whose effective date is not established.
4. **Other sources** — only when explicitly permitted by the package scope and with provenance.

A current undated configurator observation must not silently overwrite a dated historical value.

## Mandatory extraction sequence

Every source-completion package follows this sequence:

### 1. Establish the documentary source set

Identify the exact official price lists and brochures for the target model, market, model year and validity period.

Record source identity, date, scope and coverage state according to `SOURCE_ASSIMILATION_STANDARD.md`.

### 2. Fully assimilate the documentary sources

Before using the configurator for completeness work:

- review every relevant page of the documentary source;
- extract all supported technical, commercial and configuration facts;
- classify applicability by model, version, engine, gearbox, seats and other explicit dimensions;
- preserve page-level provenance;
- record facts already represented in master data;
- record omissions, contradictions and deliberate deferrals.

The task is **not** complete merely because the fields needed for the current question have been found.

### 3. Compare the source inventory with master data

Perform a gap analysis between the complete documentary fact inventory and the current repository.

For every candidate fact, determine whether it is:

- already represented correctly;
- missing and ready for import;
- represented but requiring reconciliation;
- contradictory;
- deferred because the model cannot preserve its meaning;
- outside the current project scope.

Do not use the configurator to re-extract facts already covered by the documentary source unless the package explicitly needs an independent cross-check.

### 4. Use the configurator only for the remaining gaps

The configurator is a **gap-filling and configuration-dependency source**, not the first extraction source.

Use it for facts such as:

- an option or dependency absent from the documentary source;
- a selectable state that the price list does not expose;
- a configuration-specific relationship that cannot be established from the documents;
- current-web observations that are useful for a separate provenance/reporting record.

When the configurator exposes a fact already present in the dated source, prefer the dated source for the historical master record.

### 5. Reconcile before master-data import

Configurator observations must be compared against the documentary evidence before entering master data.

Classify the result as:

- confirms existing source-backed data;
- supplies a genuine missing fact;
- current-web change with no established historical validity;
- source conflict;
- insufficient evidence.

A current-web observation with no established effective date remains reporting/provenance evidence and does not replace historical master data.

### 6. Import once

After reconciliation, import the canonical fact only once into the appropriate master structure.

Do not create duplicate records merely because the same fact was observed in both a price list and configurator.

## Special rule for price and equipment data

For prices, standard equipment, optional equipment, unavailable equipment, packages and option prices:

- the dated price list/equipment matrix is the historical baseline;
- the complete documentary matrix must be processed before configurator comparison;
- configurator option states may reveal current availability or dependencies not represented in the historical matrix;
- current configurator prices are not historical price-list values unless their effective date is established.

For equipment availability, absence from one selected configurator state is never by itself evidence of `not_available`.

## Special rule for technical specifications

Technical specifications visible in a configurator must first be checked against the assimilated documentary source.

If the cennik/brochure already contains the specification, no additional master record is required merely because the configurator exposes the same field.

If the specification is absent from the documentary source, the configurator may provide the missing observation, provided its applicability and provenance are explicit.

## Completion criteria

A model/configuration data-completion task is not considered complete until:

1. the applicable official documentary sources have been fully assimilated;
2. the documentary fact inventory has been compared with master data;
3. genuine gaps have been identified;
4. the configurator has been used only against those gaps or for explicitly separate current-web evidence;
5. conflicts and date differences have been classified;
6. all accepted master-data mutations have exact provenance;
7. no duplicate fact was created solely because multiple sources contained the same information.

## Prohibited shortcuts

Do not:

- start with the configurator when the applicable cennik/brochure has not been fully assimilated;
- copy configurator data into master simply because it is easier to read;
- treat a current web page as a dated historical source without evidence;
- infer `not_available` from absence in a selected configuration;
- replace a dated source with an undated current observation;
- declare a document complete after reading only pages relevant to one question;
- duplicate a master fact because it was independently observed in another source.

## Relationship to existing governance

This workflow supplements:

- `project/SOURCE_ASSIMILATION_STANDARD.md` — complete documentary-source coverage;
- `project/WORKFLOW_PROFILES.md` — execution and recovery workflow;
- `project/state.json` — canonical current package and execution state;
- `project/DECISIONS.md` — approved data-model decisions.

Where source evidence and workflow documentation differ, the exact source evidence and approved decisions remain authoritative for domain facts; this document governs the order in which evidence is collected and reconciled.

## End of document
