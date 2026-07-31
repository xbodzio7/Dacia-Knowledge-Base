# Jogger MY26 Fog-Light Superseding Observations

Date: 2026-07-31

Status: **complete**

## Source contract

Two exact registered Polish Jogger MY26 price lists document a dated status change for the Expression grade:

- `src_pl_jogger_price_my26_20260401`, page 5, SHA-256 `a03bb2de2cdadd51223e7d1a50aee898729172f39953bf2bfc946613d6e30d7b` — `Światła przeciwmgłowe` has the direct Expression symbol `•`;
- `src_pl_jogger_price_my26_20260703`, page 4, SHA-256 `92606411c4d8c10dd830b0d1c387fe663c4c9618422c5db639c13a23138f4a87` — the same row has the direct Expression symbol `-`.

Both sources document the same six existing Expression configurations: five- and seven-seat Eco-G 120 manual, TCe 110 manual and Hybrid 155 automatic.

## Imported observations

The April source-backed `fog_lights=standard` observations already exist and remain unchanged. The package appends six July observations with:

- attribute: `fog_lights`;
- status: `not_available`;
- observation date: `2026-07-03`;
- source page: 4;
- IDs: `5897-5902`.

The result is an explicit two-state history for every affected configuration instead of an overwrite.

## Semantic boundary

The source label is only `Światła przeciwmgłowe`; it does not say `przednie`. Therefore the package uses the existing generic boolean attribute `fog_lights`, matching the earlier April import. It does not reinterpret the row as `fog_lights_front` or `fog_lights_rear`.

The `-` symbol is imported only because it is a direct matrix cell. No omitted row, grade ordering, sibling configuration or inheritance statement is treated as negative evidence.

## Exclusions

- No April row is deleted or rewritten.
- No status is propagated to Essential, Extreme or Journey.
- No model, version, configuration or attribute is added.
- No data is transferred between seat counts, powertrains or gearboxes without each exact source relationship.

## Integrity

`tools/import_jogger_fog_light_superseding_observations.py` verifies both source hashes, the six exact active Expression configurations, both sets of source relationships, the active boolean `fog_lights` attribute, the six preserved April observations, the direct July specification, idempotent output and the contiguous availability suffix `5897-5902`.

The final pull-request diff contains exactly thirteen declared package paths and no temporary workflow or rendered source artifact. The Spring equipment regression test is narrowed to the exact Spring block `5771-5896`, so valid later imports can follow it without weakening the original 126-row contract.
