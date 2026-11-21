# Duster MY26 2026-11-02 — Page 9 Dimension Diagram Crosswalk Review

Report ID: duster_my26_20261102_dimension_diagram_crosswalk_review_20261119_001
Generated: 2026-11-21T21:40:00Z
Analysed commit: 63a91e55438de42d422c552ed580762d5a627ffc
Status: needs_review
Scope: Duster MY26 printed page 9 exterior-dimension diagram; all 16 exact source-linked configurations, with six missing 4x2/4x4 targets imported. Interior/seat callouts and tailgate-open height are explicitly excluded.

## Result

The page-9 diagram was reconciled against the exact 16 configurations linked to the official Polish Duster MY26 cennik effective 2026-11-02. The review supports **18 missing scalar observations** across six configurations: front track, rear track and ground clearance. No existing observation was overwritten or duplicated.

## Source and exact scope

- Official source: [Dacia Duster MY26 price list, effective 2026-11-02](https://cdn.group.renault.com/dac/pl/pdf/cenniki/duster-price.pdf.asset.pdf/f07ca0a87f.pdf)
- Archived source: `owner_supplied/2026-11-02/f07ca0a87f.pdf`
- Registered PDF: `PDF/Cenniki/DACIA DUSTER cennik MY26 20261102.pdf`
- SHA-256: `dd6c65d048d7531251967ba39bb8ab6767256882325254e9b3eaafac11d89118`
- Printed page: 9 (PDF page index 8)
- Exact source relationship: `src_pl_duster_price_my26_20261102` → 16 configurations (`documents`)

The source scope contains 13 4x2 configurations and three 4x4 configurations. This exact relationship resolves the earlier 4x4 source-link limitation retained in the 2025 brochure crosswalk.

## Visual crosswalk

| Attribute | 4x2 | 4x4 | Disposition |
|---|---:|---:|---|
| Roof height with rails | 1656 mm | 1661 mm | Already present for all 16 |
| Front track | 1574 mm | 1573 mm | 6 missing observations imported |
| Rear track | 1547 mm | 1562 mm | 6 missing observations imported |
| Ground clearance | 209 mm | 217 mm | 6 missing observations imported |
| Body width | 1813 mm | 1813 mm | Already represented |
| Width with mirrors | 2069 mm | 2069 mm | Already represented |
| Front overhang | 857 mm | 857 mm | Already represented |
| Wheelbase | 2657 mm | 2658 mm | Already represented |
| Rear overhang | 828 mm | 827 mm | Already represented |
| Overall length | 4343 mm | 4343 mm | Already represented |

The ground-clearance pair is printed as 217/209, i.e. in the reverse order to the front/rear track pairs. Its 4x2/4x4 assignment follows the previously reviewed Duster mapping (209 mm for 4x2; 217 mm for 4x4), rather than assuming every slash-separated pair has the same order.

## Exact imported scope

The six configurations with missing observations were:

**4x2 Eco-G 120 automatic**
- `duster_iii_expression_ecog120_4x2_automatic`
- `duster_iii_extreme_ecog120_4x2_automatic`
- `duster_iii_journey_ecog120_4x2_automatic`

**4x4 hybrid-G 150 automatic**
- `duster_iii_expression_hybridg150_4x4_automatic`
- `duster_iii_extreme_hybridg150_4x4_automatic`
- `duster_iii_journey_hybridg150_4x4_automatic`

Three declarative import specifications add 18 observations, IDs 8527–8544, dated 2026-11-02. The ten earlier 4x2 configurations retain their existing 2025-10-20 observations. No new attributes or source relationships were created.

## Explicit exclusions

- 1443/1432: interior-width callouts without an unambiguous canonical measurement basis.
- 907/894 and 14°: interior/seat geometry; 14° is not mapped to approach or departure angle.
- 2092: tailgate-open height, not normal closed-vehicle overall height; existing exact configurator observations remain unchanged.
- No speculative grade-specific or powertrain-specific splits beyond the source's explicit 4x2/4x4 applicability.

## Validation contract

- Source PDF archive and registered SHA-256 are verified.
- The test checks all 16 source-linked configurations, the exact six import targets, all 18 values and IDs, source provenance, and preservation of prior observations.
- Generic declarative import specifications are retained under `data/imports/configuration_values/`.
- Full required CI and generated-state checks must pass on the exact final PR head before merge.
