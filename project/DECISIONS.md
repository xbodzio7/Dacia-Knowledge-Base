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
