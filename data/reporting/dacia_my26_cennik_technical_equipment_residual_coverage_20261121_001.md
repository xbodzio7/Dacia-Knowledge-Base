# Dacia MY26 Official Cennik Technical and Equipment Residual Coverage Assessment

Report ID: dacia_my26_cennik_technical_equipment_residual_coverage_assessment_20261121_001
Generated: 2026-11-21T21:39:00Z
Analysed commit: 2fb6e52bc40a387c91f2c292af8af238d2b3df92
Status: needs_review
Scope: Latest registered official Polish MY26 Dacia cenniks across the five model families already represented in the master data: Sandero/Sandero Stepway, Duster, Jogger, Bigster and Spring. Reconcile catalogue-price cells, source links, commercial mappings, technical scalar values and equipment availability; exclude brochures, configurator inference, accessories, promotions and financing.

## Result

The five model families already represented in the master data have been reconciled against their latest registered official Polish MY26 cenniks. The assessment found **no additional technical or equipment facts that are both missing and safely importable** after the Duster and Spring dimension packages. No master data changed in this assessment.

| Model / source date | Source configurations | Catalogue price cells | Source-specific price rows | Commercial mappings | Technical scalar observations | Equipment availability observations |
|---|---:|---:|---:|---:|---:|---:|
| Sandero / Sandero Stepway — 2026-11-02 | 19 | 15 | 15 | 209 | 111 | 27 |
| Duster — 2026-11-02 | 16 | 16 | 0 (16 reused) | 64 | 18 | 0 |
| Jogger — 2026-10-01 | 12 | 11 | 11 | 54 | 0 | 0 |
| Jogger — 2026-11-02 | 12 | 11 | 0 (11 reused) | 12 | 0 | 0 |
| Bigster — 2026-10-01 | 13 | 13 | 13 | 86 | 150 | 564 |
| Bigster — 2026-11-02 | 0 (intentional) | 13 | 13 | 86 | 0 | 0 |
| Spring MY26 — 2026-02-06 | 3 | 3 | 3 | 10 | 2 | 0 |
| **Total** | **75** | **82** | **55** | **521** | **281** | **591** |

The Bigster November source intentionally has no `source_configurations` links: its 13 catalogue prices and 86 commercial mappings are represented directly, while its technical table is explicitly dated 01.10.2026 and is already covered by the October source. The Jogger November edition reuses all 11 catalogue-price rows and adds only 12 dated special non-metallic paint mappings. No unchanged catalogue price was duplicated.

## Completed source-backed additions

- **Duster:** 18 missing exterior-dimension observations from page 9, across six exact 4x2/4x4 configurations: front track, rear track and ground clearance. All other supported exterior dimensions were already represented.
- **Spring:** two 155 mm ground-clearance observations for Expression Electric 70 and Extreme Electric 100, explicitly equipped with 15-inch wheels. Essential remains `not_stated` for this source because it has 14-inch wheels.
- **Spring package marker:** Extreme DC 40 kW charging is included in the priced POWER package; no standalone Extreme DC40 option was added.
- **Jogger:** the 2026-11-02 source is registered; its 11 unchanged catalogue prices were reused and 12 special non-metallic paint mappings at 2,800 PLN were added.

## Remaining evidence boundaries

| Model | Finding | Disposition |
|---|---|---|
| Sandero / Stepway | Eco-G 120 injection and LPG 40 l total/fillable semantics | `Do sprawdzenia`; do not transfer Jogger wording without a normalized shared-engine identity |
| Sandero / Stepway | Interior dimensions and decorative trim descriptors | `Do sprawdzenia`; no exact canonical attribute/configuration crosswalk |
| Duster | Interior/seat callouts and tailgate-open height | Excluded; semantics do not match canonical attributes |
| Jogger | 2026-10-01 historical paint amount | `Do sprawdzenia`; archived page-3 visual verification is still needed; historical mapping remains unchanged |
| Jogger | Metallic paint 2,800/3,000 PLN pair | `Do sprawdzenia`; no named-colour or exact configuration crosswalk |
| Bigster | HDC qualifier “Extreme oraz 4x4” | `Do sprawdzenia`; source does not establish conjunctive vs independent applicability |
| Bigster | Additional dimension callouts | `Do sprawdzenia`; no exact canonical attribute/applicability mapping |
| Spring | Electric 70 power and battery capacity | `Do sprawdzenia`; page 2 narrative conflicts with page 5 technical table |
| Spring | Overall-height, side-view and interior dimension callouts | `Do sprawdzenia`; conflicting or unlabelled measurement semantics |

## Scope and exclusions

- Five existing model families only: Sandero/Sandero Stepway, Duster, Jogger, Bigster and Spring.
- Seven source/date entries across the five model families.
- No brochures, configurator inference, accessory catalogues, promotions or financing offers.
- No source omission is interpreted as unavailability.
- No new canonical attributes or architecture changes are proposed.
- Striker is a separate model-family expansion. Its official cennik is available, but adding Striker requires explicit owner approval and remains outside this completed five-family assessment.

## Decision

The current cennik-only technical/equipment coverage assessment is complete with explicit evidence deferrals. No further safe master-data import is identified from the reviewed price lists. The next possible scope expansion is Striker; do not start it until the Project Owner explicitly approves it.
