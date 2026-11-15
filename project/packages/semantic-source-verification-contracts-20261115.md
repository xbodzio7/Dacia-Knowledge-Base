# Semantic source-verification contracts and CI failure prevention

**Package ID:** `semantic_source_verification_contracts_20261115_001`  
**Status:** Implementation in progress; pending final CI  
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

Implementation uses the existing Bigster source registry row, `bigster_my26_20261102_capture.json`, its `.sha256` sidecar and the archived PDF. The source test now checks the actual binary hash/size and structured manifest fields rather than a hard-coded notes sentence. `package-preflight` validates every verified capture manifest against the source registry, sidecar and actual archived bytes. Regression coverage proves that editorial wording changes pass while missing marker evidence and a modified binary fail. No new source metadata fields are introduced.

## Acceptance criteria

- [x] Semantic test policy documented in the mandatory quality protocol.
- [x] Decision D-025 recorded.
- [x] Focused semantic regression tests implemented against the existing canonical schema.
- [x] Source archive integrity validation is included in `package-preflight`; the focused regression runs before the Python 3.14 full quality gate.
- [ ] Documentation/state generators and full quality pass on the final PR head.
- [ ] PR reviewed; no automatic merge.

## Explicit exclusions

- No changes to PR #826, #807 or #634.
- No price or source-data re-import.
- No new source metadata schema fields without a separate evidence-backed design.
- No changes to master CSV records.


## Implementation details

- \`tools/package_preflight.py\`: read-only validation of verified capture manifests, actual archive SHA-256/byte length, sidecar digest/path, first-page marker consistency and source-registry linkage.
- \`tests/test_bigster_price_list_commercial_matrix_20261001_20261102.py\`: replaces the exact notes assertion with actual Bigster archive/manifest checks and positive/negative fixtures.
- \`.github/workflows/quality.yml\`: runs the focused source-archive regression before the Python 3.14 full quality gate; Python 3.10 and 3.13 already execute it through unit-test discovery.
- \`project/QUALITY_AND_SOURCE_VALIDATION_PROTOCOL.md\` and \`project/SOURCE_ASSIMILATION_STANDARD.md\`: define the preflight's exact coverage and limitations.

The source archive preflight deliberately allows a blank \`sources.csv.file_path\` while a source-registration closure is still pending, but if that field is populated it must match the manifest. This preserves the distinction between an archived verified binary and a fully closed source-registry relationship. PR #826 remains untouched; its branch still needs its own exact-head revalidation after the semantic test correction reaches \`main\`.
