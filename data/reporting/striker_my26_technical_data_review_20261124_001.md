# Striker MY26 technical data review — 2026-11-24

## Scope and source

- Official Polish Striker MY26 cennik effective 2026-11-02
- Source: `src_pl_striker_price_my26_20261102`; archived file: `PDF/Cenniki/striker-price.pdf`
- SHA-256: `d9e1e874ceaf2b65faf37650ad7be4b9a7c9710ee1d09cbdee5856c286e62d35`
- Eight pages; pages 6 and 7 reviewed; 11 exact source-linked configurations

## Imported data

- **423 scalar observations** across 42 declarative import specifications
- **21 bounded-range observations** across 3 range specifications
- Observation date: 2026-11-02

### Technical data

The source identifies three 1,199 cm³ three-cylinder powertrain columns (12 valves) and one 1,789 cm³ four-cylinder hybrid 155 column (16 valves). The first three are 48 V mild-hybrid systems; hybrid 155 is a 280 V full hybrid. Source-stated engine outputs, torque, traction-motor output, HSG output, battery capacity, emission standard, particulate-filter presence and transmission descriptions are stored without calculating unprinted totals.

The hybrid 150 row prints engine output plus a 10 kW traction motor; no combined system total is calculated. Hybrid 155's 116 kW system output is stored because it is explicitly printed.

### Performance, fuel and capacity

Petrol/LPG distinctions are preserved for mild hybrid-G 140 acceleration, tank capacity, CO₂ and combined fuel consumption. Printed intervals are stored as bounded ranges, not flattened. Hybrid 155 CO₂ notation `95/96` remains unresolved.

Minimum luggage volume is imported using `boot_capacity`. Maximum folded-seat volume is not imported because no existing attribute unambiguously captures its measurement basis.

### Dimensions

The page-7 vector diagram was visually inspected because its measurements are not embedded in the PDF text layer. Imported dimensions include overall length, widths with and without mirrors, overall height, height with tailgate open, wheelbase, front/rear track, overhangs and ground clearance. 4x2/4x4 differences are assigned only to matching configurations.

## Explicit exclusions

- Hybrid 155 CO₂ `95/96`: no unsupported range or trim mapping.
- Minimum mass ready to drive: not mapped to kerb-weight attributes.
- Maximum folded-seat luggage volume: no exact existing attribute.
- Tyre-size list: no trim-level standard/optional fitment crosswalk; only summer tyre season is recorded.
- 1000 m standing-start time: no matching attribute; `NC` is not converted to a number.
- Interior/seat diagram measurements with unexplained asterisks and unlabeled endpoints remain unresolved.

## Non-changes

No prices, priced options, package memberships, commercial-item mappings, model/version/configuration records or equipment availability records are changed. No brochures or configurator observations are used.

## Source verification

The archived PDF identity is fixed by its registered SHA-256, byte size and eight-page count. Page-6 specifications validate source text. Page-7 dimension specifications skip text-layer matching only because the diagram is vector artwork; binary hash and file identity remain verified.
