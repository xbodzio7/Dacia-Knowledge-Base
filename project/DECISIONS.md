\# Decyzje projektowe



\## D-001



Repozytorium GitHub jest jedynym źródłem prawdy.



\---



\## D-002



Excel nie jest bazą danych.



Excel jest eksportem.



\---



\## D-003



Architektura została zamknięta.



Nie przebudowujemy jej bez uzasadnienia.



\---



\## D-004



Identyfikatory są tekstowe.



Przykład:



MODEL\_SANDERO



ATTR\_ABS



ENG\_TCE90



\---



\## D-005



Każda wartość musi mieć źródło.



\---



\## D-006



Każdy import posiada historię.



\---



\## D-007



Nigdy nie poprawiamy danych ręcznie w tabelach wynikowych.



Poprawiamy źródło.



Uruchamiamy import.



Generujemy nowe dane.



\---



\## D-008



Każdy plik powinien być gotowy do commitu.



\---



\## D-009



Nie duplikujemy informacji.



Jedna informacja istnieje tylko raz.



\---



\## D-010



Repozytorium ma być gotowe do migracji do SQLite lub PostgreSQL.



\---



\## D-011 — Knowledge First



Najważniejszym produktem projektu jest wiedza.



Kod i narzędzia pełnią funkcję pomocniczą.



\---



\## D-012 — Stable Architecture



Architektura repozytorium jest uznana za stabilną.



Nowe elementy architektury mogą być dodawane wyłącznie po wykazaniu rzeczywistej potrzeby.



\---



\## D-013 — Incremental Development



Projekt rozwijany jest w małych, kompletnych pakietach zmian.



Każdy pakiet powinien być gotowy do zatwierdzenia i wykonania commitu.



\## DEC-00X — Zasady prowadzenia kolejnych sesji



Status: Accepted

Data: 2026-07-01



\### Decyzja



Od tego etapu projektu AI nie generuje kolejnych plików "z wyprzedzeniem".



Każda sesja przebiega według następującego schematu:



1\. odczyt `project/START\_HERE.md`,

2\. odczyt `project/SESSION\_STATE.md`,

3\. analiza wyłącznie dokumentów związanych z bieżącym zadaniem,

4\. przygotowanie jednego logicznego pakietu zmian,

5\. przedstawienie pełnej treści nowych lub zmienionych plików,

6\. przygotowanie gotowego polecenia `git add` oraz `git commit`.


Decision: DKB v2.1 Managed Data Model

Status: Accepted

The project separates:

- core data,
- reference dictionaries,
- validation rules,
- project governance.

This architecture minimizes duplication and enables automated validation.

\### Uzasadnienie



Projekt osiągnął etap, na którym repozytorium stanowi jedyne źródło prawdy.



Generowanie zmian bez analizy aktualnego stanu prowadzi do:

\- proponowania istniejących już plików,

\- niespójności architektury,

\- błędnych commitów.



\### Konsekwencje



\- zmiany są przygotowywane wyłącznie na podstawie aktualnego stanu repozytorium,

\- nie wykonuje się pełnego audytu bez wyraźnego polecenia użytkownika,

\- każdy commit obejmuje jeden logiczny pakiet zmian.



## ADR-00X — Domain-oriented development

Status: Accepted

Decision:

The project is developed using domain-oriented sprints.

A sprint should complete one logical area instead of introducing many unrelated changes.

Quality and consistency take precedence over rapid dataset growth.

---

## D-014 — Observation-level fuel context

Status: Accepted

Date: 2026-07-12

### Decision

`configuration_attribute_values.csv` contains an optional
`fuel_type_code` column referencing `data/master/enums/fuel_types.csv`.

The field is populated when the meaning of an observation depends on the
fuel used during the measurement, for example LPG or petrol WLTP fuel
consumption and CO2 emissions. It remains empty for fuel-independent
observations.

Fuel context is stored separately from `attribute_code`; fuel-specific
variants are not represented as duplicate attribute definitions.

### Rationale

A bi-fuel configuration can have multiple valid values for the same
attribute, date and source. The existing observation model could not
distinguish those values without encoding fuel in identifiers or notes.

An optional referenced column is the smallest extension that preserves
the source meaning, supports validation and remains compatible with all
existing observations.

### Consequences

- LPG and petrol observations use the same canonical attribute codes.
- Populated fuel contexts must exist in the fuel-type dictionary.
- Existing fuel-independent observations retain an empty context.
- Future imports may reuse the same mechanism for other fuel-dependent
  configuration observations.

## D-015 — Configuration-level equipment availability

Status: Accepted

Date: 2026-07-13

### Decision

Standard, optional and unavailable equipment is represented at the
configuration level in a dedicated
`configuration_attribute_availability.csv` relation.

The relation reuses canonical `attribute_code` entries from
`data/master/attributes.csv`. A separate equipment-item catalogue is not
introduced.

Each availability record contains:

- `id`
- `code`
- `configuration_code`
- `attribute_code`
- `availability_status`
- `observation_date`
- `source_code`
- `notes`

`availability_status` references a controlled dictionary containing:

- `standard`
- `optional`
- `not_available`
- `unknown`
- `package` — the item is available only as part of a package; the specific package identity may remain unspecified.

The absence of a record means that availability has not been imported.
It must not be interpreted as `unknown` or `not_available`.

### Rationale

The reviewed Sandero and Sandero Stepway configuration PDFs show that
equipment can differ between manual and automatic configurations of the
same version. A version-only relationship would therefore lose source
meaning.

`configuration_attribute_values.csv` stores observed attribute values.
A boolean value cannot distinguish standard equipment, optional
equipment, unavailable equipment and missing source coverage.

Reusing the existing attribute catalogue avoids duplicated equipment
definitions. A dedicated availability relationship preserves commercial
meaning, observation date and source provenance.

### Consequences

- Equipment availability is linked to `configuration_code`, not only to
  `version_code`.
- Existing attributes remain the canonical vocabulary for equipment
  features.
- Every imported availability record is dated and linked to a source.
- `unknown` is used only when the source explicitly prevents reliable
  classification.
- A missing record means that the availability has not been imported.
- Implementation requires status validation, cross-file reference
  validation, schema documentation, automated tests and SQLite coverage.
- Schema implementation and equipment import remain separate future
  packages.
- This analysis package records the architectural decision only.

## D-016 — Configuration-level wheel and upholstery values

