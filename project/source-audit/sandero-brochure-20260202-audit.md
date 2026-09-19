# Sandero brochure — source audit

- Source code: src_pl_sandero_brochure_20260202
- Title: DACIA SANDERO broszura
- Publisher: Dacia
- Market: PL
- Document date: 2026-02-02
- Pages: 21
- SHA-256: adee5017a405a22dffaca0555b47b84b718f2166534652c9863ba2f97f325f97
- Canonical source: PDF/Broszury/DACIA SANDERO broszura 20260202.pdf
- Audit status: partial_review — the complete text surface was reviewed, but the PDF screenshot service did not provide rendered images for every page. Therefore the source is not promoted to fully_assimilated under SOURCE_ASSIMILATION_STANDARD.

## Page inventory

| Page | Section / content | Classification |
|---:|---|---|
| 1 | Cover / headline claims: boot up to 1108 dm3, 10" screen, hands-free, front lighting | context; claims cross-checked later |
| 2 | Interactive menu | navigation/context |
| 3 | Styling: front-end design, LED lighting, 16" wheels, shark-fin antenna | already represented / equipment evidence |
| 4 | Powertrain introduction: Eco-G 120 manual/automatic, LPG range claim, TCe 100 | contradictory historical technical wording; see conflicts |
| 5 | Interior, 7" cluster, 10" multimedia, inductive charger | already represented |
| 6 | Interior/storage and 328 dm3 / 410 l boot statement | already represented; measurement context retained |
| 7 | YouClip system and cabin organization | already represented in part; no new master mutation |
| 8 | Multimedia: Media Control, Media Display, Media Nav Live, Arkamys | already represented |
| 9 | ADAS overview: driver attention, AEBS, LKA, traffic-sign recognition | already represented |
| 10 | Additional safety-system visuals/text | already represented / context |
| 11 | Exterior colours and paint applicability | source-specific colour catalogue; not imported as generic equipment |
| 12 | Essential equipment list | already represented by configuration evidence |
| 13 | Expression equipment list | already represented by configuration evidence |
| 14 | Journey equipment and options | already represented by configuration evidence |
| 15 | Accessories catalogue/introduction | accessory scope; not factory configuration master data |
| 16 | Engine/gearbox, performance, WLTP, masses and towing | already represented where configuration-specific evidence exists; several brochure values are contradictory or country-dependent |
| 17 | Equipment matrix, essential/expression/journey | equipment evidence; overlaps current price-list/configurator evidence |
| 18 | Equipment matrix continuation | equipment evidence; overlaps current price-list/configurator evidence |
| 19 | Dimensions and boot capacities, including 78 l under-floor compartment | dimensions/capacities; most values already represented; 78 l deferred |
| 20 | Legal/technical disclaimer | provenance/context |
| 21 | Back-cover / publication material | context |

## Confirmed facts and repository comparison

Already represented in master data or stronger configuration-specific sources include:

- 4102 mm overall length;
- 1853 mm source-stated body width and 2012 mm width with mirrors where that source interpretation is retained;
- 1496 mm height;
- 2604 mm wheelbase;
- 10.64 m turning circle between kerbs;
- 328 l / 410 dm3 minimum boot presentation and 1108 l / 1455 dm3 maximum presentation, subject to the source's ISO/VDA context;
- 5 seats;
- major ADAS, lighting, comfort and multimedia equipment for the documented Sandero configurations;
- configuration-specific masses, towing limits and powertrain values from stronger configuration/price-list evidence.

## Contradictions requiring source-aware treatment

1. TCe 100 power
   - Brochure page 16 prints 74 (120 KM).
   - The official 2026-08-11 Sandero/Stepway price list states 74 kW (100 KM).
   - The current official Sandero configurator also identifies the base engine as TCe 100.
   - The brochure value must not overwrite the later/current source-backed 100 KM value.

2. Eco-G 120 automatic gearbox description
   - Brochure page 16 describes a 6-speed dual-clutch automatic.
   - The official 2026-08-11 price list identifies Eco-G 120 auto as a 6-speed automatic and Hybrid 155 as Multimode.
   - The brochure wording is retained as historical source evidence, not normalized into the current configuration as the sole gearbox description.

3. Width representation
   - The brochure dimension drawing gives 1853 mm body width and 2012 mm with mirrors.
   - Some later configuration PDFs use a different field interpretation for overall_width (1753 mm).
   - No blanket correction is made from one source to another; the conflicting source semantics remain traceable.

4. Fuel/CO2 values
   - The brochure's technical table leaves CO2 and WLTP consumption as "to be adjusted according to the country".
   - It is therefore not used as the authoritative Polish numerical source where the dated Polish price list provides exact values.

## Deferred facts

- Under-floor compartment volume = 78 l is source-explicit, but the current attribute model has no dedicated under-floor-storage-volume attribute and the brochure does not establish a configuration-specific applicability boundary. It is therefore deferred rather than encoded through an unrelated cargo attribute.
- Gear-specific elasticity values on page 16 remain documentary evidence unless a matching canonical attribute/context exists.
- Accessory products on page 15 remain outside the factory configuration equipment relation.

## Visual review boundary

Rendered inspection succeeded for representative content-heavy pages including the engine table, equipment pages, multimedia/safety illustrations and the dimension drawing. The web PDF screenshot endpoint repeatedly returned cache-miss errors for other pages. Because the project standard requires rendered inspection of every page before fully_assimilated, this source remains partial_review and is not falsely marked complete.

## Result

No master-data mutation is justified by this audit alone. Existing configuration-specific values remain authoritative where stronger evidence exists. The remaining work is bounded to:
1. complete rendered-page review;
2. decide whether a dedicated under-floor storage attribute is warranted;
3. reconcile remaining brochure-only technical claims against configuration PDFs/current price lists;
4. then promote the source to fully_assimilated_with_deferrals if all pages are classified.
