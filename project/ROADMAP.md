# Dacia Knowledge Base

# Roadmap

Ten dokument opisuje plan rozwoju projektu oraz jego aktualny stan.

---

# Vision

Celem projektu jest stworzenie kompletnej, weryfikowalnej bazy wiedzy dotyczącej samochodów marki Dacia.

Repozytorium ma umożliwiać:

- przechowywanie danych technicznych i handlowych,
- powiązanie danych ze źródłami,
- import danych z katalogów PDF,
- automatyczną walidację jakości i spójności,
- generowanie raportów i statystyk,
- eksport danych do SQLite i Excela,
- szybkie wyszukiwanie informacji.

---

# Current Status

## Phase

Data Expansion

## Progress

🟩 Dokumentacja projektu

🟩 Struktura repozytorium

🟩 Fundament Master Data

🟩 Tooling i automatyzacja

🟩 Walidacja i testy

🟩 Dwa źródłowe pakiety Sandero i Sandero Stepway

🟨 Rozbudowa danych opartych na źródłach

⬜ Automatyczny import PDF

⬜ Raporty i eksporty użytkowe

---

# Completed

## Documentation

- README
- START_HERE
- AI_CONTEXT
- AI_WORKING_AGREEMENT
- DECISIONS
- ROADMAP
- SESSION_STATE
- CHANGELOG

## Repository

- stabilna struktura katalogów,
- reguły ignorowania artefaktów generowanych,
- licencja,
- GitHub Actions dla kontroli jakości,
- praca na gałęziach i integracja przez Pull Request.

## Master Data

- modele, silniki, skrzynie biegów i typy nadwozia,
- relacje model–silnik i model–skrzynia,
- kategorie, domeny, jednostki i typy wartości,
- atrybuty oraz dedykowany słownik kategorii atrybutów,
- słowniki wartości enumeracyjnych,
- deklaratywne reguły walidacji,
- rejestr siedmiu oficjalnych dokumentów Sandero i Sandero Stepway,
- powiązania źródeł z modelami, wersjami i konfiguracjami,
- pięć wersji wyposażenia,
- siedem konfiguracji Eco-G 120,
- waluta PLN i siedem datowanych obserwacji cen katalogowych brutto,
- 168 datowanych obserwacji technicznych dla siedmiu konfiguracji,
- podstawowe parametry zespołu napędowego i pojemności,
- prędkość maksymalna, średnica zawracania, masy pojazdu i przyczep,
- długość, szerokość, rozstaw osi oraz zwisy,
- pojemność bagażnika VDA i w litrach z kontekstem zestawu naprawczego,
- 28 obserwacji zużycia paliwa i emisji CO2 w cyklu WLTP,
- oddzielny kontekst LPG i benzyny przez opcjonalne `fuel_type_code`,
- zakończony pakiet Fuel-mode-aware WLTP Observation Analysis,
- decyzja D-014 — Observation-level fuel context,
- zakończona analiza pokrycia siedmiu źródeł PDF,
- decyzja D-015 — Configuration-level equipment availability,
- decyzja D-016 — Configuration-level wheel and upholstery values,
- decyzja D-017 — Evidence-gated commercial packages and options,
- analiza siedmiu źródeł bez potwierdzonych nazwanych pakietów lub opcji,
- kontrolowany słownik statusów dostępności wyposażenia,
- schemat `configuration_attribute_availability.csv`,
- 42 kanoniczne atrybuty funkcjonalnego i pasywnego wyposażenia,
- 419 datowanych rekordów dostępności dla siedmiu konfiguracji,
- jawne rozróżnienie 389 pozycji `standard` i 30 `not_available`,
- jednoznaczne wyposażenie bezpieczeństwa pasywnego z zachowaną proweniencją,
- dwa kanoniczne atrybuty wartościowe `wheel_design` i `upholstery_variant`,
- 29 datowanych wartości kół i tapicerki dla siedmiu konfiguracji,
- zachowana granica konfliktu ERALIA/TAMIA BI-TON dla Stepway Essential,
- kategoria `Exterior` i kanoniczny atrybut string `exterior_color`,
- 7 datowanych wartości koloru `biel alpejska` z zachowanym zapisem `0 zł` w proweniencji,
- decyzja D-018 — axle-neutral standard tyre specification,
- analiza pozostałych wartości PDF z wyborem specyfikacji opony jako następnego importu,
- kanoniczny atrybut string `standard_tyre_specification`,
- 7 datowanych wartości `205/60 R16 92H` z zachowaną stroną i brzmieniem źródła,
- zachowana granica między pełną specyfikacją opony, osiami, indeksami maksymalnymi i rozmiarem felgi,
- ponowna analiza pozostałych jawnych wartości po imporcie specyfikacji opony,
- ręczna klasyfikacja kandydatów z odrzuceniem nagłówków, wariantów brzmienia i już pokrytych faktów,
- wybór istniejącego atrybutu `number_of_doors` dla następnego kontrolowanego importu,
- 7 datowanych wartości `number_of_doors = 5` z zachowaną stroną, sekcją i brzmieniem źródła,
- zachowana granica między całkowitą liczbą drzwi i liczbą drzwi bocznych.
- decyzja D-019 — exact emission-standard variants,
- kontrolowana wartość `euro_6e_bis` zachowująca dokładne `Euro 6e BIS`,
- zachowana granica między `Euro 6e BIS`, `Euro 6e` i poziomem hałasu 67 dB.
- 7 datowanych wartości `emission_standard = euro_6e_bis` z zachowaną stroną 6 i brzmieniem źródła,
- zachowany rozdział między normą emisji i poziomem hałasu przy 50 km/h.
- decyzja D-020 — speed-specific vehicle noise measurement,
- kategoria `Acoustics`, jednostka `dB` i atrybut decimal `noise_level_at_50_kmh`,
- zachowana granica między warunkiem 50 km/h a niepotwierdzoną lokalizacją i procedurą pomiaru.
- 7 datowanych wartości `noise_level_at_50_kmh = 67` z zachowaną stroną 6 i brzmieniem źródła,
- zachowany rozdział między pomiarem przy 50 km/h a ogólnym, wewnętrznym i zewnętrznym poziomem hałasu,
- przegląd 1371 wystąpień kandydatów po imporcie poziomu hałasu,
- ręczna klasyfikacja 1010 niedopasowanych wystąpień i odrzucenie pozycji już reprezentowanych, wyposażenia, nagłówków oraz fragmentów tabel,
- wybór istniejącego atrybutu enum `drive_type` i aktywnej wartości `fwd` dla następnego kontrolowanego importu,
- zachowana granica względem ogólniejszych atrybutów string `drive_layout` i `drivetrain_type`,
- 7 datowanych wartości `drive_type = fwd` z zachowaną stroną 5, sekcją i brzmieniem źródła,
- zachowana granica między kontrolowanym enumem `drive_type` i ogólniejszymi atrybutami string.
- decyzja D-021 — source-stated maximum payload,
- aktywny atrybut integer `maximum_payload` w kategorii `Weights` z jednostką `kg`,
- zachowana granica między jawną ładownością, masami całkowitymi, obciążeniem dachu i parametrami holowania.