Status: Accepted

Date: 2026-07-13

### Decision

Wheel and upholstery descriptions are represented as dated configuration
attribute values in `configuration_attribute_values.csv`. They are not
modeled as boolean equipment availability records.

Wheel observations use separate canonical attributes:

- existing `wheel_size`,
- existing `wheel_material`,
- new `wheel_design`,
- existing `wheel_finish`.

`wheel_size` stores the explicit rim-size description supplied by the source.
`wheel_material` stores an explicitly stated material such as `steel` or
`alloy`. `wheel_design` stores the commercial design name such as `ERALIA` or
`TAMIA`. `wheel_finish` stores an explicitly stated visual treatment such as
`bi-tone`.

Compound source wording may be decomposed only into components stated by the
source. For example, `TAMIA BI-TON` supports design `TAMIA` and finish
`bi-tone`; wheel material must not be inferred unless the same source wording
explicitly identifies it.

Upholstery is represented by a new string attribute
`upholstery_variant`. It stores the named commercial variant or a normalized
source description. Explicit material details remain part of that normalized
value, while the exact source wording stays in `notes`. Upholstery presence is
not represented by a boolean.

Every imported value remains linked to the configuration, observation date
and source document. The `notes` field preserves the source page, source
section and original wording needed to audit the normalized value.

### Stepway Essential source conflict

The Stepway Essential source contains incompatible wheel-design assertions:

- the configuration-selection section identifies steel `ERALIA` wheels,
- the equipment list identifies `TAMIA BI-TON` and also mentions steel rims.

This conflict does not support a single canonical `wheel_design` value.
The controlled source import must therefore:

- import `wheel_material = steel` only because both source sections explicitly
  support that material,
- omit `wheel_design` for Stepway Essential,
- omit `wheel_finish` for Stepway Essential because `bi-tone` belongs to the
  conflicting `TAMIA` assertion,
- preserve the conflict in documentation and regression coverage,
- wait for an independent source or corrected document before selecting
  `ERALIA` or `TAMIA`.

Two conflicting values must not be collapsed into one preferred value and
must not be encoded as simultaneous equipment availability.

### Ordering criteria

Internal ordering criteria, configurator condition codes, technical selection
keys and similar implementation metadata are not vehicle equipment. They must
not create attributes, availability records or configuration values.

Such criteria may be mentioned in review notes only when needed to explain
why a source fragment was excluded.

### Rationale

Boolean modeling would lose the actual wheel or upholstery variant and could
not distinguish design, material, size and finish. The existing dated
configuration-value relation already preserves source provenance and is the
smallest compatible extension of the stable architecture.

Treating the Stepway Essential discrepancy as unresolved prevents the model
from turning contradictory source claims into false certainty. Importing the
shared material observation retains useful knowledge without selecting an
unsupported design.

### Consequences

- Wheel and upholstery records are added to
  `configuration_attribute_values.csv`, not
  `configuration_attribute_availability.csv`.
- The source-import package adds `wheel_design` and
  `upholstery_variant` to the canonical attribute catalogue before using
  them.
- Existing `wheel_size`, `wheel_material` and `wheel_finish` definitions are
  reused.
- Values are normalized, while exact Polish wording and page provenance stay
  in `notes`.
- Missing value rows mean that a value was not imported; they do not mean
  `not_available`.
- Ambiguous Stepway Essential design and finish remain absent until supported
  by a non-conflicting source.
- This package records the model and conflict policy only; source-data import
  remains a separate package.

## D-017 — Evidence-gated commercial packages and options

Status: Accepted

Date: 2026-07-13

### Decision

A commercial package or option is modeled only when a source explicitly
identifies a named selectable commercial item and links it to a vehicle
configuration, observation date and source document.

A package must not be inferred from:

- a group or section of standard equipment,
- a trim or version name,
- simultaneous presence of several equipment attributes,
- configurator condition codes or ordering criteria,
- technical wording that merely uses the word `option`.

Individual equipment features remain in
`configuration_attribute_availability.csv`. Selected descriptive values such
as exterior colour, wheel variant or upholstery remain in
`configuration_attribute_values.csv`. Those records must not be relabeled as a
commercial package.

The package name, its configuration-level availability or selection, its
price, and its component features are separate facts. A future package model
must preserve those facts separately instead of collapsing the package into
its components or duplicating component availability.

### Current source coverage

The seven reviewed Sandero and Sandero Stepway configuration PDFs do not
contain a named commercial `Pakiety`, `Opcje` or equivalent offer section.

Their configuration summary lists only:

- equipment version,
- exterior colour,
- wheels,
- upholstery.

The following pages list standard equipment and technical specifications.
The phrase `Minimalna Masa Pojazdu Gotowego Do Jazdy (Bez Opcji)` is a
technical measurement qualifier. It is not evidence of an offered or selected
commercial option.

The current sources therefore do not support package or option records and do
not justify a package-specific schema extension.

### Evidence required for a future package model

A future source-backed package may be modeled only when the source provides
enough information to preserve at least:

- an explicit commercial package or option name,
- the affected configuration or offer,
- the observation date and source,
- availability or selected state when stated,
- price and currency when stated,
- component membership when stated.

Missing component details must remain missing. They must not be reconstructed
from coincident standard-equipment lists.

### Consequences

- No package or option table is added by this analysis package.
- No current equipment or configuration value is reclassified as a package.
- Package and option work remains deferred until explicit source evidence is
  available.
- The next source-backed package imports the exterior colour explicitly listed
  for all seven current configurations.
- Internal configurator metadata and the technical `Bez Opcji` qualifier remain
  excluded from commercial package data.

## D-018 — Axle-neutral standard tyre specification

Status: Accepted

Date: 2026-07-13

### Decision

A source field that identifies one standard tyre specification for the complete
vehicle without distinguishing front and rear axles is represented as a dated
configuration-level string value.

The canonical attribute for this fact is `standard_tyre_specification` in the
`Wheels` category. The normalized value preserves the complete source
specification, including nominal size, load index and speed symbol. For the
seven current Sandero sources the normalized value is `205/60 R16 92H`.

The exact source wording, page and section remain in `notes`. The planned
import uses `configuration_attribute_values.csv` and does not create an
equipment-availability record.

The source wording must not be decomposed into:

- `front_tyre_size` and `rear_tyre_size`, because the source does not state an
  axle assignment,
