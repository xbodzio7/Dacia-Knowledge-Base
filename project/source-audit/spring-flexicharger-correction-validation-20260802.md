# Spring FlexiCharger correction validation

**Audit date:** 2026-08-02  
**Package:** `legacy_pdf_source_audit_governance_001`  
**Status:** correction materialized; corrected independent final Quality running before merge

## Confirmed evidence boundary

The official current Spring price-list charging matrix explicitly lists the domestic-socket FlexiCharger as an optional item priced at 1500 PLN for Spring Expression Electric 70.

A saved configuration PDF documents the equipment selected in that configuration. Absence of an unselected item from such a PDF is not evidence that the item is unavailable in the complete product range.

## Materialized correction

- Essential Electric 70: domestic-socket charging cable — optional, 1500 PLN.
- Expression Electric 70: domestic-socket charging cable — optional, 1500 PLN.
- Extreme Electric 100: domestic-socket charging cable — optional, 1500 PLN.
- Type 2 charging cable representation remains separate from the domestic-socket cable.

## Verified repository counts

- commercial item configuration mappings: 189;
- total master rows: 11730;
- discovered tests: 1797;
- configuration values: 3568.

## Continuity rule

This bounded correction does not mark the Spring brochure or price list as fully assimilated. The next package must review every page, table, legend, footnote, symbol and rendered visual before assigning a full-assimilation status.
