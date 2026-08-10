# Sandero Stepway Full Modal Residual Review

Date: 2026-08-10

## Result

The historical package planned a residual review around 873 rows. Recomputing against the current conservative reconciliation contract shows a live residual of 940 rows.

- 286 equipment rows are positive, source-bounded normalization candidates.
- 315 technical rows are scalar or source-state normalization candidates.
- 124 technical rows can reuse an existing explicit contextual parser.
- 59 negative or base-state equipment rows remain literal evidence only.
- 96 equipment rows have no safe direct canonical mapping and remain literal evidence.
- 60 model-qualified or multi-context technical rows remain literal evidence.

In total, 725 rows have a safe normalization path and 215 rows remain preserved evidence.

## Safety boundary

A normalization candidate does not require a duplicate master observation when the same configuration slot is already covered by another exact 2026-08-09 source. Negative/base-state wording never proves `not_available` or optional factory availability. Model-qualified or multi-context values are not projected to a scalar unless an explicit parser selects the configuration-specific component.

The stale historical mapping `Liczba drzwi -> door_count` is not valid against the current attribute dictionary; the canonical target is `number_of_doors`.
