# Data Products v1.14.1 Interface Correction

Date: 2026-08-03

Package ID: `data_products_v1_14_1_interface_correction_001`

Status: **complete**

## Audit of v1.14.0

The v1.14.0 source tree contained the forced dark theme, grouped commercial grade choices with exact version codes, deterministic comparison-column widths and the two-axis sticky comparison grid.

The versioned release builder nevertheless bypassed the enhanced shortlist pipeline and called the lower-level selection renderer directly. Therefore the published ZIP omitted:

- the official Spring model-image supplement;
- reviewed commercial-price and technical-gap materialization;
- the comparison-open rule that prevents the sticky selection panel from covering table headers;
- per-group collapse controls;
- global **Ukryj wszystkie grupy** and **Pokaż wszystkie grupy** controls;
- session-scoped persistence of collapsed groups.

## Correction

The CLI and versioned release builder now call one canonical `collect_enhanced_browser_catalog` function and the same enhanced HTML renderer. This removes the divergent build path rather than duplicating the missing features.

The release regression test opens the generated ZIP and requires all agreed interface markers, the Spring media URL and reviewed gap/price state payload.

## Release

Publish the correction as immutable patch release `data-products-v1.14.1`; do not rewrite `data-products-v1.14.0`. The release must retain exact-source double-build identity, offline workspace verification and public-download byte identity.

## Boundaries

No source data, master data, configuration identity, reporting scope, comparison pair, ranking, recommendation or inferred value changes.
