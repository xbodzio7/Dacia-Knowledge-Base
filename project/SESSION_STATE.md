# Session State

## Repository Status

Repozytorium pozostaje jedynym źródłem prawdy.

Gałąź `main` zawiera pakiety Sandero i Sandero Stepway zintegrowane przez
Pull Requesty #3–#17. Aktualny punkt odniesienia to merge commit
`39b2c3a`.

PR #16 zakończył analizę pokrycia siedmiu źródeł PDF i zapisał decyzję
D-015. PR #17 dodał automatyzację bezpiecznego workflow pakietów oraz
poprawkę UTF-8 dla lokalnej bramki jakości na Windows.

Bieżący pakiet schematu jest rozwijany na gałęzi
`feature/equipment-availability-schema`.

## Verified Quality Baseline

Zweryfikowany lokalnie punkt odniesienia dla bieżącego pakietu:

```bash
python tools/dkb.py quality
```

Wynik docelowy:

- 169 testów automatycznych zakończonych powodzeniem,
- 34 pliki CSV w `data/master`,
- 766 rekordów danych,
- 34 relacje między tabelami,
- 19 reguł statusów,
- walidator repozytorium w wersji 0.10,
- 168 obserwacji w `configuration_attribute_values.csv`,
- zero rekordów w pustym schemacie dostępności wyposażenia,
- baza SQLite obejmująca 34 tabele i 766 rekordów,
- zgodność schematu i zawartości SQLite z plikami CSV,
- wszystkie źródłowe pliki CSV zapisane jako UTF-8.

## Current Sprint

Equipment Availability Schema Implementation.

Zakres:

- kontrolowany słownik statusów dostępności wyposażenia,
- pusty schemat `configuration_attribute_availability.csv`,
- referencje do konfiguracji, atrybutów, statusów i źródeł,
- walidacja statusów oraz automatyczna unikalność `id` i `code`,
- testy deklaracji schematu i wykrywania tabel przez SQLite,
- synchronizacja dokumentacji,
- brak importu rekordów wyposażenia z PDF.

## Current Phase

Aktualna faza to **Data Expansion**.

Pięć pakietów źródłowych danych technicznych jest zakończonych.
Tabela `configuration_attribute_values.csv` zawiera 168 datowanych
obserwacji dla siedmiu konfiguracji Sandero i Sandero Stepway.

Pierwsze 140 obserwacji jest niezależnych od rodzaju paliwa i zachowuje
puste `fuel_type_code`. Obserwacje 141–168 zapisują zużycie paliwa oraz
emisję CO2 oddzielnie dla LPG i benzyny.

Zakres obejmuje:

- pojemność zbiornika paliwa,
- pojemność skokową i liczbę cylindrów,
- liczbę miejsc i przełożeń,
- prędkość maksymalną i średnicę zawracania,
- masę własną i dopuszczalną masę całkowitą,
- dopuszczalną masę całkowitą zespołu pojazdów,
- masy przyczepy z hamulcem i bez hamulca,
- długość, szerokość, rozstaw osi oraz zwisy,
- pojemność bagażnika VDA i w litrach,
- kontekst wariantu z zestawem naprawczym,
- zużycie paliwa w cyklu mieszanym WLTP,
- emisję CO2 w cyklu mieszanym WLTP.

Opcjonalne `fuel_type_code` wskazuje na
`data/master/enums/fuel_types.csv`. Decyzja D-014 zachowuje kontekst
paliwa na poziomie obserwacji bez tworzenia paliwowych duplikatów
definicji atrybutów.

Analiza siedmiu źródeł PDF wykazała, że główne obszary danych technicznych
są już reprezentowane, natomiast wyposażenie seryjne pozostaje największym
jednoznacznym obszarem niezaimportowanym.

Porównanie konfiguracji Stepway Expression i Extreme wykazało, że
wyposażenie może zależeć od rodzaju skrzyni biegów. Decyzja D-015 przyjmuje
więc dedykowaną relację dostępności wyposażenia na poziomie konfiguracji,
z ponownym użyciem istniejącego katalogu atrybutów.

Bieżący pakiet implementuje kontrolowany słownik statusów i pustą relację
zgodną z D-015. Brak rekordu nadal oznacza brak importu, a nie status
`unknown` lub `not_available`. Wypełnienie relacji pozostaje osobnym
pakietem źródłowym.

## Next Development Package

Sandero Equipment Availability Source Import.

Planowany przebieg:

1. Odczytać wyposażenie z siedmiu zarejestrowanych źródeł PDF.
2. Powiązać pozycje z kanonicznym katalogiem atrybutów.
3. Zapisać dostępność na poziomie konfiguracji.
4. Zachować status, datę obserwacji, źródło i niezbędne uwagi.
5. Nie interpretować braku rekordu jako `unknown` lub `not_available`.
6. Nie zgadywać wyposażenia niewskazanego jednoznacznie w źródle.
7. Zakończyć pakiet pełną bramką jakości i weryfikacją SQLite.

## Working Mode

