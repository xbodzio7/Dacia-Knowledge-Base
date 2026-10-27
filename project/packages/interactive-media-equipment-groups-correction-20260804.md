# Interactive Media and Equipment Groups Correction

## Package

- Package ID: `interactive_media_equipment_groups_correction_001`
- Kind: `user_interface_repair`
- Date: 2026-08-04
- Status: complete

## Purpose

Complete the two user-visible interface agreements that remained outside the canonical queue: make the Spring media visually consistent with the other model cards and make thematic equipment groups collapsible and closed by default while their names remain visible.

## Implemented correction

- replaces the former small Spring carousel thumbnail with the current official configurator image;
- keeps the generated Spring fallback and restricts cover framing to Spring only;
- upgrades every existing thematic equipment section to native `details`/`summary` disclosure;
- leaves every group closed at initial page load;
- keeps the Polish group name and live visible/selected counts in the summary;
- opens matching visible groups during equipment-name search and restores only search-opened groups when the query is cleared;
- closes the groups again when the filter form is reset;
- preserves existing equipment filtering, selected chips, availability reconciliation and no-inference semantics.

## Boundaries

No source-backed vehicle fact, price, availability state, model, version, configuration, comparison scope, ranking, recommendation or inferred value changes. The planned Portfolio Powertrain and Transmission Matrix remains the next package.

## Verification

The existing shortlist and release tests are extended without increasing the canonical test count. The generated standalone HTML must contain the v1.7 enhancement, the official Spring media URL, collapsible group contract and Spring-only framing markers. Full repository pull-request CI remains required before merge.