- `max_tyre_load_index` and `max_tyre_speed_rating`, because `92H` identifies
  the stated standard tyre and is not described as a maximum approved rating,
- `wheel_size`, because that attribute stores the selected rim size rather
  than the complete tyre specification.

Axle-specific sizes or maximum approved ratings may be imported separately
only when a source explicitly provides those meanings.

### Current source coverage

All seven reviewed Sandero and Sandero Stepway configuration PDFs contain the
same technical field on page 5 under `Koła i opony`:

`Opony Standardowe 205/60 R16 92H`

The current dataset contains selected rim descriptions, wheel material,
commercial wheel design, wheel finish and exterior colour. It does not contain
a standard-tyre-specification value.

The attribute catalogue already contains axle-specific tyre-size attributes
and maximum-rating attributes, but their meanings do not match the
axle-neutral source field. Reusing them would add unsupported axle or maximum
semantics.

### Consequences

- The next source-backed package adds the active string attribute
  `standard_tyre_specification`.
- The next package imports seven dated values, one for each current
  configuration.
- The normalized value is `205/60 R16 92H`.
- Source page 5, section `Koła i opony` and the original Polish field remain in
  `notes`.
- Existing `front_tyre_size`, `rear_tyre_size`, `max_tyre_load_index`,
  `max_tyre_speed_rating` and `wheel_size` records are not populated from this
  field.
- Equipment availability and configuration prices remain unchanged.
- This analysis package changes documentation only.

## D-019 — Exact emission-standard variants

Status: Accepted

Date: 2026-07-14

### Decision

An explicitly stated emission-standard variant is preserved as its own controlled
dictionary value when reducing it to an existing broader value would lose source
meaning. The page-6 source field `Norma Emisji Spalin Euro 6e BIS` is therefore
represented by the active code `euro_6e_bis` with the display name `Euro 6e BIS`.

The existing `emission_standard` attribute is reused. The existing `euro_6e`
dictionary entry remains a separate value and must not be used as an automatic
substitute for `euro_6e_bis`. A future source-data import stores the normalized
controlled value `euro_6e_bis` and preserves the exact Polish wording, page and
section in `notes`.

The source field `Poziom Hałasu Przy 50 Km/H (DB) 67` is a different fact. It
does not create an emission-standard value and remains deferred to a separate
attribute-and-unit modeling package.

### Current source coverage

All seven reviewed Sandero and Sandero Stepway configuration PDFs contain the
same page-6 technical field:

`Norma Emisji Spalin Euro 6e BIS`

The canonical attribute catalogue already contains the active enum attribute
`emission_standard`. The emission-standard dictionary currently contains
`Euro 6`, `Euro 6e` and `EV`, but not the exact `Euro 6e BIS` variant. No current
configuration value uses `emission_standard`.

### Consequences

- This modeling package adds `euro_6e_bis` to the existing emission-standard
  dictionary.
- No new attribute, relation, availability record, price or configuration value
  is introduced by the modeling package.
- The next source-backed package imports seven dated `emission_standard` values,
  one for each current configuration.
- `euro_6e_bis` and `euro_6e` remain distinct controlled values.
- The 67 dB source field remains outside this package.

## D-020 — Speed-specific vehicle noise measurement

Status: Accepted

Date: 2026-07-14

### Decision

A source field that states a noise level together with an explicit vehicle speed
is modeled as a speed-specific configuration attribute. The page-6 field
`Poziom Hałasu Przy 50 Km/H (DB) 67` is therefore represented by the active
decimal attribute `noise_level_at_50_kmh` in the new `Acoustics` category.

The measurement unit is the new `dB` unit. The condition `at 50 km/h` is part of
the attribute meaning and must not be dropped or replaced by a generic noise
level. A future source-data import stores the normalized numeric value `67` and
preserves the exact Polish wording and page in `notes`.

The source does not identify the measurement as interior, exterior, stationary,
pass-by or tied to a named test standard. It also states `DB`, not `dB(A)`.
Those meanings must not be inferred. They may be modeled separately only when
an explicit source provides them.

### Current source coverage

All seven reviewed Sandero and Sandero Stepway configuration PDFs contain the
same page-6 technical field:

`Poziom Hałasu Przy 50 Km/H (DB) 67`

The current attribute catalogue contains no canonical noise-level attribute.
The unit catalogue contains no decibel unit, and the category catalogue has no
dedicated acoustics category. Existing emission, performance and equipment
attributes do not preserve this measurement's exact meaning.

### Consequences

- This modeling package adds the `Acoustics` category.
- This modeling package adds the `dB` unit.
- This modeling package adds the active decimal attribute
  `noise_level_at_50_kmh`.
- No configuration value, availability record or price is introduced by the
  modeling package.
- The next source-backed package imports seven dated values of `67`, one for
  each current configuration.
- The future import preserves page 6, the observation date and the exact source
  wording.
- No interior/exterior location, acoustic weighting or test procedure is
  inferred.

## D-021 — Source-stated maximum payload

Status: Accepted

Date: 2026-07-14

### Decision

The explicit page-5 source field `Maksymalna Ładowność (Kg)` is represented
by the active integer attribute `maximum_payload` in the existing `Weights`
category. The attribute uses the `kg` unit backed by the existing `mass_kg`
unit-catalogue entry.

Maximum payload is stored as a source-stated configuration observation. It is
not calculated from `gross_vehicle_weight - kerb_weight`, even when the source
figures appear arithmetically consistent. Source definitions, rounding,
equipment assumptions and option treatment may differ, so the explicit source
value remains the authoritative fact.

`maximum_payload` is separate from:

- `kerb_weight`,
- `gross_vehicle_weight`,
- `gross_train_weight`,
- `roof_load`,
- `braked_trailer_weight`,
- `unbraked_trailer_weight`,
- tow-ball or other local load limits.

A future source-data import stores the numeric payload value in
`configuration_attribute_values.csv`, leaves fuel context empty, and preserves
the observation date, page 5, the `Dopuszczalna masa całkowita` section and the
exact Polish field in `notes`.

### Current source coverage

All seven reviewed Sandero and Sandero Stepway configuration PDFs contain the
explicit page-5 field `Maksymalna Ładowność (Kg)` under
`Dopuszczalna masa całkowita`. The values vary by configuration.

The attribute catalogue already contains kerb weight, gross vehicle weight,
gross train weight, roof load and trailer-weight concepts, but none represents
the source-stated maximum payload. No current configuration value uses
`maximum_payload`.

