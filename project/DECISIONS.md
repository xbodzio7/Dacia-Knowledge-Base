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
