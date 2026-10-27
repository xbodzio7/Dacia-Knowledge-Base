# Spring Brochure Technical Observations — 2026-02-19

## Goal

Reduce visible `brak danych` fields for the three existing passenger Spring configurations by importing only direct, grade-bounded technical observations from the already registered official Polish brochure.

This package intentionally takes precedence over the previously planned Bigster paint-options package because it fills core comparison fields for configurations that previously had no technical observations. It adds no model, version, configuration, powertrain or canonical attribute.

## Source

- Source code: `src_pl_spring_brochure_20260219`
- File: `PDF/Broszury/DACIA SPRING broszura 20260219.pdf`
- Document date: 2026-02-19
- SHA-256: `73a4c568ce273bc095f6ecf1cfa4f5f2a92324bb2f0bbc171ba45bb4a4cf3c8d`
- Relevant pages: 8, 18 and 21

The three source-to-configuration relationships already present in `source_configurations.csv` are reused without widening their scope:

- `spring_essential_electric70_automatic`
- `spring_expression_electric70_automatic`
- `spring_extreme_electric100_automatic`

## Imported contract

The package adds 54 scalar observations, 18 for each exact configuration:

- passenger seats;
- electric-motor power;
- maximum speed;
- acceleration 0–50 km/h and 0–100 km/h;
- combined WLTP range;
- wheel-track turning circle;
- kerb weight, payload and gross vehicle weight;
- minimum and maximum ISO 3832 luggage volume;
- tyre specification and wheel size;
- front and rear suspension;
- front and rear brake type with source-stated diameter.

It also adds three inclusive `max_power_rpm` ranges, preserving the printed endpoints rather than inventing a single representative RPM. The three `boot_capacity` observations receive exact one-to-one ISO 3832 cargo-context rows (rear bench upright, main luggage compartment, optional equipment states unstated).

## Applicability boundaries

The source footnotes are applied literally:

- Electric 70 values are assigned only to Essential and Expression;
- Electric 100 values are assigned only to Extreme;
- Essential, Expression and Extreme grade-specific ranges, masses, payloads, tyres and wheel sizes remain separate;
- Cargo-only values and Cargo applicability are not projected onto passenger configurations.

## Deliberate non-imports

The package does not import or infer:

- motor torque or torque RPM, because the printed torque unit is internally inconsistent;
- gross or net battery capacity, because the source provides an unqualified capacity only;
- city range, because no matching canonical city-range attribute is available in this package;
- energy consumption, because the printed unit and numeric scale are inconsistent;
- charging times or DC charging capability, because the table includes option-qualified states;
- steering-assistance text or steering-wheel turns, because there is no matching scalar contract selected here;
- axle loads or brake-servo diameter, because no matching canonical attribute is selected;
- body dimensions from the diagram, because positional layout alone is not treated as a safe field mapping;
- the Cargo luggage volume of 1085 litres.

## Completeness effect

The Electric 70 completeness scope changes from zero technical slots to 19 source-backed slots for each of its two existing configurations. Extreme receives the same 18 scalar attributes and one power-RPM range under its own Electric 100 evidence.

## Verification

- versioned CSV import specification;
- deterministic importer with `--apply` and `--check` modes;
- exact PDF hash and exact configuration relationships;
- exact row counts, ID suffixes, grade values, ranges and cargo contexts;
- explicit regression protection for non-imported ambiguous fields;
- synchronized completeness report, canonical project state and documentation baseline;
- full repository test and quality gates.