### Consequences

- This modeling package adds the active integer attribute `maximum_payload`.
- The existing `Weights` category and `kg` unit are reused.
- No category, unit, configuration value, availability record or price is
  introduced by the modeling package.
- Existing mass observations are not rewritten or used to derive payload.
- The next source-backed package imports seven dated payload values, one for
  each current configuration.
- The future import preserves page 5, section, observation date and exact
  source wording.

## D-022 — Source-stated total engine valve count

Status: Accepted

Date: 2026-07-15

### Decision

The explicit page-6 source field `Liczba Zaworów 12` is represented by the
active integer attribute `total_valve_count` in the existing `Engine` category.
The attribute has no unit because it stores a count.

`total_valve_count` preserves the source-stated total number of engine valves.
It is separate from:

- `valves_per_cylinder`, which stores a count for one cylinder,
- `cylinder_count`, which stores the number of engine cylinders,
- power, torque, displacement and other engine observations.

The per-cylinder valve count must not be calculated by dividing the source
total by `cylinder_count`, even when the current source values make that
arithmetic possible. The explicit total and any future explicit per-cylinder
value remain separate facts with their own provenance.

A future source-data import stores the numeric value `12` in
`configuration_attribute_values.csv`, leaves fuel context empty, and preserves
the observation date, page 6, the `Silnik` section and the exact Polish field in
`notes`.

### Current source coverage

All seven reviewed Sandero and Sandero Stepway configuration PDFs contain the
same page-6 field under `Silnik`:

`Liczba Zaworów 12`

The attribute catalogue already contains `valves_per_cylinder` and
`cylinder_count`, but neither represents the source-stated total valve count.
No current configuration value uses `total_valve_count`.

### Consequences

- This modeling package adds the active integer attribute
  `total_valve_count`.
- The existing `Engine` category is reused and no unit is added.
- No configuration value, availability record, price or source relationship is
  introduced or changed by the modeling package.
- Existing cylinder, power and torque observations are not rewritten or used
  to derive a per-cylinder valve count.
- The next source-backed package imports seven dated values of `12`, one for
  each current configuration.
- The future import preserves page 6, section, observation date and exact
  source wording.

## D-023 — Contextual cargo-volume observations

Status: Accepted

Date: 2026-07-25

### Decision

Context-rich luggage-capacity observations remain numeric configuration values in
`configuration_attribute_values.csv`. New brochure imports use the existing neutral
`boot_capacity` attribute rather than creating further attribute codes that embed VDA,
seat, spare-wheel, floor or compartment qualifiers.

A follow-up schema package shall add an optional one-to-one relation named
`configuration_cargo_volume_contexts.csv`. Each row shall reference exactly one
`configuration_attribute_values.code` through
`configuration_attribute_value_code`. A value may have zero or one cargo-context row;
a context row without its referenced value is invalid.

The planned relation shall contain:

- `id`;
- `code`;
- `configuration_attribute_value_code`;
- required `measurement_basis_code`;
- optional `second_row_state_code`;
- optional `third_row_state_code`;
- required `compartment_code`;
- optional `spare_wheel_state_code`;
- optional `tyre_repair_kit_state_code`;
- optional `double_floor_state_code`;
- `notes`.

The schema shall use controlled dictionaries for:

- measurement basis: `vda_iso_3832` and `ordinary_litre`;
- seat-row state: `upright`, `folded`, `removed` and
  `folded_or_removed` when the source explicitly groups those alternatives;
- compartment: `main_luggage_compartment`, `underfloor_compartment` and
  `source_stated_total`;
- presence state: `present` and `absent`.

Empty optional context fields mean that the source did not qualify that dimension. They
must not be interpreted as `absent`, `unknown` or a default state. Spare-wheel,
tyre-repair-kit and double-floor states are independent facts and must not be inferred
from one another.

Passenger layout and drive type are stable properties of the target configuration and
shall not be duplicated in the cargo-context relation. A brochure value split by five
or seven seats, or by 4x2 or 4x4, may be imported only into exact configurations whose
canonical seat count and drive data match the source group. If an exact target is not
modeled, the value remains unimported.

The `boot_capacity` unit remains litres. A VDA figure stated in cubic decimetres may be
stored at the numerically identical litre value because one cubic decimetre equals one
litre, while `measurement_basis_code = vda_iso_3832` and source notes preserve the
measurement method and original wording.

Minimum and maximum cargo capacities are not separate future attributes. They are
observations of the same `boot_capacity` fact under different explicit seat-row,
compartment and equipment states. Separate underfloor capacity is a separate value row
with `compartment_code = underfloor_compartment`; it must not be added to a main or
total value unless the source explicitly supplies that total.

### Existing data

Existing observations and attributes that encode historical cargo qualifiers remain
unchanged, including:

- `cargo_volume_vda`;
- `cargo_volume_vda_to_luggage_cover`;
- `cargo_volume_vda_to_seatback`;
- `cargo_volume_without_spare_wheel_iso3832`;
- `maximum_cargo_volume_iso3832`.

They are not migrated or reinterpreted by this modeling package. New context-rich
brochure imports shall use `boot_capacity` plus the accepted context relation after the
schema, validators, SQLite export and reporting surfaces support it.

### Reporting and uniqueness

Context-distinct `boot_capacity` rows must not be collapsed into one scalar or selected
arbitrarily. Reporting shall either require an explicit cargo context or expose all
source-backed contexts. The follow-up schema package shall validate one-to-one context
cardinality, controlled references and cargo-attribute eligibility before any brochure
cargo values are imported.

### Scope boundary

This decision does not import cargo values and does not modify current master-data
schemas. Gear-specific 80–120 km/h elasticity remains a separate future modeling
question; no generic all-purpose measurement-context architecture is introduced here.

## D-024 — Observation-level selected-gear context

Status: Accepted
Date: 2026-07-26

### Decision

Gear-qualified performance observations remain numeric rows in
`configuration_attribute_values.csv` and reuse the neutral
`elasticity_80_120` attribute. The follow-up schema package shall add one
optional `gear_number` column after `fuel_type_code` and before `value`.

`gear_number` stores a canonical positive integer only when the source
explicitly qualifies the observation by one selected forward gear. Examples
include `4`, `5` and `6`. An empty field means that the source does not state a
selected-gear qualifier. It must not be interpreted as `unknown`, all gears,
top gear, the highest available gear or not applicable.

