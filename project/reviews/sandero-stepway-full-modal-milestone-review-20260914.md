# Sandero Stepway Full Modal Milestone Review

Date: `2026-09-14`

## Scope

This review closes the five logical packages completed after the full-modal evidence-boundary delivery and determines the next bounded work without changing domain semantics.

Reviewed packages:

| PR | Result | Merge commit |
|---|---|---|
| #640 | state synchronized; live availability baseline retained at 7286 | `39d39c39db3405da67811b4f563ce41ff137545f` |
| #641 | 315 technical residuals reconciled against current main | `1a483858c260f627d627565c0422e1350c60f5e1` |
| #642 | `drive_layout` source vocabulary reconciled without normalization | `400606513329a467361bcad43f5cb5f4e2221d16` |
| #643 | technical residual materialization preflight: 0 new rows | `37d9f692602f868a9cf6ccaea65b793ed85a2932` |
| #644 | equipment residual materialization preflight: 0 new rows | `a43d30c8d49249a8e6d098dc4ead15554cc20767` |

## Verified milestone outcome

The five-package closure did not increase the current master-data baseline. The two historical materialization scopes were re-evaluated against the actual current `main` rather than replayed from stale branches:

- technical: 315 candidates → 297 exact occupied scalar slots + 18 composite/non-scalar deferred; 0 new rows;
- equipment: 286 safe occurrences → 277 explicitly mappable occurrences, 370 occupied canonical targets, 9 schema-gap occurrences; 0 new availability rows.

The repository baseline therefore remains:

- 1925 tests;
- 47 master CSV files;
- 16911 master rows;
- 6682 configuration attribute values;
- 139 configuration value import specifications;
- 345 configuration value ranges;
- 24 configuration range import specifications;
- 7286 availability records;
- 416 canonical attributes in 30 categories.

## Remaining bounded evidence

The full-modal residual review still contains evidence that was deliberately not promoted to master data. The immediate residual boundary is:

- 155 other equipment occurrences preserved outside positive normalization;
- 60 technical contextual/model-qualified occurrences preserved from scalar promotion;
- 9 `kluczyk z 3 przyciskami` occurrences retained as a schema gap inside the otherwise safe equipment set;
- negative/base and unmapped wording remains preserved and must not be converted into positive states.

These observations do not by themselves authorize a new canonical attribute, a cross-configuration projection, or a guessed value. Any future promotion must be based on an exact current source-to-canonical mapping and occupied-slot/value agreement.

## Decisions for the next package

1. Do not reopen PR #634.
2. Do not revive or modify PR #639.
3. Do not reuse or rerun the historical PR #637 branch.
4. Keep the 7286 availability baseline unchanged until a genuine absent canonical observation is proven.
5. Review the preserved evidence as a separate bounded package. First classify each residual as already covered, composite/context-only, schema-gap, genuinely missing canonical observation, or unresolved evidence.
6. A schema change for `kluczyk z 3 przyciskami` is not assumed; it requires an explicit repository/domain decision if evidence demonstrates that the current model cannot represent it.

## Acceptance criteria for the next package

- exact source/configuration boundaries remain attached to every reviewed observation;
- no inference from absence or wording alone;
- no cross-configuration, fuel, transmission, grade or model-year projection;
- current canonical dictionaries and occupied slots are checked before any proposed write;
- zero-data-delta remains an acceptable result;
- any genuine data gap is isolated into a small, independently verifiable change.

## Conclusion

The accelerated milestone closure is clean. The previous apparent materialization backlog was largely stale relative to current `main`; it has now been reconciled without duplicate data. The next logical work is therefore **preserved-evidence review**, not replay of historical materialization PRs.
