# Complete Source Assimilation Standard

**Project:** Dacia Knowledge Base (DKB)  
**Status:** Active  
**Effective from:** 2026-08-02

## Purpose

This document defines the mandatory treatment of every documentary source used by DKB. It prevents partial, question-driven reading from being mistaken for complete source analysis.

## Core rule

Every PDF, brochure, price list, saved configuration, instruction or equivalent documentary source must be analysed from the first page to the last page before it is considered assimilated.

Reading only the pages needed for the current package is allowed for preliminary triage, but it must be labelled `partial_review` and must not be described as complete source analysis.

## Source priority for vehicle data completion

For a defined model year, market and validity date, source collection follows this order:

1. **Official dated price list / brochure** — primary source for the historical product state.
2. **Other official dated documentary sources** — used to complete or clarify the primary source when their scope is explicit.
3. **Official interactive configurator** — used after documentary extraction and repository gap analysis to fill genuine omissions, resolve configuration dependencies, or record current-web differences whose effective date is not established.
4. **Other sources** — only when explicitly permitted by the package scope and with provenance.

The configurator must not become a substitute for complete price-list or brochure extraction.

A current undated configurator observation must not silently overwrite a dated historical value.

## Mandatory data-completion sequence

For model, version or configuration data-completion work:

1. establish the exact official documentary source set;
2. fully assimilate the applicable price lists and brochures;
3. compare the complete documentary fact inventory with master data;
4. identify genuine gaps, contradictions and unresolved applicability;
5. use the configurator only against those gaps or for explicitly separate current-web evidence;
6. reconcile configurator observations against the documentary evidence;
7. import the accepted canonical fact once, with exact provenance.

Facts already covered by the assimilated documentary source must not be re-imported merely because the configurator exposes the same field.

For prices, standard equipment, optional equipment, unavailable equipment, packages and option prices, the dated price list/equipment matrix remains the historical baseline. Current configurator prices and availability remain current-web evidence unless their effective date is established.

For technical specifications, a configurator field must first be checked against the assimilated documentary source. If the source already contains the specification, the configurator observation is a cross-check rather than a new master fact. If the specification is genuinely absent, the configurator may supply it when applicability and provenance are explicit.

## Source lifecycle

Each documentary source has one of these coverage states:

- `registered` — identity, provenance and hash are recorded, but content has not been fully analysed;
- `partial_review` — selected sections were used for a bounded question or package;
- `fully_assimilated` — every page and relevant visual element was reviewed and all supported facts were inventoried;
- `fully_assimilated_with_deferrals` — complete review was performed, but named facts remain deliberately deferred because the current data model cannot preserve their context;
- `blocked` — complete review cannot be performed because the exact source bytes or readable pages are unavailable.

Registration, hash verification, a normalized slice or successful use in one migration does not by itself establish `fully_assimilated` status.

## Mandatory full-document procedure

Before a source becomes `fully_assimilated`, the maintainer must:

1. verify the exact document identity, date, market, version and SHA-256 when available;
2. review every page, including tables, footnotes, legends, symbols and embedded images;
3. create a section and page inventory;
4. extract every fact that may belong to the current DKB domain, not only facts needed by the active package;
5. record applicability boundaries such as model, grade, engine, gearbox, seat count, market, model year and observation date;
6. compare the complete fact inventory with master data, existing normalized snapshots and explicit non-import decisions;
7. classify every identified fact as imported, already represented, deferred with reason, contradictory, superseded or out of scope;
8. record exact page evidence for every proposed master-data mutation;
9. run a second-pass completeness check asking whether any table row, option, package, footnote or technical value remains unclassified.

## Evidence record requirements

A fact intended for master data must retain, directly or through a source-normalization artifact:

- canonical source code;
- document page number;
- document section or table name;
- exact configuration or applicability scope;
- observation or validity date;
- interpretation status and confidence;
- explicit distinction between absence from a selected configuration and unavailability in the product range.

A missing item in a saved-configuration PDF is not evidence of `not_available`. Full option availability must come from a price list, complete configurator option matrix or another source that explicitly covers unselected options.

## Visual-content rule

Parsed text alone is not sufficient when the source contains tables, symbols, layout-dependent applicability columns, footnotes, diagrams or text embedded in images. The rendered page must also be inspected.

## Migration gate

A migration based on a documentary source may proceed only when:

- the relevant fact has exact page-level evidence;
- the source coverage state is recorded;
- all competing sections of the same document have been checked for qualifications or contradictions;
- related supplied documents have been reconciled when they cover the same product state.

A migration may use a `partial_review` source only for a strictly bounded fact if the package explicitly records that the remainder of the document is unaudited. It must not close the source-assimilation task.

## Audit requirement for legacy sources

All PDF sources registered before this standard took effect must undergo a retrospective coverage audit. Until that audit is complete, prior data remains usable but is not assumed to prove complete extraction of the source.

The audit must produce:

- a canonical PDF inventory;
- a coverage state for every document;
- page/section coverage evidence;
- a list of omissions, contradictions and deliberate deferrals;
- bounded corrective packages for confirmed gaps.

## Definition of done

A source-assimilation package is complete only when:

- all pages and rendered visuals have been reviewed;
- every relevant fact is classified;
- page-level evidence is recorded;
- repository comparison is complete;
- corrective migrations are either completed or queued with an exact evidence boundary;
- tests and project-state checks pass.

## Session continuity

Every AI session must read this document before working with documentary sources. Conversation memory must never substitute for the source coverage registry or page-level audit artifacts.
