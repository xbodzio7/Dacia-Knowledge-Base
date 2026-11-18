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


## User-supplied source intake and persistence

A source upload is not a disposable conversation attachment. Before requesting a repeat upload, search current conversation files, persistent Library, Project files/knowledge and repository branches/commits/PRs. Check the source register and its official URL as well. Do not infer unavailability from the absence of an attachment in the current turn.

For every user-supplied source intended for DKB: (1) identify and verify the actual bytes, filename, byte length and SHA-256; (2) search for identical Library and repository copies; (3) retain the original in the Library if no identical copy exists; (4) archive it at the canonical repository source path when permitted; (5) register source ID, provenance, canonical path, byte length and verified hash; and (6) record any blocked step as action_required with the exact reason.

The repository is the canonical project archive; the Library is secondary. Reuse identical copies; do not create duplicates merely to satisfy a new upload request. A Git blob SHA is not a substitute for the SHA-256 of the original PDF bytes.

**No-repeat rule:** asking the Project Owner to upload a source again is the last recovery step, permitted only after the above locations have been checked and the exact bytes remain unavailable. State what was checked and why recovery failed. Never request a resend merely because session context or an earlier attachment reference was not carried forward.

## Deferred source gaps — non-value status

An unresolved source fact may be recorded in a source-specific deferred-gap ledger with the exact status **`Do sprawdzenia`**. This is a workflow status meaning that the fact has not yet been established; it is not a vehicle specification, equipment-availability state, price, quantity, or substitute for a missing master-data value.

Use this status to keep bounded packages moving when the unresolved item is not required to safely import the supported facts. Each ledger item must identify the source and subject, explain what remains unresolved, and state the next verification action. Preserve any known page references; do not invent page numbers or technical values.

Rules:
- Do not put `Do sprawdzenia` into typed master-data value or availability fields.
- Do not convert an unresolved item to `standard`, `optional`, `not_available`, zero, an empty technical value, or a guessed value.
- Keep the supported observations and their provenance separate from the unresolved item.
- A package may proceed with explicitly registered deferrals when all other acceptance criteria are met; the deferral itself must not be represented as a resolved source fact.
- Reopen a deferred item only when its source and exact applicability can be verified, or when the user explicitly prioritizes it.


## Source binary identity and capture preflight

Before capturing a documentary source, define its identity independently of its filename or search-engine representation. Record the expected model, market, model year, effective date, source URL, provenance class and distinguishing document markers. Record the SHA-256 and size of every known prior version so a revised source cannot silently overwrite or masquerade as an earlier one.

A live manufacturer URL, a cached/search-index representation and a dealer/distributor mirror are distinct evidence locations. Downloaded bytes determine the binary identity. A mirror may be used when its content is verified and the package permits it, but its actual host and provenance must remain explicit. Do not describe a dealer-hosted copy as a live manufacturer CDN response.

Before using an automated capture workflow, inspect its actual trigger, branch/path filters, permissions, artifact retention and available invocation mechanism. A workflow definition containing a manual-dispatch event does not prove that the current session can dispatch it or that a run occurred. If dispatch is unavailable, report the exact manual action required; do not imply that a merge automatically started the workflow.

For a captured PDF, retain the original bytes and independently verify the SHA-256, byte length, page count, first-page identity markers and comparison with registered versions. Store the verification result and missing-marker list in the capture manifest. A binary that fails identity verification may be retained only as a clearly labelled diagnostic artifact; it must not enter the canonical source archive or feed a master-data import. Do not make page count an acceptance condition until it has been checked against the actual document.

## Workflow completion is not source completion

A successful PR merge, a green PR quality workflow and a successful source-capture workflow are separate events. After merging a workflow or source package, verify Actions runs against the exact merge SHA and expected push event, inspect jobs and artifacts, and independently confirm the source branch, archive file and manifest. If no run exists, diagnose the trigger and permissions; never assume it ran. Source registration and master-data import remain blocked until the exact binary is durably archived and its identity is verified.

Every package report must distinguish implementation, commit, push, PR, exact-HEAD validation, merge, downstream workflow execution, binary archival, source registration and master-data import. Unobserved or failed stages remain incomplete/action-required.

## Capture manifest integrity and test boundary

A verified source-capture manifest is the machine-readable record for the captured binary. Its existing fields must be reused as the contract: source code and URL, market/model year/date, archive path, SHA-256, byte size, page count, verification status, expected first-page markers and missing-marker list. A sibling SHA-256 sidecar must identify the same digest and repository-relative archive path.

Before a verified capture is used by a package, \`python tools/dkb.py package-preflight\` checks the actual archived bytes against the manifest digest and byte length, checks the sidecar, and reconciles the manifest with the existing source-registry row. It also checks that the recorded page count is positive and that expected markers agree with the captured first-page text. The check does not re-open the PDF to recompute its page count or replace rendered page-by-page review.

The source registry's \`notes\` field remains human-readable explanatory provenance. Tests must not depend on an exact sentence, punctuation or editorial word order in that field. Test structured source facts and archive relationships instead. If a required fact is not represented in an existing canonical field, use a narrow semantic predicate until a separately reviewed schema change is justified; do not add duplicate metadata merely to satisfy a test.

Positive regression cases must show that equivalent evidence with different explanatory wording still passes. Negative cases must show that a missing marker, mismatched sidecar, missing archive, or altered binary fails. Passing this preflight does not establish that every page has been assimilated or that any price/technical value has been imported correctly.

## Source-registry metadata comparison

`data/master/sources.csv` is canonical for structured source identity. Import specifications may repeat those fields for reviewability, but importer comparisons must use the shared `tools/source_registry_contract.py` helper and exclude only the free-form `notes` field. Notes are explanatory provenance, not source identity; wording or punctuation edits must not block a valid import. SHA-256, archive path, document date, market, source code and all other structured identity fields remain strict and fail closed.

Add both positive tests (editorial notes differ, structured identity still matches) and negative tests (a changed digest or other identity field is rejected).
