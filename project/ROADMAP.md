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
- wybór istniejącego atrybutu `number_of_doors` dla następnego kontrolowanego importu.

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
- 211 testów automatycznych,
- 34 deklarowane relacje między tabelami,
- kontrola jakości w CI na Pythonie 3.10 i 3.13.

---

# Current Sprint

## Sandero Remaining PDF Value Gap Reassessment

Cel sprintu:

- zweryfikować siedem źródeł PDF przez SHA-256,
- porównać źródła z 211 wartościami konfiguracji, 419 rekordami dostępności i 7 cenami,
- odrzucić nagłówki, tekst marketingowy, warianty brzmienia i fakty już reprezentowane w modelu,
- potwierdzić na stronie 5 wspólne pole `Liczba Drzwi 5`,
- potwierdzić aktywny atrybut `number_of_doors` i brak odpowiadających mu rekordów,
- nie zmieniać danych ani schematu w pakiecie analitycznym,
- wybrać jeden mały następny pakiet bez zgadywania danych.

---

# Next Sprint

## Sandero Number of Doors Value Import

Cel sprintu:

- zaimportować `number_of_doors = 5` dla siedmiu konfiguracji,
- użyć istniejącego atrybutu integer w kategorii `Doors`,
- zachować datę, źródło, stronę 5, sekcję `Typ nadwozia` i brzmienie `Liczba Drzwi 5`,
- użyć `configuration_attribute_values.csv`,
- nie zmieniać schematu, dostępności wyposażenia ani cen konfiguracji,
- dodać testy regresyjne i zakończyć pakiet pełną kontrolą jakości.

---

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