## Tooling

- zunifikowany interfejs `python tools/dkb.py`,
- pełna lokalna bramka jakości `quality`,
- walidator repozytorium w wersji 0.10,
- kontrola UTF-8 i normalizacja kodowania CSV,
- walidacja struktury, unikalności, referencji, zakresów lat, statusów i okresów powiązań,
- walidacja kontraktów oraz wykonywanie deklaratywnych reguł danych,
- wyszukiwanie, statystyki i raporty Markdown,
- atomowa budowa bazy SQLite,
- weryfikacja zgodności schematu i danych SQLite z plikami CSV,
- 272 testy automatyczne,
- 34 deklarowane relacje między tabelami,
- kontrola jakości w CI na Pythonie 3.10 i 3.13,
- wersjonowany manifest pakietu z dokładną gałęzią, bazą, tematem i zakresem,
- bezpieczne dekodowanie UTF-8 oraz bajtowe listy ścieżek Git,
- polityka LF w `.gitattributes`,
- regresyjne testy workflow na Windows.

---

# Current Sprint

## Package Workflow Hardening

Cel sprintu:

- wymusić deterministyczne UTF-8 dla procesów Git i jakości,
- zachować bajtowe, NUL-separowane odczyty ścieżek,
- dodać wersjonowany manifest JSON do `package-review` i `package-finish`,
- wymagać dokładnej gałęzi, bazowego SHA i manifestu plików przed commitem,
- wymagać jednego commitu, dokładnego rodzica i zgodnego tematu po commicie,
- dodać `.gitattributes` z polityką LF,
- uruchamiać regresyjne testy workflow na Windows,
- zachować kompatybilność dotychczasowych komend bez manifestu,
- zakończyć pakiet pełną kontrolą jakości.

---

# Next Sprint

## Manifest-driven Package Publishing

Cel sprintu:

- dodać trwałą komendę `package-publish`,
- generować receipt jakości związany z hashem stanu pakietu,
- pomijać ponowną pełną jakość tylko dla niezmienionego, zweryfikowanego stanu,
- generować mały `handoff.json` obok pełnego logu,
- skrócić log sukcesu bez utraty szczegółów błędów,
- ograniczyć duplikację walidacji danych i SQLite w CI,
- po zakończeniu toolingowego usprawnienia wrócić do importu
  `maximum_payload`.

# Backlog

## Data

- pakiety i opcje po uzyskaniu źródła z jawną ofertą handlową
- dalsze techniczne wartości konfiguracji
- wyposażenie wersji i konfiguracji
- dalsze rozszerzanie pokrycia źródłami

## Import

- automatyczny potok importu PDF,
- ekstrakcja tabel i specyfikacji,
- kontrola pochodzenia danych,
- dalsze dane Sandero i Sandero Stepway,
- Duster,
- Jogger,
- Bigster,
- Spring

## Reporting

- eksport do Excela,
- raporty porównawcze modeli i wersji,
- raport kompletności danych,
- raport pokrycia źródłami.