The existing observation and configuration dimensions remain authoritative:

- the 80–120 km/h speed interval is part of the canonical attribute meaning;
- LPG and petrol alternatives use the existing observation-level
  `fuel_type_code` from D-014;
- five- and seven-seat distinctions target exact configurations and reuse
  canonical `number_of_seats` data;
- powertrain and transmission are properties of the exact target
  configuration.

These dimensions shall not be duplicated in a new context relation or in
additional columns.

### Evidence

The reviewed official brochure tables contain:

- Sandero page 17: fourth- and fifth-gear elasticity, including separate LPG
  and petrol values for Eco-G 120;
- Sandero Stepway page 17: fourth-, fifth- and sixth-gear elasticity where
  stated, including separate LPG and petrol values;
- Jogger page 19: fourth-gear elasticity separated by exact five- and
  seven-seat variants and by fuel where the powertrain is bi-fuel.

The source may explicitly name a gear for an automatic transmission. Such a
value may use `gear_number` exactly as stated. Missing gear values are not
inferred from `gear_count`, transmission type or neighbouring table rows.

### Validation and reporting

The schema foundation shall enforce that:

- `gear_number` is empty or a canonical positive integer;
- a populated value is permitted only for an explicitly eligible performance
  attribute, initially `elasticity_80_120`;
- gear-distinct observations may share configuration, attribute, fuel, date
  and source;
- two rows with the same complete observation identity and date remain a
  semantic collision;
- latest-value selection, comparisons, shortlist exports and data products
  include `gear_number` in the technical observation key.

Existing values remain unchanged. During schema migration they receive an
empty `gear_number` unless their current source-backed meaning already
contains an explicitly modeled selected gear in a future reviewed import.

### Rejected alternatives

- Gear-specific attribute codes such as `elasticity_80_120_4th_gear` would
  duplicate one fact and fragment comparisons.
- A separate one-to-one context relation is disproportionate for one scalar
  qualifier already analogous to observation-level fuel context.
- A generic key-value measurement-context table would be untyped and is not
  justified by the reviewed evidence.
- Passenger layout, fuel, powertrain and transmission must not be duplicated
  because the current model already represents them.

### Scope boundary

This decision imports no elasticity values and changes no master-data schema.
Cargo measurement context remains governed independently by D-023. The next
package implements the optional column, validation, import-spec, SQLite,
data-dictionary and reporting support before any brochure performance values
are imported.

---

## D-016 — Brochure chassis measurement context

Status: Accepted

Date: 2026-07-26

### Decision

Basis-qualified brochure chassis measurements use separate, unambiguous
attributes instead of a new generic context table:

- `turning_circle_between_kerbs` stores a turning-circle diameter explicitly
  measured between kerbs;
- `turning_circle_wheel_track` stores a turning-circle diameter explicitly
  stated using the wheel-track basis;
- `maximum_kerb_weight` stores an explicitly maximum-qualified kerb mass and
  remains distinct from `minimum_kerb_weight` and unqualified `kerb_weight`;
- `payload` stores a neutral source-stated payload. A single value is written
  to `configuration_attribute_values.csv`; a bounded interval is written to
  `configuration_attribute_value_ranges.csv` without flattening. The existing
  `maximum_payload` remains reserved for an explicitly stated maximum.

Compound tyre, suspension, brake and steering specifications reuse the
existing string attributes `standard_tyre_specification`, `front_suspension`,
`rear_suspension`, `front_brake_type`, `rear_brake_type` and `steering_type`.
The complete source wording is preserved rather than decomposed without
controlled dictionaries.

The legacy `turning_circle` attribute remains active for existing observations
whose measurement basis was not modeled. New basis-qualified brochure evidence
must use one of the two dedicated attributes.

Model-wide or powertrain-wide evidence may be projected to exact active
configurations only when the source scope maps unambiguously. Ambiguous or
physically inconsistent source labels are not semantically reassigned without
corrected official evidence.

### Rationale

The reviewed brochures use at least two materially different turning-diameter
bases. They also distinguish minimum and maximum kerb mass and sometimes state
payload as an interval. Folding these observations into existing context-free
or maximum-only attributes would lose source meaning. A dedicated generic
context table would be disproportionate to the current evidence and would
require broad changes to validators, reporting, exports and comparisons.

### Consequences

- Four attributes are added without introducing a new table.
- Turning-circle values with different bases remain directly comparable only
  within the same attribute.
- Payload intervals reuse the existing range infrastructure.
- Existing source-text specification attributes remain canonical.
- The Jogger mass-table label conflict remains blocked until corrected official
  evidence is available.

## D-ACC-001 — Accelerated milestone closure mode

Status: Accepted

Date: 2026-08-01

### Decision

The project may use `accelerated_milestone_closure` for a bounded milestone or release when the remaining backlog is known and logically related.

The mode uses focused tests during implementation, batches mechanical snapshot and counter repairs, opens the Pull Request after branch stabilization when practical, and runs the complete required quality matrix once on the final Pull Request head.

Closely related sources may be combined only into one explicit closure package. Exact evidence boundaries remain unchanged.

For releases, publication may be completed by one post-merge workflow that builds twice from the exact merge SHA, verifies byte identity and the offline workspace, publishes immutable assets, records the result and removes itself.

### Rationale

Repeated full-matrix runs and repeated Pull Request setup after every small deterministic correction consumed substantial time without adding proportional safety. The repository already provides focused contracts, deterministic generators, a final cross-platform matrix and exact release verification.

### Consequences

- one logical package still maps to one Pull Request;
- final complete quality is mandatory;
- stale or unverified SHAs cannot be merged or published;
- evidence may not be inferred or transferred across scope boundaries;
- public releases remain immutable;
- the canonical execution policy is stored in `project/state.json`;
- detailed rules are stored in `project/ACCELERATED_MILESTONE_CLOSURE.md`.


---

## D-017 — Fail-fast package data integrity gates

Status: Accepted

Date: 2026-11-12

### Decision

Every candidate package must run a read-only data preflight before publication. The preflight validates every repository CSV under `data/` using the canonical strict CSV validator and parses every JSON file under `data/`. The standard Quality workflow runs this check before compilation and tests.

