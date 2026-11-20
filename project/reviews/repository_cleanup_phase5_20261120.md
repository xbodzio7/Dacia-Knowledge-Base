# Repository cleanup — phase 5

**Date:** 2026-11-20  
**Base:** `main` at `66626ee8afa81b46a3c7bc5b97662cc6aa9e88bf`

## Reorganized historical documentation

Moved seven early documents into `Archiwum/old_documentation/` without changing their contents:

- `Dokumentacja/00_START.md`
- `Dokumentacja/01_MODELE.md`
- `Dokumentacja/02_SILNIKI.md`
- `Dokumentacja/03_SKRZYNIE_BIEGOW.md`
- `Dokumentacja/04_REKOMENDACJE.md`
- `project/PROJECT_CONTEXT.md`
- `project/REPOSITORY_STRUCTURE.md`

These documents describe an earlier Sandero/Stepway-centred project structure and old purchase guidance. They are not in the mandatory reading sequence in `project/START_HERE.md` and are not linked from the current README. Their historical content is retained, not discarded.

Added `Archiwum/old_documentation/README.md` to mark the archive as non-authoritative and point to current documentation.

## Safety

- This is a path-only move; the seven original Git blob contents are preserved unchanged.
- No current project instructions, source files, data, tests, or tools are removed.
- No local tests are claimed; required GitHub Actions checks must validate the exact PR head.
