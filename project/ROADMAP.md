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

🟩 Pierwszy źródłowy pakiet Sandero i Sandero Stepway

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
- 84 datowane obserwacje techniczne dla siedmiu konfiguracji,
- podstawowe parametry zespołu napędowego i pojemności,
- prędkość maksymalna, średnica zawracania, masy pojazdu i przyczep.

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
- 148 testów automatycznych,
- kontrola jakości w CI na Pythonie 3.10 i 3.13.

---

# Current Sprint

## Sandero Technical Data Documentation Sync

Cel sprintu:

- zsynchronizować README, roadmapę, stan sesji i changelog po PR-ach #8 i #9,
- zapisać punkt odniesienia: 32 pliki CSV i 678 rekordów,
- odnotować 29 relacji między tabelami oraz 32 tabele SQLite,
- udokumentować 84 datowane obserwacje techniczne,
- wyznaczyć kolejny mały pakiet danych opartych na źródłach.

---

# Next Sprint

## Source-backed Dimensions and Capacities

Cel sprintu:

- wybrać niewielki zestaw wymiarów i pojemności jednoznacznie podanych
  w zarejestrowanych dokumentach,
- mapować wartości wyłącznie do istniejących atrybutów i jednostek,
- zachować powiązanie każdej wartości z konfiguracją, źródłem i datą,
- nie rozdzielać wartości na osie ani warianty paliwa bez jednoznacznego
  potwierdzenia w źródle,
- uruchomić pełną bramkę `python tools/dkb.py quality` przed integracją zmian.

---

# Backlog

## Data

- pakiety i opcje
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
