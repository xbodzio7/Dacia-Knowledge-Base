\# DATA SCHEMA



\## Cel



Niniejszy dokument opisuje fizyczną organizację danych w Dacia Knowledge Base.



Stanowi uzupełnienie dokumentu `DATA\_MODEL.md`, który opisuje model logiczny.



\---



\# Zasady ogólne



\- Dane przechowywane są w formacie CSV.

\- Jeden plik odpowiada jednej encji lub jednemu słownikowi.

\- Nazwy plików zapisujemy w `snake\_case`.

\- Kodowanie: UTF-8.

\- Separator: przecinek (`,`).

\- Pierwszy wiersz zawiera nagłówki.



\---



\# Identyfikatory



Każdy rekord powinien posiadać:



\- techniczny identyfikator (`id`),

\- stabilny identyfikator biznesowy (`code`), jeśli ma zastosowanie.



Identyfikatory techniczne nie powinny być wykorzystywane jako dane referencyjne poza repozytorium.



\---



\# Klucze



Relacje pomiędzy encjami realizowane są przy użyciu stabilnych identyfikatorów biznesowych.



\---



\# Nazewnictwo



Nazwy plików:



\- małe litery,

\- `snake\_case`.



Nazwy kolumn:



\- małe litery,

\- `snake\_case`,

\- liczba pojedyncza.



Przykład:



```text

model\_code

engine\_code

attribute\_code

version\_code

```



\---



\# Typy danych



Preferowane typy:



\- string

\- integer

\- decimal

\- boolean

\- date



Jednostki (np. mm, kg, kW) powinny być przechowywane jako dane, a nie część nazwy kolumny.



\---



\# Wersjonowanie



Zmiany schematu powinny być kompatybilne wstecz, jeśli to możliwe.



Zmiany niekompatybilne wymagają odpowiedniej decyzji projektowej i aktualizacji dokumentacji.



\---



\# Zakres



Dokument opisuje wyłącznie sposób przechowywania danych.



Nie opisuje modelu logicznego ani procesu importu danych.

## Fuel-tank capacity semantics

The existing master attribute catalogue already distinguishes:

- `fuel_tank_capacity` — one undivided fuel-tank capacity value;
- `lpg_vessel_capacity_total` — total internal LPG pressure-vessel capacity;
- `lpg_vessel_filling_capacity` — source-stated LPG volume available or permitted for filling, distinct from total vessel capacity.

For bi-fuel configurations, use the existing `fuel_type_code` observation context only when the source identifies the fuel. Use the two LPG-specific attributes only when the source explicitly distinguishes total and filling capacity. Do not infer either value from the other or transfer values between models. See D-032 in `DECISIONS.md`.


## Equipment and commercial availability statuses

The shared dictionary `data/master/enums/equipment_availability_statuses.csv` defines the statuses used by configuration equipment availability and commercial-item configuration mappings:

- `standard` — present as standard equipment;
- `optional` — available as a separately selectable paid option;
- `not_available` — explicitly absent or unavailable for the configuration;
- `package` — available only as part of a package; the specific package may remain unidentified;
- `unknown` — the source does not permit a reliable classification.

A `package` status does not by itself create a package-component relationship or identify the package. Preserve the raw source marker in notes. See D-015 and D-035 in `DECISIONS.md`.
