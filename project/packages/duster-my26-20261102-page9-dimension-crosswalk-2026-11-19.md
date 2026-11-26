# Duster MY26 2026-11-02 — Page 9 Dimension Diagram Crosswalk

## Goal

Reconcile every rendered label and paired measurement on printed page 9 of the official Polish Duster MY26 cennik dated 2026-11-02 against the exact source-linked 16-configuration scope and existing dimension observations.

## Source

- Source code: `src_pl_duster_price_my26_20261102`
- Archived PDF: `owner_supplied/2026-11-02/f07ca0a87f.pdf`
- Registered PDF: `PDF/Cenniki/DACIA DUSTER cennik MY26 20261102.pdf`
- SHA-256: `dd6c65d048d7531251967ba39bb8ab6767256882325254e9b3eaafac11d89118`
- Printed page: 9 (PDF page index 8)
- Source relationships: 16 exact configurations, relationship `documents`

## Review result

Import 18 missing scalar observations for three attributes across six configurations:
- front track: 1574 mm (4x2), 1573 mm (4x4)
- rear track: 1547 mm (4x2), 1562 mm (4x4)
- ground clearance: 209 mm (4x2), 217 mm (4x4)

The ground-clearance values appear in reverse order (217/209) in the diagram. Their assignment follows the previously reviewed Duster 4x2/4x4 mapping. Do not assume all slash-separated pairs share one ordering.

The ten older 4x2 configurations already have the relevant values. Roof height with rails, width, wheelbase, overhangs and overall length are also already represented for all 16 configurations; no duplicate rows are added.

## Exclusions

Interior callouts 1443/1432, 907/894 and 14° remain unmapped. The 2092 mm tailgate-open height is not imported. No new attributes or source relationships are created.

## Acceptance

- Three declarative import specs, 18 exact observations, IDs 8527–8544.
- Source PDF archive and SHA-256 verified.
- Exact 16-configuration source scope and all 18 values verified by a focused test.
- Generic import verification may use `--skip-source-text` because diagram numerals are graphical and are not reliably present in extracted PDF text; the archived file hash remains mandatory.
- All six required CI checks and generated-state checks must pass on the exact final PR head before merge.
