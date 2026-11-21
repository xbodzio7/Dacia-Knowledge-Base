# Sandero / Sandero Stepway MY26 Interior Dimensions and Trim Semantics Review — 2026-11-19

Report ID: sandero_my26_20261102_interior_dimensions_and_trim_semantics_review_20261119_001
Generated: 2026-11-21T21:12:29Z
Analysed commit: 63a91e55438de42d422c552ed580762d5a627ffc
Status: needs_review
Scope: Official Polish Sandero/Sandero Stepway MY26 cennik effective 2026-11-02, printed pages 2, 3 and 6; review of interior dimension callouts and decorative trim descriptors against the canonical attribute catalogue. Review-only where exact semantic mapping or configuration applicability is not established.

## Objective

Review the interior dimension callouts and decorative trim descriptors in the official Polish MY26 cennik dated 2026-11-02 against the canonical attribute catalogue. The review covers printed pages 2, 3 and 6 and the 19 source-linked configurations.

## Source and evidence

- Official PDF: `owner_supplied/2026-11-02/3b4618d7da.pdf`
- SHA-256: `8ee10aaf69a7807655d3fd9251fc999b7192a2b239ae865ea0e7f9e58dbbf28c`
- Source code: `src_pl_sandero_stepway_price_my26_20261102`
- Printed page 2 contains broad marketing descriptions of dashboard and door materials; it does not establish exact grade/configuration-level values.
- Printed page 3 contains grade-level appearance and trim descriptors. Existing fields such as `upholstery_variant`, `centre_console_variant`, `wheel_design`, `wheel_material`, `wheel_finish`, `roof_rails` and `modular_roof_rails` retain their narrow declared meanings and cannot represent other component finishes.
- Printed page 6 is a Sandero dimension diagram, not a Stepway dimension page. Some cabin callouts do not have a sufficiently explicit measurement name, reference point or configuration crosswalk.

## Findings

1. `sandero-interior-dimension-callouts` — `needs_review`. Do not map unnamed cabin values to inferred headroom, elbow room, seatback angle, seat height, boot width or other generic dimensions. Preserve the diagram context until exact semantics and applicability are established.
2. `sandero-decorative-trim-descriptors` — `needs_review`. Do not overload upholstery, centre-console, wheel or generic appearance fields with grille, mirror-cap, door-handle, dashboard/door insert, vent-surround, decal or mat-pattern descriptions.

## Outcome

- 0 master rows added or updated.
- 0 new attributes.
- 0 import specification rows changed.
- Existing external dimension observations preserved.
- Existing Hybrid 155 scalar observations not duplicated.
- No source binary changed.

This package is a completed evidence review with explicit semantic deferrals, not a claim that the source descriptions are absent. No unsupported data migration is warranted.