CSV files must be written with Python's standard `csv` module (or an equivalent standards-compliant serializer), never by manually concatenating fields. Fields containing delimiters, quotes or line breaks must be quoted and escaped by the serializer.

The full repository validators remain responsible for semantic checks such as identifiers, uniqueness, references, domain rules and cross-file consistency. The package preflight does not replace them.

### Rationale

Recent CI failures were caused by unquoted commas in CSV notes and by dependent reports not being updated after their source records changed. A fail-fast structural check catches malformed CSV and JSON before the expensive full quality matrix. Reusing the canonical CSV validator avoids a competing parser or divergent CSV rules.

### Consequences

- `python tools/dkb.py package-preflight` is available for local or candidate-branch checks;
- the Quality workflow executes it on every supported matrix job;
- malformed CSV row widths, quoting and invalid JSON block the quality run;
- generated reports and documentation must still be refreshed and checked through their canonical generators;
- source-to-master fidelity and exact-head CI remain separate mandatory gates.


## D-025 — Semantic source-verification test contracts

Status: Accepted

Date: 2026-11-15

### Decision

Automated tests shall validate stable, source-backed facts and canonical structured fields rather than incidental explanatory prose. Exact string assertions are permitted only for controlled identifiers, fixed protocol literals, or text whose exact wording is itself the requirement.

Source-verification tests shall prefer the canonical fields already present in the repository schema. They must validate applicable integrity and provenance evidence (including source identity, SHA-256, byte size, page count, markers, archive location and manifest linkage) without inventing duplicate metadata fields. Where a required fact exists only in free text, tests shall use narrow semantic checks until a separately reviewed schema change makes the fact structured.

Tests shall prove both sides of the contract: editorial wording may change without invalidating unchanged facts, while missing, malformed or contradictory source evidence must fail. A failing assertion must be traced to its producer and authoritative data before expectations are changed.

### Rationale

The Bigster MY26 source-archive closure exposed a brittle test that required one exact sentence in a source notes field. The source verification itself was correct; the assertion failed after the explanatory wording was improved. The same root cause failed three Python matrix jobs and delayed an otherwise valid package.

### Consequences

- Source-verification tests distinguish semantic facts from presentation text.
- Positive and negative regression cases are required for source integrity contracts.
- Cross-version failures sharing one assertion are reported as one root cause.
- `package-preflight` validates CSV/JSON structure and verified archive-manifest integrity; it is not represented as a complete source-fidelity validator.
- Source/schema/importer/test changes require focused regression checks and final full quality on the exact PR head.
- No canonical source metadata fields are added by this decision; schema changes require evidence and a separate implementation package.

## D-026 — Single-maintainer technical review in place of independent approval

Status: Accepted

Date: 2026-11-15

### Decision

The repository is maintained by one project owner. An independent approving GitHub review is not required when no other reviewer with write access is available. Before every merge, the AI maintainer performs a technical review of the complete diff, source evidence, package scope, exact head SHA, target-branch freshness, conflicts, tests, generated artifacts, project state and required CI results.

The following six status checks remain mandatory and must pass on the exact current PR head:

- Python 3.10;
- Python 3.13;
- Python 3.14;
- Package workflow / Windows;
- Generated documentation / documentation-baseline --check;
- Repository state / project-state --check.

This decision removes only the independent-approval prerequisite. It does not permit bypassing status checks, merging stale or conflicting branches, weakening source evidence, or ignoring repository policy. A changed head invalidates prior exact-head validation; a failed or missing required check blocks merge.

### Rationale

The project has a single owner and no second reviewer with write access. Requiring an independent GitHub approval made otherwise fully validated Pull Requests unmergeable, while the AI maintainer can perform the substantive technical review. The six automated checks provide the mandatory reproducible quality gate; the pre-merge technical review addresses correctness, source fidelity and scope.

### Consequences

- The AI maintainer records a technical review before each merge.
- Independent approving reviews are not required for the single-maintainer workflow.
- All six required CI checks remain enabled and mandatory.
- Exact-head, freshness, conflict and post-merge verification remain mandatory.
- This decision does not authorize automatic merging when any check or review condition is unresolved.



## D-027 — Unified fail-closed package consistency gate

Status: Accepted

Date: 2026-11-16

### Decision

Every Pull Request must pass a unified, read-only repository-consistency gate on one exact candidate commit. The existing required status context `Repository state / project-state --check` runs, in order:

1. `python tools/dkb.py package-preflight`;
2. `python tools/dkb.py project-state --check`;
3. `python tools/dkb.py documentation-baseline --check`.

The separately required generated-documentation check remains enabled. The three subchecks are also executed inside the required repository-state job so that this required context cannot pass while data structure, canonical state or managed documentation is stale.

### Rationale

A recent source-data package exposed that structurally valid imported rows can coexist with stale canonical counters and generated documentation. The individual validators already existed, but the required repository-state context did not combine them into one explicit fail-closed package gate. Running them sequentially on the same checked-out candidate makes the consistency boundary visible and blocks a merge when any layer is stale.

### Consequences

- malformed repository CSV/JSON or source-capture manifest integrity failures block the repository-state required check;
- stale `state.json`, references or generated state summary block the same check;
- stale managed documentation baseline blocks the same check;
- CI performs checks only and never mutates candidate files;
- repairs use canonical generators, are reviewed in the complete diff, and require all three checks to pass again on the final candidate;
- the six existing required status-check names remain unchanged;
- importer idempotency, source-to-master fidelity, full quality and exact-head technical review remain separate mandatory controls.

This decision strengthens technical consistency enforcement; it does not claim that automated structural checks can resolve ambiguous documentary evidence or replace independent source review.


## D-028 — GitHub runtime repository metadata guard

Status: Accepted

Date: 2026-11-17

### Decision

The canonical project-state check must fail when the repository identity or
default-branch metadata recorded in `project/state.json` conflicts with the
GitHub Actions execution context.

The validator checks, when supplied:

- `DKB_EXPECTED_REPOSITORY` or `GITHUB_REPOSITORY` against
  `state.repository.full_name` (case-insensitively);
- `DKB_EXPECTED_DEFAULT_BRANCH` against
  `state.repository.default_branch`;
- `DKB_EXPECTED_BASE_BRANCH` or `GITHUB_BASE_REF` against the canonical
  default branch, preventing a Pull Request targeting a non-default branch
  from silently passing the project-state gate.

