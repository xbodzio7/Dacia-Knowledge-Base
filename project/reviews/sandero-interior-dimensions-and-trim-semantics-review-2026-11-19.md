# Sandero / Sandero Stepway — review dimensions and trim semantics (2026-11-19)

## Decision

Close the bounded review as review-only. Keep both findings `needs_review` / `Do sprawdzenia`; do not add master data or import specifications.

## Evidence boundary

- Source: official Polish MY26 cennik dated 2026-11-02, archived at `owner_supplied/2026-11-02/3b4618d7da.pdf`, SHA-256 `8ee10aaf69a7807655d3fd9251fc999b7192a2b239ae865ea0e7f9e58dbbf28c`.
- Printed page 2: general marketing descriptions of dashboard/door materials, without exact grade-level attribute semantics.
- Printed page 3: grade-level decorative appearance descriptions. Existing upholstery, centre-console, wheel and roof-rail attributes do not preserve the distinct meanings of grille, mirror-cap, handle, insert, vent-surround, decal and mat finishes.
- Printed page 6: Sandero dimension diagram. Do not infer Stepway applicability. Unnamed interior callouts cannot be safely assigned to generic `interior_length`, `interior_width` or `interior_height` without exact label/reference-point evidence.

## Required boundaries

- `sandero-interior-dimension-callouts`: retain source context; no dimension import until exact canonical meaning and configuration scope are established.
- `sandero-decorative-trim-descriptors`: retain source descriptions; do not overload existing attributes or create a broad generic trim field.
- Preserve existing external dimension and Hybrid 155 scalar observations; do not duplicate them.

## Deliverables

- JSON/Markdown report under `data/reporting/`.
- Report registry entry.
- Focused semantic regression test.
- No changes to `data/master/`, import specifications or source binaries.

## Next package

After closure, continue with the Jogger MY26 2026-10-01 cennik review of metallic-paint price applicability (2,800/3,000 PLN) and the Extreme heated-seat package-only `P` marker. Do not create commercial mappings unless the source provides an exact colour/grade/configuration crosswalk.
