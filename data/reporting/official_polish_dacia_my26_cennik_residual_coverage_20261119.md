# Official Polish Dacia MY26 Cennik Residual Coverage Assessment

Report ID: official_polish_dacia_my26_cennik_residual_coverage_20261119_001
Generated: 2026-11-19T10:00:15.033Z
Analysed commit: 5a6e5f317e7d163efd0a26e2ca619daa81894ab2
Status: current
Scope: Latest registered official Polish MY26 Dacia cenniks for Sandero/Sandero Stepway, Duster, Jogger, Bigster and Spring reconciled against current source links, catalogue prices, commercial mappings, scalar technical values, equipment availability and value ranges. No brochure or configurator extraction was performed; previously registered observations were treated only as existing master history. Separate accessory catalogues, promotions and financing offers are excluded.

## Result

Six registered MY26 cennik source/date entries across five model families were reconciled against current source relationships and master records. The review found **no additional technical or equipment rows that are both missing and safely importable**. No master data changed.

| Model / source date | Source configurations | Price cells | Source-specific price rows | Commercial mappings | Technical scalar rows | Equipment availability rows |
|---|---:|---:|---:|---:|---:|---:|
| Sandero / Stepway — 2026-11-02 | 19 | 15 | 15 | 209 | 111 | 27 |
| Duster — 2026-11-02 | 16 | 16 | 0 (16 reused) | 64 | 0 | 0 |
| Jogger — 2026-10-01 | 12 | 11 | 11 | 54 | 0 | 0 |
| Bigster — 2026-10-01 | 13 | 13 | 13 | 86 | 150 | 564 |
| Bigster — 2026-11-02 | 0 (intentional) | 13 | 13 | 86 | 0 | 0 |
| Spring — 2026-02-06 MY26 | 3 | 3 | 3 | 10 | 0 | 0 |
| **Total** | **63** | **71** | **55** | **509** | **261** | **591** |

The Bigster November source has zero `source_configurations` links by explicit tested contract for the price/commercial-only revision; this is not treated as a missing relationship. Its technical table is labelled as of 01.10.2026 and is already represented by the October source's 22 import specifications and 150 scalar observations.

## Verified source dispositions

- **Sandero / Stepway:** all nine pages of the 2026-11-02 cennik were visually reviewed. The 111 scalar and 27 availability rows are already present. The 40 l LPG figure is retained without interpreting total versus fillable capacity; Eco-G injection is not split by fuel. Interior dimension callouts and decorative trim descriptors remain deferred.
- **Duster:** all 16 catalogue prices are represented by existing dated price history; 64 commercial mappings are present. The page-6 table states 230 V for Hybrid 155 while page 2 separately states 260 V in narrative text. Existing 230 V observations remain unchanged; no 280 V value is warranted. The page-9 dimension diagram remains deferred because paired values lack a reliable grade/powertrain crosswalk.
- **Jogger:** 11 catalogue price cells and 54 commercial mappings are present. The principal page-5 technical values are already represented by existing observations for the exact configurations; no duplicate scalar rows are proposed. The metallic paint 2,800/3,000 PLN pair has no exact named-colour/grade assignment. Extreme heated seats marked `P` are not a standalone option.
- **Bigster October:** 150 scalar technical observations and 564 equipment observations are present, alongside 13 prices and 86 commercial mappings. 93 of 94 equipment attribute groups agree. HDC remains unresolved. Standard exterior dimension candidates are already represented by dated configuration observations; extra transverse, seatback-angle and seat-height/clearance callouts have no exact canonical attributes.
- **Bigster November:** the eight-page PDF is now archived and hash-verified. Its 13 prices and 86 commercial mappings are present. Its technical table is dated 01.10.2026, so no November duplicate is created.
- **Spring MY26:** the three exact price cells and ten priced commercial mappings are present. Page 2 narrative and page 5 technical table conflict on Electric 70 power and battery capacity; neither context is selected for technical master data. Dimension diagram and the Extreme DC 40 kW `P` cell remain deferred.

## Open findings

- **duster-page9-dimension-crosswalk:** The page-9 dimension diagram is visually reviewed but paired values are not mapped to exact grades/powertrains. Existing dimensions from other dated sources do not justify projecting the paired cennik values. Reconcile the rendered diagram labels against exact configuration scope before any import.
- **sandero-ecog120-injection-and-lpg-capacity-semantics:** The source's Eco-G injection statement does not distinguish petrol and LPG, and the 40 l LPG figure does not state total versus fillable capacity. The 18 fuel-specific capacity observations imported in PR #845 remain valid as printed values; no total/fillable classification or fuel-specific injection split is inferred.
- **sandero-interior-dimensions-and-trim-semantics:** Interior dimension callouts and decorative trim descriptors do not map unambiguously to current canonical attributes. Preserve as deferred source evidence; do not collapse them into generic dimensions or trim fields.
- **jogger-paint-variant-applicability:** The metallic paint pair 2,800/3,000 PLN is not assigned to named colours or grades by the source. Extreme heated front seats marked P are part of a package and are not a standalone priced mapping.
- **bigster-october-hdc-applicability:** 93 of 94 equipment attribute groups agree. The HDC qualifier 'Extreme oraz 4x4' does not establish an unambiguous configuration truth table. Preserve all six existing unresolved statuses.
- **bigster-october-dimension-extra-callouts:** The standard exterior dimension candidates are already represented by existing dated configuration observations. Additional transverse, seatback-angle and seat-height/clearance callouts lack exact canonical attribute mappings; no new rows are proposed.
- **spring-my26-technical-source-conflict:** Page 2 narrative and page 5 technical table disagree on Electric 70 power and battery capacity. Neither context is promoted to master technical data. The page-6 dimension diagram and Extreme DC 40 kW P cell remain deferred.

## Policy decisions

- Cennik pages remain the primary dated evidence; no brochure or configurator extraction was performed in this assessment.
- Do not duplicate unchanged price, technical or equipment observations solely to attach them to a later cennik edition.
- Do not infer applicability from omissions, `P` markers, ambiguous grade/drivetrain qualifiers or paired diagram values.
- Historical reports that describe the Bigster November or Spring MY26 binaries as unarchived are superseded by the current registered source records and verified archive files.

## Next package

`duster_my26_20261102_dimension_diagram_crosswalk_review_20261119_001`: reconcile every rendered label and paired measurement on Duster MY26 2026-11-02 printed page 9 against the exact 16-configuration scope and existing dimension observations. Import nothing unless the source establishes precise applicability; preserve the current deferral if the crosswalk remains ambiguous.
