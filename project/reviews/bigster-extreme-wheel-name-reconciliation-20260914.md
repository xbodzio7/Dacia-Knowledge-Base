# Bigster Extreme wheel-name reconciliation — 2026-09-14

## Scope

Close `CAT-GAP-014` by checking the four active Bigster Extreme powertrain configurations against the current canonical `wheel_design` coverage.

## Result

All four exact configuration/attribute slots are already occupied. No new canonical rows, import specifications or attributes are required.

The source-backed distinction is retained:

- three 4x2 Extreme configurations use the 18-inch TAGASAN semi-diamond-cut wording;
- the Hybrid-G 150 4x4 configuration carries the 18-inch 225 TAGASAN wording.

The audit deliberately does not flatten the 4x2 and 4x4 variants into one generic wheel value.

## Evidence

Current Dacia Poland catalogue pages expose exact configuration identities and the corresponding TAGASAN wheel wording for the selected Extreme powertrains. The repository already contains the corresponding exact `wheel_design` slots, so adding another row would create duplicate canonical evidence rather than improve coverage.

## Acceptance

- target configurations: 4
- occupied canonical slots: 4
- missing slots: 0
- duplicate slots: 0
- new master rows: 0
- new import specifications: 0
- new attributes: 0
- outcome: **closed, zero-data delta**

## Safety

No inference from grade alone, no cross-powertrain projection, no vocabulary normalization, and no reopening of the Sandero Stepway full-modal residual boundary. PR #634, PR #639 and historical PR #637 remain untouched.

## Next gap

The next material gap remains `CAT-GAP-002` (exact colour compatibility surfaces). Unlike this package, its unresolved surfaces require reproducible exact-state configurator interaction. Static current pages do not prove the full grade/powertrain compatibility graph, so the project should stop at that execution boundary rather than invent values.
