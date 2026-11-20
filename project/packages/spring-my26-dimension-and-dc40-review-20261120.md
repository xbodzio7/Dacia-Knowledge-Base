# Spring MY26 2026-02-06 Dimension Diagram and DC 40 kW Package Marker Review

**Package ID:** `spring_my26_20260206_dimension_and_dc40_package_marker_review_20261120_001`  
**Review date:** 2026-11-20  
**Source:** `src_pl_spring_price_my26_20260206`  
**Source file:** `PDF/Cenniki/DACIA SPRING cennik MY26 20260206.pdf`  
**SHA-256:** `ab36fba1106ca4929c42330df7896cea8fe56e8774353f6cbb5a7a94cfc18055`

## Scope and source evidence

Reviewed the official Polish Spring MY26 price list effective 2026-02-06. The key evidence is on pages 3–6: wheel-size applicability (page 3), commercial package matrix and P markers (page 4), technical wheel-size footnotes (page 5), and the rendered dimension diagram (page 6). The registered binary is a Dacia-branded PGD distribution copy; it is not represented as a verified live manufacturer CDN binary.

Exact configurations:
- `spring_essential_electric70_automatic`
- `spring_expression_electric70_automatic`
- `spring_extreme_electric100_automatic`

## Page 4 — Extreme DC 40 kW P marker

**Resolved.** The P cells for DC 40 kW fast charging and V2L in the Extreme column are package components, not standalone options. The POWER package row explicitly groups CCS DC fast charging and V2L and is priced at 3,000 PLN for Extreme. The P convention is corroborated by the legend in another official Polish Dacia price list (`P = element pakietu`).

- Existing `spring_power_package` mapping for Extreme at 3,000 PLN is retained.
- Existing standalone DC 40 kW option mapping for Expression at 2,750 PLN is retained.
- No standalone Extreme DC40 option is added.
- The separate brochure-derived V2L equipment note is preserved as source-specific evidence; no silent reconciliation is made.

## Page 6 — dimension diagram

### Imported observations

The diagram states ground clearance of **155 mm for 15-inch wheels**. The price list identifies:
- Essential: 14-inch steel wheels (page 3);
- Expression: 15-inch steel wheels (page 3);
- Extreme Electric 100: 15-inch steel wheels (pages 3 and 5).

Accordingly, two dated source-specific observations were added to `data/master/configuration_attribute_values.csv`:

| Configuration | Attribute | Value | Source date | Applicability |
|---|---|---:|---|---|
| Expression Electric 70 | `ground_clearance` | 155 mm | 2026-02-06 | Explicit 15-inch wheel qualifier |
| Extreme Electric 100 | `ground_clearance` | 155 mm | 2026-02-06 | Explicit 15-inch wheel qualifier |

No 155 mm observation is assigned to Essential (14-inch wheels). Existing `ground_clearance_laden=115.3` and `ground_clearance_unladen=146.1` observations from the saved configurator PDFs are preserved unchanged. The new cennik observation is source- and date-specific; it does not overwrite or erase the distinct configurator evidence.

### Already represented

The following eight exterior measurements from the diagram are already represented for the three exact configurations and were not duplicated: overall length 3701 mm, front overhang 683 mm, wheelbase 2423 mm, rear overhang 595 mm, front track 1385 mm, overall width 1583 mm, width with mirrors 1767 mm, and rear track 1365 mm.

### Explicit exclusions / unresolved semantics

- **Overall height 1519 mm:** conflicts with the existing 1489 mm observations; the diagram does not provide a sufficiently explicit grade/wheel applicability crosswalk. No replacement or new mapping.
- **Side-view vertical callout 1900 mm:** measurement semantics are not explicitly labelled; do not map it to `height_with_tailgate_open`.
- **Interior vertical measurements 896/843 mm and interior widths 1253/1231 mm:** the drawing distinguishes positions/seat contexts that the available generic canonical attributes cannot preserve. No import.
- **Essential ground clearance 155 mm:** excluded because the source qualifies 155 mm to 15-inch wheels while Essential has 14-inch wheels.

## Validation boundary

The CSV changes are limited to two new rows with IDs 8545–8546. Existing rows and IDs are preserved. The source registry note is updated to describe the bounded import and the preserved source conflicts. A focused regression test verifies exact configuration/source/date/value mappings, exclusion of Essential, and preservation of existing configurator observations.

GitHub Actions is the execution environment for package preflight, test discovery, focused and full quality checks, project-state synchronization and generated-documentation validation. No local test execution is claimed.