The Quality Linux/Python matrix and required Windows package-workflow job
must pass the expected repository, default branch and Pull Request base branch
into the validator. Outside GitHub Actions, absent runtime metadata remains
optional so local project checks continue to work.

The check runs before baseline collection and before either read-only
validation or state synchronization. It must not mutate state or infer the
repository identity from a local directory name.

### Rationale

A valid-looking state file can be copied to another repository or retain a
stale default-branch declaration. A Pull Request can also target a branch other
than the canonical default branch. Without checking the live GitHub context,
all ordinary state and documentation checks may pass against the wrong
repository or target.

### Consequences

- Repository identity, default-branch and Pull Request-target mismatches fail
  closed with actionable errors.
- Positive and negative contract tests cover matching, mismatched and absent
  GitHub metadata, including native GitHub environment-variable fallbacks.
- Local execution remains supported when no GitHub context is present.
- The six existing required status-check names remain unchanged.
- The guard supplements, and does not replace, package preflight, generated
  documentation checks, exact-head CI or technical review.

## D-029 — Canonical package lifecycle identity invariants

Status: Accepted

Date: 2026-11-17

### Decision

The canonical `current_package` and `next_package` objects in
`project/state.json` must each carry a non-empty stable `package_id` and
`kind`, in addition to the existing name, status and goal fields. Their
identifiers must differ, and `next_package.status` must not be `complete`.

These are repository-state invariants and apply to every candidate tree. They
do not require every Pull Request to claim ownership of the current package.
Documentation-only, tooling, CI, and governance maintenance PRs may leave the
current/next package selector unchanged when they do not complete or redefine
the selected package.

A package implementation PR must still update canonical state and generated
summary in the same logical package change when its completion changes the
current or next package selection. Any stronger PR-to-package binding must be
opt-in and scoped to explicitly declared package PRs; it must not be a global
requirement for every pull_request event.

### Rationale

Stable IDs prevent accidental repetition and allow exact package reconciliation.
Rejecting a completed next package catches stale selectors. However, requiring
every maintenance PR to mark itself as the completed current package conflates
repository maintenance with domain-package completion and blocks valid
infrastructure/documentation work.

### Consequences

- The existing `project-state --check` command enforces the identity,
  uniqueness and next-status invariants.
- Positive and negative contract tests cover valid selectors, missing IDs,
  duplicate IDs and a completed next package.
- No PR number is required in `current_package` merely because a PR exists.
- Generated `STATE_SUMMARY.md` continues to derive from canonical
  `state.json`; no hand-edited state summary is permitted.
- The six existing required CI status-check names remain unchanged.


## D-030 — Analytical report provenance and freshness

Status: Accepted

Date: 2026-11-17

### Decision

New and materially refreshed analytical reports must carry exact repository and input provenance, explicit freshness status, scope and stable finding lifecycle states. A report is current only after its input identities, scope, findings and JSON/Markdown parity have been revalidated. Historical reports remain immutable historical evidence and must not be presented as current.

A prior open finding must be rechecked before it is carried into a successor report. A resolved finding may be reopened only on new contradictory evidence. Input hashes are necessary but do not by themselves prove that source interpretation or scope remains valid.

### Rationale

Reports had become stale after later source archival and master-data imports without any automatic indication that their conclusions needed review. Exact provenance and explicit finding states prevent historical limitations from silently becoming current project blockers.

### Consequences

- `project/REPORT_FRESHNESS_STANDARD.md` defines the report contract.
- Existing reports remain legacy until reviewed; no bulk migration is implied.
- Automated freshness validation must be implemented with positive, negative, legacy and tampering tests before it becomes a required CI gate.
- Historical reports are preserved; refreshed analyses receive versioned successor identities.


## D-031 — Enforce analytical report provenance in CI

Status: Accepted

Date: 2026-11-17

### Decision

Use `data/reporting/report_registry.json` as the explicit inventory of governed analytical reports and run the report freshness validator in the required Quality workflow. New registry entries fail closed unless they carry the provenance contract. Legacy reports remain readable only through an explicit legacy marker and cannot claim current status. Validate safe paths, required metadata, exact input Git blob SHA-1 and SHA-256, finding lifecycle/evidence metadata and JSON/Markdown parity.

### Rationale

A written standard alone does not prevent a stale report from being merged. A deterministic validator and required CI gate make the contract executable while avoiding an unsafe bulk migration of historical analytical artifacts.

### Consequences

- `python tools/dkb.py report-freshness` is the canonical local check.
- The required Quality workflow runs the same command after package preflight.
- New reports must be registered; legacy exceptions must be explicit and cannot be current.
- The validator checks byte-level input identity but does not replace human/source review of scope or interpretation.

## D-032 — Reuse existing total and filling capacity attributes

Status: Accepted

Date: 2026-11-18

### Decision

Do not add generic `fuel_tank_capacity_total` or `fuel_tank_capacity_usable` attributes. The canonical catalogue already has distinct, source-linked fields for the relevant LPG semantics:

- `lpg_vessel_capacity_total` (ID 362) — total internal capacity of the LPG pressure vessel;
- `lpg_vessel_filling_capacity` (ID 363) — source-stated LPG volume available or permitted for filling, distinct from total vessel capacity;
- `fuel_tank_capacity` (ID 128) — generic fuel-tank capacity where the source supplies one undivided value.

For a bi-fuel configuration, use the existing `fuel_type_code` context when the source explicitly distinguishes petrol and LPG. When the source states both total LPG vessel capacity and filling capacity, populate the two LPG-specific attributes. When it supplies only one undivided capacity, retain the generic attribute with the applicable fuel context. Do not derive one value from the other.

Do not transfer a capacity value between models, powertrains or configurations based only on a shared engine label. Exact source applicability is required. A source that says only “LPG tank capacity” without establishing whether the number is total or fillable must remain unclassified between the two LPG-specific attributes.

### Rationale

A repository audit found that the model already contains separate LPG total-vessel and filling-capacity attributes, and the Jogger MY26 2026-04-01 cennik import already uses them for the explicit source wording “LPG całkowita pojemność/pojemność napełniania: 50/40”. Adding generic total/usable fields would duplicate these semantics and create competing representations for the same LPG facts.

The accepted requirement is therefore met by reusing the existing canonical attributes, not by extending the schema. The original proposal to add two generic attributes is superseded by this evidence-based refinement.

### Consequences

