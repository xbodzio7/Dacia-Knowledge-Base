# Sandero / Sandero Stepway Eco-G 120 — fuel-specific tank-capacity import

**Package ID:** `sandero_ecog120_fuel_tank_capacity_cennik_import_20261118_001`  
**Date:** 2026-11-18  
**Status:** Candidate package; exact-head CI and merge pending  
**Decision:** D-032 — reuse existing capacity attributes

## Portfolio gap assessment

The latest registered Polish MY26 cenniks for the five active model families were reconciled against source/configuration relationships, dated catalogue prices and commercial mappings:

| Model | Latest source | Configurations linked | New price rows | Commercial mappings | Assessment |
|---|---|---:|---:|---:|---|
| Sandero / Sandero Stepway | 2026-11-02 | 19 | 15 | 209 | 4 Hybrid 155 prices explicitly confirmed unchanged |
| Duster | 2026-11-02 | 16 | 0 | 64 | 16 catalogue prices already present and unchanged from 2026-09-01 |
| Bigster | 2026-11-02 | 0 by intentional price-only contract | 13 | 86 | 13 direct price observations; no source-configuration links by design |
| Jogger | 2026-10-01 | 12 | 11 | 54 | One seven-seat Essential Eco-G 120 price cell is explicitly a dash |
| Spring MY26 | 2026-02-06 | 3 | 3 | 10 | All three exact catalogue-price cells represented |

No missing current catalogue-price or commercial-matrix rows were identified in these five latest registered MY26 cenniks. Unchanged prices were not duplicated, and explicit dashes were not converted into prices. The Spring MY25 stock cennik is a separate MY25 dealer-stock scope and is not mixed into MY26 history. Striker remains excluded while its price list is unavailable.

## Source evidence

- Official source: [Dacia Sandero / Sandero Stepway MY26 cennik effective 2026-11-02](https://cdn.group.renault.com/dac/pl/pdf/cenniki/sandero-price.pdf.asset.pdf/3b4618d7da.pdf)
- Source code: `src_pl_sandero_stepway_price_my26_20261102`
- Archived binary: `owner_supplied/2026-11-02/3b4618d7da.pdf`
- SHA-256: `8ee10aaf69a7807655d3fd9251fc999b7192a2b239ae865ea0e7f9e58dbbf28c`
- PDF page 5 (technical-data table; printed page 4 in the package's page references), row `Pojemność zbiornika paliwa (l)`.
- The row explicitly distinguishes `LPG: 40` and `Ben: 50` for both Eco-G 120 manual and Eco-G 120 automatic powertrain columns.

## Imported observations

The nine exact Eco-G 120 configurations linked to the source each receive two dated observations:

- `fuel_tank_capacity`, `fuel_type_code=petrol`, value `50 L`;
- `fuel_tank_capacity`, `fuel_type_code=lpg`, value `40 L`.

Total: **18 observations** dated 2026-11-02.

The cennik does not state whether the 40 L LPG value is total vessel capacity or filling capacity. The import therefore uses the existing undivided `fuel_tank_capacity` attribute with explicit fuel context. It does not classify the LPG value as total or usable.

## Data-model decision D-032

The repository already contains the appropriate canonical attributes:

- `fuel_tank_capacity` — one undivided fuel-tank capacity value;
- `lpg_vessel_capacity_total` — total internal LPG pressure-vessel capacity;
- `lpg_vessel_filling_capacity` — source-stated LPG volume available or permitted for filling.

No generic duplicate total/usable attributes or schema columns are added. The existing Jogger cennik's explicit `50/40` total/filling pair remains represented by its two LPG-specific attributes. No Jogger value is copied to Sandero.

## Preservation and exclusions

- Older undifferentiated 50 L observations from the 2026-06-26 source and the 2026-02-02 brochure remain unchanged.
- No previous observation is overwritten or migrated.
- No LPG total/filling value is inferred from the Sandero 40 L figure.
- No injection-type value is imported: the Sandero table does not separate petrol and LPG injection wording, and no cross-model transfer is permitted.
- No brochure or configurator data is used for this package.
- No catalogue price or commercial mapping is changed.

## Validation

- Declarative import spec: `data/imports/configuration_values/sandero-ecog120-fuel-tank-capacity-20261102.json`
- Shared importer: `tools/import_configuration_values.py`
- Contract tests verify all 18 rows, exact fuel contexts, source-page text/hash, nine configurations and preservation of older observations.
- Full Quality and Repository Baselines are required on the final exact PR head.
