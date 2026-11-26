# Duster Mini Technical Page 21 Ambiguity Review

Date: 2026-07-28
Source: `src_pl_duster_mini_brochure_20251020`
Page: 21
Package: `residual_gap_006`

## Scope

Review the single ambiguous technical candidate while preserving its exact text, source line, page and attached evidence. The package is review-only and creates no master-data row or approved import specification.

## Authored decision

Candidate `6fd0360bfac47f6996e0fb04b3de4470e2edb507a12c70d96008d442a1489a6c` at line 56 is **partially covered**.

The visual table shows a steering-type row followed by a separate turning-circle row. Only `steering_type = Elektryczne wspomaganie układu kierowniczego` belongs to the candidate. Its three exact records cover Hybrid 155 configurations.

The following attached signatures are not selected because they belong to other labelled rows on the same page:

- `turning_circle_wheel_track = 10.96`;
- front and rear brake types;
- standard tyre specification;
- `maximum_kerb_weight = 1454`;
- payload range `451–525`.

The same steering value is visibly printed for Hybrid-G 150 4×4, but no attached record covers that powertrain. It remains a source fact and is not projected from Hybrid 155 configurations.

## Result

- reviewed candidates: 1;
- partially covered: 1;
- selected signatures: 1;
- selected records: 3;
- `data/master` changes: none;
- `data/imports` changes: none.

## Next package

**Duster Mini Equipment Page 23 Ambiguity Review** — review 26 ambiguous equipment candidates against 61 preserved signatures without automatic promotion.