Projekt jest rozwijany w małych, kontrolowanych pakietach.

Każdy pakiet:

- rozpoczyna się od sprawdzenia gałęzi i czystości katalogu roboczego,
- obejmuje wyłącznie pliki związane z bieżącym zadaniem,
- jest przeglądany przed commitem,
- przechodzi odpowiednie testy lub pełną bramkę `quality`,
- kończy się aktualizacją dokumentacji tylko wtedy, gdy zmienia stan projektu.

Git Bash służy do generowania zmian, testów i kontroli stanu. Git GUI
może służyć do przeglądania różnic, stagingu, commitów i pushowania.

Powtarzalne kontrole pakietu są dostępne przez `package-start`,
`package-review` i `package-finish`. Commit, push, utworzenie Pull Requestu
oraz merge pozostają operacjami jawnymi.

## Project Rules

- `data/master` zawiera źródłowe dane projektu.
- Raporty, eksporty wyszukiwania i lokalne bazy SQLite są artefaktami generowanymi.
- Dane handlowe i techniczne muszą mieć datę i źródło.
- Nie należy zgadywać brakujących parametrów technicznych.
- Nie należy ponownie projektować stabilnej architektury bez wyraźnej potrzeby.
- Nie należy deklarować powodzenia CI bez sprawdzenia wyniku.
- `ROADMAP.md` definiuje fazę i kierunek rozwoju.
- `SESSION_STATE.md` opisuje bieżący kontekst roboczy i musi pozostawać
  zgodny z roadmapą.

## Sprint History

### Sprint 001 — Repository Startup Alignment

Completed:

- poprawiono lokalizację roadmapy wskazywaną przez `START_HERE`,
- procedurę rozpoczęcia pracy dopasowano do rzeczywistej struktury repozytorium.

### Tooling and Data Quality Phase

Completed:

- zunifikowany CLI,
- rozbudowany walidator danych,
- normalizacja kodowania CSV,
- wyszukiwanie, statystyki i raporty,
- bezpieczna budowa i pełna weryfikacja SQLite,
- testy regresyjne,
- lokalna bramka `quality`,
- automatyczna kontrola jakości w GitHub Actions.

### Sandero Source-backed Baseline

Completed:

- PR #3: rejestr siedmiu dokumentów i powiązania z modelami,
- PR #4: pięć wersji oraz powiązania źródło–wersja,
- PR #5: siedem konfiguracji oraz powiązania źródło–konfiguracja,
- PR #6: waluta PLN i siedem datowanych obserwacji cen,
- PR #7: synchronizacja dokumentacji bazowego pakietu danych,
- rozszerzenie walidacji referencji i statusów dla nowych tabel.

### Sandero Source-backed Technical Data

Completed:

- PR #8: 35 podstawowych obserwacji technicznych i trzy nowe relacje,
- PR #9: 49 obserwacji osiągów, mas pojazdu i mas przyczep,
- PR #10: synchronizacja dokumentacji po pierwszych dwóch pakietach,
- PR #11: 35 obserwacji długości, szerokości, rozstawu osi i zwisów,
- PR #12: 21 obserwacji pojemności bagażnika i wariantu naprawczego,
- PR #13: synchronizacja dokumentacji po pakietach wymiarów i pojemności,
- PR #14: 28 obserwacji WLTP z jawnym kontekstem LPG i benzyny,
- opcjonalne `fuel_type_code` i decyzja D-014,
- PR #15: synchronizacja dokumentacji po pakietach technicznych i WLTP,
- 168 obserwacji technicznych dla siedmiu konfiguracji,
- pełna kontrola jakości: 149 testów, 32 pliki CSV, 762 rekordy,
  30 relacji oraz 32 tabele SQLite.

### Sandero PDF Source Coverage Analysis

Completed:

- PR #16: przeanalizowano siedem zarejestrowanych źródeł PDF,
- główne dane techniczne potwierdzono jako objęte wcześniejszymi pakietami,
- wyposażenie seryjne wskazano jako największą lukę,
- różnice manual–automatic potwierdziły poziom konfiguracji,
- zaakceptowano decyzję D-015,
- oddzielono implementację schematu od importu danych.

### Package Workflow Automation

Completed:

- PR #17: dodano `package-start`, `package-review` i `package-finish`,
- zachowano jawne commit, push, PR i merge,
- dodano testy workflow izolowane od konfiguracji Git i zakończeń linii,
- wymuszono UTF-8 dla procesów lokalnej bramki jakości na Windows,
- GitHub Actions Quality run #62 zakończył się powodzeniem.

### Equipment Availability Schema

Current package:

- kontrolowany słownik czterech statusów,
- pusty schemat relacji zgodny z D-015,
- cztery deklarowane referencje,
- walidacja statusu słownika,
- testy schematu i automatyczne pokrycie SQLite,
- brak importowanych rekordów wyposażenia.

Next priority:

Źródłowy import dostępności wyposażenia Sandero i Sandero Stepway do
przygotowanego schematu.