- No new master attributes, tables or observation columns are introduced.
- Existing Jogger LPG observations (50 L total and 40 L filling capacity) remain unchanged.
- Petrol capacity observations remain separate through `fuel_type_code` where explicitly stated.
- Sandero/Sandero Stepway LPG capacity remains deferred unless its own cennik clearly identifies total versus filling capacity and exact configuration applicability.
- No capacity is inferred from the Jogger cennik for Sandero or another model.
- Contract tests protect the existing attribute definitions and the exact source-backed Jogger import semantics.



## D-033 — Fail-closed protected-main merge diagnosis

Status: Accepted

Date: 2026-11-21

### Decision

The `main` branch protection and all six required status checks are safety controls and must not be disabled, bypassed or weakened to resolve a blocked Pull Request. A merge attempt must be based on a freshly verified PR head SHA and target-branch SHA, with all required checks successful on that exact head and the branch satisfying the configured freshness rule.

GitHub Actions check runs, classic commit statuses and required branch-protection status contexts are distinct evidence surfaces. A successful check run does not, by itself, prove that GitHub recognizes the corresponding required status context. Merge rejection diagnostics must capture the exact GitHub error, HTTP status, PR/target SHAs, required context names, exact-head conclusions, source GitHub App where available, classic statuses and branch freshness. An inaccessible protection endpoint must be reported as an access limitation.

A merge rejection must be classified before any retry or configuration change. Stale-branch remediation requires updating the branch and rerunning the complete required quality matrix on the new exact head. Context/App mismatch requires administrator-level diagnosis or correction while preserving all six required checks. If the cause remains unknown, the PR stays unmerged.

Any temporary protection adjustment requires explicit Project Owner approval, a demonstrated root cause, narrow reversible scope, a rollback plan and post-change verification. Disabling all protection is not an acceptable routine workaround.

### Rationale

In November 2026, several PRs showed successful GitHub Actions check runs for all six required names, yet GitHub rejected merge with HTTP 405 and reported that six required status checks were expected. The owner-provided branch-protection screenshot confirmed that all six checks were selected under GitHub Actions and that requiring branches to be up to date was enabled. The available connector could not read the protection endpoint (403). A PR branch being behind `main` was also observed, but this alone does not establish the cause of the required-status rejection. The evidence therefore demonstrates a mismatch between observed check-run success and merge enforcement, while the precise underlying mechanism remains unresolved.

### Consequences

- The exact-head, exact-context merge diagnostic is mandatory.
- The six required status checks remain unchanged and mandatory.
- Repeated merge attempts on an unchanged head are prohibited after a deterministic policy rejection.
- Stale-branch updates invalidate prior head validation and require a fresh complete quality matrix.
- Protection changes require explicit approval and a rollback/verification record.
- Unknown merge blockers remain blocked; no speculative bypass is permitted.
- Operational steps are defined in `project/AUTONOMOUS_MAINTAINER.md` and `project/WORKFLOW_PROFILES.md`.


## D-034 — Isolated automatic write-back for canonical baseline repair

Status: Accepted

Date: 2026-11-24

### Decision

The canonical Baseline Repair workflow shall automatically apply its generated six-file artifact to the exact target PR branch after a successful generation. The workflow must use two isolated jobs: a read-only generation job that executes the repository's canonical generators, and a write-back job that receives the minimum write permissions only after generation succeeds.

The write-back job must re-verify that the target is the same open, same-repository PR against `main`, with the exact branch, head SHA and current `main` base SHA captured before generation. It must reject missing/extra artifact paths and symbolic links, stage only the six explicit generated files, use a normal non-force push, and fail closed on branch races or target-branch drift. It must not execute code from the PR branch while write credentials are available.

After a successful write-back, it must explicitly dispatch the required Quality and Repository Baselines workflows on the updated PR branch. A green result on the pre-repair SHA is never sufficient; all six required checks must pass on the post-repair exact head.

### Rationale

The previous read-only workflow generated the correct artifact but required a separate manual download and branch update. The connector could retrieve an artifact reference without making the ZIP contents available to the Git write workflow, creating an avoidable user handoff and delaying validation. A two-job workflow closes that gap while keeping untrusted PR code outside the write-permission job.

### Consequences

- The Project Owner does not manually download, extract or upload the artifact.
- Write permissions are isolated to the artifact validation and branch update job.
- The exact six-file allowlist and immutable-head checks remain mandatory.
- Force-push and writes to `main` are prohibited.
- CI is explicitly dispatched after the write-back and must be reviewed on the resulting exact PR SHA.
- A stale PR, branch race, malformed artifact or unexpected path fails closed and leaves the PR unmerged.


## D-035 — Owner-defined interpretation of equipment and commercial matrix symbols

Status: Accepted

Date: 2026-11-24

### Decision

For the official Polish Striker MY26 cennik effective 2026-11-02, the Project Owner explicitly defines the printed matrix symbols as follows:

- `●` — present / included as standard (`standard`);
- `-` — absent / unavailable for the configuration (`not_available`);
- `o` — selectable paid option (`optional`);
- `P` — available as part of a package (`package`).

This owner-supplied interpretation is authoritative for the Striker MY26 matrix even though the cennik itself contains no legend defining `P`. It supersedes the provisional `unknown` classification for the seven literal P mappings in the Striker heated-washer-nozzles/windscreen commercial-item row. Preserve the raw symbol and page-level source wording in notes.

The `package` status means only that the item is available through a package. It does not identify which named package contains the item, establish a standalone price, or authorize creation of a package-component relationship. Those facts must remain unassigned unless a source explicitly links them.

When another source provides its own explicit legend, apply that source's legend for that source edition. Do not silently generalize this owner clarification to unrelated markets, model years or source formats without confirming that the same symbol convention applies.

### Rationale

The Project Owner supplied an explicit interpretation to resolve the previously retained P markers. A distinct controlled status preserves the difference between a paid standalone option and an item available through a package, while avoiding unsupported identification of the package itself.

### Consequences

- Add `package` to the shared equipment-availability status dictionary used by equipment and commercial-item configuration relations.
- Reclassify the seven Striker MY26 P mappings from `unknown` to `package` in both the import specification and master data.
- Keep their amounts empty; retain the three Journey mappings as `optional` at 1,000 PLN and the Essential dash as `not_available`.
- Update the importer, regression tests, source report and project documentation.
- Do not add equipment-component rows or infer a specific named package for the heated washer nozzles/windscreen item.
