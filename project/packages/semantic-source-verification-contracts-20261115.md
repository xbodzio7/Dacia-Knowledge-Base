# Semantic source-verification contracts and CI failure prevention

**Package ID:** `semantic_source_verification_contracts_20261115_001`  
**Status:** In progress  
**Date:** 2026-11-15  
**Base:** `main` at `1895c97731caf35c68dacd910184b00481c29971`

## Trigger

PR #826 exposed a stale assertion requiring the exact phrase `SHA-256 verified from uploaded raw bytes` in a free-text notes field. The canonical source notes had been rewritten to describe the same evidence more precisely. Three Python versions failed on the same assertion; this was one stale test contract, not three separate runtime defects.

## Scope

- Establish a durable rule that tests validate source facts and structured contracts, not editorial prose.
- Define positive and negative regression expectations for source integrity/provenance.
- Clarify that structural package preflight does not replace semantic validation or the full quality matrix.
- Keep PR #826, #807 and #634 unchanged.

## Accepted safeguards

1. Exact prose assertions are prohibited for explanatory notes unless exact wording is itself the controlled requirement.
2. Reuse existing canonical fields; do not create duplicate metadata fields to satisfy tests.
3. Verify source identity and applicable integrity evidence: SHA-256, byte size, page count, markers, archive path and manifest relationship.
4. Test wording independence (same facts, changed prose passes) and evidence sensitivity (missing/contradictory facts fail).
5. Diagnose the first causal failure and classify it before changing code, data or expectations.
6. Treat repeated matrix failures from one assertion as one root cause.
7. Run focused regression tests, canonical state/documentation checks and the full required matrix on the final exact PR head.

## Implementation boundary

This first governance slice records the accepted contract. It deliberately does not modify PR #826 or add speculative fields to the source schema. The next implementation slice must inspect the current source registry/manifest schema and refactor the failing source test to semantic predicates with positive and negative fixtures. The test must verify the archived Bigster PDF's actual registered facts rather than a hard-coded note sentence.

## Acceptance criteria

- [x] Semantic test policy documented in the mandatory quality protocol.
- [x] Decision D-018 recorded.
- [ ] Focused semantic regression tests implemented against the existing canonical schema.
- [ ] Preflight/quality workflow runs the focused contract before the expensive full matrix where practical.
- [ ] Documentation/state generators and full quality pass on the final PR head.
- [ ] PR reviewed; no automatic merge.

## Explicit exclusions

- No changes to PR #826, #807 or #634.
- No price or source-data re-import.
- No new source metadata schema fields without a separate evidence-backed design.
- No changes to master CSV records.
