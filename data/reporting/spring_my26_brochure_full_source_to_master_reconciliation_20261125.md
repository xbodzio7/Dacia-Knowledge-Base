# Spring MY26 Brochure Full Source-to-Master Reconciliation

**Reviewed:** 2026-11-26  
**Status:** Fully reconciled with explicit source deferrals  
**Package:** `spring_my26_brochure_full_source_to_master_reconciliation_20261125_001`

## Scope and source identity

This review reconciles all 22 pages of the official Polish Spring brochure dated 2026-02-19 with the dated Spring MY26 price list effective 2026-02-06 and the source-linked master data for exactly three existing passenger configurations:

- `spring_essential_electric70_automatic`
- `spring_expression_electric70_automatic`
- `spring_extreme_electric100_automatic`

The brochure is archived at `PDF/Broszury/DACIA SPRING broszura 20260219.pdf`, SHA-256 `73a4c568ce273bc095f6ecf1cfa4f5f2a92324bb2f0bbc171ba45bb4a4cf3c8d`.

The MY26 price list is archived at `PDF/Cenniki/DACIA SPRING cennik MY26 20260206.pdf`, SHA-256 `ab36fba1106ca4929c42330df7896cea8fe56e8774353f6cbb5a7a94cfc18055`. It is a Dacia-branded distribution copy hosted by PGD, not a verified live manufacturer CDN binary.

## Verified source-to-master coverage

| Source surface | Existing rows in master | Result |
|---|---:|---|
| Brochure scalar technical observations | 90 | Complete for the previously approved scope |
| Brochure bounded RPM ranges | 3 | Complete |
| Brochure grade equipment availability | 126 | Complete |
| Brochure commercial item/configuration mappings | 21 | Existing dated mappings retained |
| MY26 price-list catalogue prices | 3 | Existing prices retained |
| MY26 commercial item/configuration mappings | 10 | Existing mappings retained |
| MY26 ground clearance | 2 | 155 mm for Expression and Extreme, on 15-inch wheels |
| MY26 source-to-configuration links | 3 | Existing exact links retained |
| MY26 source-to-grade links | 3 | Existing exact links retained |

The earlier Spring technical package describes the initial 54 scalar observations and 3 ranges. Subsequent common-technical migration added 36 scalar observations. The current master therefore contains **90 brochure scalar observations**, not 54. This reconciliation checked the actual master rows rather than relying on the older package description.

## Technical crosswalk: 21 candidate pairs, zero missing imports

Seven candidate attributes across three configurations were checked: seats, electric-motor power, electric-motor torque, source-stated battery capacity, battery voltage, 0–100 km/h acceleration and combined WLTP range.

All 21 configuration/attribute pairs already have exact source-linked observations in the master. Their provenance is not interchangeable:

- Seats, power, acceleration and the brochure WLTP values are already recorded from the 2026-02-19 brochure.
- 137 Nm torque, 24.3 kWh source-stated capacity and 354 V are already recorded from the three exact configurator PDFs dated 2026-08-09.
- The MY26 price list provides corroborating printed values, but adding duplicate observations would not fill missing master facts.
- WLTP range values from the brochure (222/225/225 km) remain distinct from later configurator observations (221/226/226 km). These dated source states are not collapsed.

No additional MY26 technical scalar row is approved by this review.

## Conflicts and explicit deferrals

1. **Page 2 versus page 5:** the narrative states 48 kW / 65 KM and 26.8 kWh; the page-5 technical table states Electric 70 at 52 kW / 70 hp and 24.3 kWh, and Electric 100 at 75 kW / 100 hp and 24.3 kWh. Preserve the conflict; do not manufacture a single timeless value.
2. **Torque:** the MY26 technical review flags an internal printed-unit inconsistency for the 137 value. The exact configurator observations remain unchanged; no MY26 torque row is added.
3. **Battery mass:** 204 kg is printed, but no semantically exact canonical battery-mass attribute exists. Defer rather than create a new attribute without a domain decision.
4. **Dimensions:** only the already-imported 155 mm ground-clearance observations for Expression and Extreme are accepted from the MY26 list, with 15-inch wheel applicability. Other diagram callouts remain deferred where semantic/measurement basis is not proven.
5. **Extreme DC 40 kW:** the P marker is retained in package context; no standalone Extreme DC40 availability or price is inferred.
6. **Cargo and accessories:** Cargo-only values are not projected to passenger configurations; accessories and YouClip are not silently converted into factory equipment.

## Page-level disposition

- Pages 1, 3 and 11: cover, contents and navigation context only.
- Pages 2 and 6: technical claims and diagram reconciled with the documented conflicts and measurement boundaries.
- Pages 4, 5, 7 and 9: descriptive claims cross-checked against exact grade matrices; no duplicate rows.
- Pages 8 and 21: passenger capacity and dimensions retained with existing source/measurement contexts.
- Pages 10 and 16: Cargo-only, excluded from passenger configurations.
- Page 12: six-colour palette; existing commercial item definitions/mappings retained without inventing grade defaults or prices.
- Pages 13–15: grade equipment and charging options; dated brochure, MY25, MY26 and configurator states remain separate.
- Pages 17–18: accessory/YouClip domain deferrals retained.
- Pages 19–20: primary equipment matrices; 126 existing brochure-sourced availability rows retained.
- Page 22: legal and temporal source boundary preserved.

The detailed 22-page inventory remains in `project/source-audit/spring-brochure-20260219-page-inventory.md`.

## Result

**No master-data mutation is justified.** The 21 apparent technical candidates were already represented, and the two MY26 ground-clearance observations were already imported. No duplicate rows, unsupported attributes, cross-grade projections or unresolved source values were added.

The next brochure package must be selected from a fresh portfolio-wide readiness comparison. Do not reactivate Spring or repeat the already completed Bigster brochure package.
