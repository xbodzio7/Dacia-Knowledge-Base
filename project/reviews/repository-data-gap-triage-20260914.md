# Repository Data Gap Triage — 2026-09-14

## Scope

Re-evaluate the repository-level data-gap backlog after the Sandero/Sandero Stepway 2026-08-09 full-modal residual boundary was closed by PR #646. The closed evidence boundary is excluded from the new queue.

## Baseline

The live `main` baseline remains 1925 tests, 47 master CSV files, 16,911 master rows, 6,682 configuration values, 139 configuration import specifications, 345 configuration value ranges, 24 range import specifications, 7,286 availability records, 416 attributes and 30 attribute categories.

## Triage result

The high-priority colour, wheel and upholstery gaps remain broad dynamic-capture scopes. They are not safe to close from static page text because the acceptance criterion requires exact grade/powertrain compatibility. The saved configurator PDF bundle explicitly contains zero separate option/package/accessory catalogue entries, so those rows must not be reconstructed from the PDFs.

`CAT-GAP-014` is selected as the next bounded package despite its medium priority because it is currently **unblocked** and materially smaller than the dynamic 81-surface gaps. It concerns only the unresolved Bigster Extreme 18-inch wheel identity and can be reconciled against current official Dacia catalogue configuration pages without interactive configurator state switching.

## Selected package

`bigster_extreme_wheel_name_reconciliation_001`

Target active configurations:

- `bigster_extreme_mildhybrid140_4x2_manual`
- `bigster_extreme_mildhybridg140_4x2_manual`
- `bigster_extreme_hybrid155_4x2_automatic`
- `bigster_extreme_hybridg150_4x4_automatic`

Current official Dacia catalogue evidence identifies the first three as `18\" TAGASAN pół diamentowane`; the 4x4 Hybrid-G 150 configuration is explicitly `18\" 225 TAGASAN pół diamentowane`. The distinction is retained rather than flattened across powertrains.

## Safety contract

- Exact configuration identity must be checked before canonical promotion.
- Source wording is retained.
- No grade-only inference.
- No 4x2/4x4 projection.
- No reopening of the closed Sandero Stepway full-modal evidence boundary.
- `CAT-GAP-002`, `CAT-GAP-003` and `CAT-GAP-004` remain open and are not silently marked complete.

## Evidence references

The selected package is supported by current Dacia catalogue pages for exact Bigster Extreme configurations. The repository configuration registry contains the four active Extreme powertrain identities used by this handoff.

## Next step

Reconcile the four exact Bigster Extreme wheel observations against the canonical attribute model. Materialize only genuinely missing exact slots; if all are already covered, close the package as a zero-data-delta reconciliation.
