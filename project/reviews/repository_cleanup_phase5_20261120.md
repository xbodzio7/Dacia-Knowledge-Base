# Repository cleanup — phase 5

**Date:** 2026-11-20  
**Base:** `main` at `66626ee8afa81b46a3c7bc5b97662cc6aa9e88bf`

## Reorganized historical and superseded documentation

Moved thirteen documents into `Archiwum/old_documentation/`, preserving their original contents:

### Earlier project scope and structure

- `Dokumentacja/00_START.md`
- `Dokumentacja/01_MODELE.md`
- `Dokumentacja/02_SILNIKI.md`
- `Dokumentacja/03_SKRZYNIE_BIEGOW.md`
- `Dokumentacja/04_REKOMENDACJE.md`
- `project/PROJECT_CONTEXT.md`
- `project/REPOSITORY_STRUCTURE.md`

These describe an earlier Sandero/Stepway-centred project structure and old purchase guidance. They are not in the mandatory reading sequence in `project/START_HERE.md`.

### Superseded project guidance

- `project/KNOWN_ISSUES.md` — obsolete snapshot claiming that core tools, PDF importers and tests were absent.
- `project/DATA_QUALITY_CHECKLIST.md` — generic checklist superseded by the mandatory quality and source-validation protocol.
- `project/DECISION_TEMPLATE.md` — old ADR-XXXX template inconsistent with the current D-### decision register.
- `project/NAMING_CONVENTIONS.md` — early naming and branch examples that are not reliable current repository guidance.
- `project/PROJECT_LIFECYCLE.md` — generic lifecycle duplicated and superseded by the current startup, package and quality contracts.
- `project/CHANGELOG_PROJECT.md` — partial project log; its recent package notes are represented in the canonical root `CHANGELOG.md`, while early project-history notes are retained in the archive.

The active documents identified as replacements are recorded in `Archiwum/old_documentation/README.md`. The root `CHANGELOG.md` remains the canonical project-wide change history. A targeted reference review of the current startup/governance documents, README and relevant documentation tests found no active references to the five superseded guidance files. This was not represented as a complete repository-wide dependency scan; GitHub code search did not provide reliable coverage.

## Preserved active documentation

- `project/AI_CONTEXT.md` remains active because `project/START_HERE.md` requires it and it contains a file-modification policy not yet migrated.
- `project/STANDARDS.md` remains active because current `DOCUMENT_TYPES.md` and `WORKFLOW_PROFILES.md` explicitly refer to it, and it retains the controlled-dictionary update rule.
- No source files, master data, tests, importers, validators or active workflows were removed.

## Safety and validation

- The archived files are preserved byte-for-byte as Git content; only their repository paths changed.
- The five superseded guidance files were not in the mandatory startup reading order.
- No local tests are claimed. GitHub Actions must validate the exact updated PR head.
- This PR remains separate from, and does not merge, any other cleanup PR.
