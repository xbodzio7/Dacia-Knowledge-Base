# Session State

## Repository Status

Repozytorium pozostaje jedynym źródłem prawdy.

Gałąź `main` zawiera pakiety Sandero i Sandero Stepway zintegrowane przez
Pull Requesty #3–#18. Aktualny punkt odniesienia to merge commit
`4bb28d6`.

PR #18 zaimplementował schemat dostępności wyposażenia zgodny z D-015,
kontrolowany słownik statusów oraz pokrycie testami i SQLite.

Bieżący pakiet źródłowy jest rozwijany na gałęzi
`data/sandero-equipment-availability`.

## Verified Quality Baseline

Zweryfikowany lokalnie punkt odniesienia dla bieżącego pakietu:

```bash
python tools/dkb.py quality
```

Wynik docelowy:

- 177 testów automatycznych zakończonych powodzeniem,
- 34 pliki CSV w `data/master`,
- 1091 rekordów danych,
- 34 relacje między tabelami,
- 19 reguł statusów,
- walidator repozytorium w wersji 0.10,
- 168 obserwacji w `configuration_attribute_values.csv`,
- 300 rekordów w `configuration_attribute_availability.csv`,
- 277 rekordów `standard` i 23 rekordy `not_available`,
- 25 nowych kanonicznych atrybutów wyposażenia,
- baza SQLite obejmująca 34 tabele i 1091 rekordów,
- zgodność schematu i zawartości SQLite z plikami CSV,
- wszystkie źródłowe pliki CSV zapisane jako UTF-8.

## Current Sprint

Sandero Core Equipment Availability Source Import.

Zakres:

- weryfikacja siedmiu plików PDF przez SHA-256,
- import 300 datowanych rekordów dla siedmiu konfiguracji,
- mapowanie 52 funkcji wyposażenia na katalog atrybutów,
- dodanie 25 brakujących atrybutów typu boolean,
- 277 jawnych pozycji `standard`,
- 23 jawne pozycje `not_available`,
- zachowanie strony i źródłowego brzmienia w `notes`,
- brak wnioskowania na podstawie nieobecności pozycji,
- odłożenie wyglądu, tapicerki i pozostałego bezpieczeństwa pasywnego.

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

Schemat dostępności z PR #18 jest wypełniany pierwszym kontrolowanym
pakietem źródłowym. Import obejmuje funkcjonalne wyposażenie możliwe do
jednoznacznego powiązania z katalogiem atrybutów. Jawne negacje źródłowe są
zapisywane jako `not_available`; brak wzmianki pozostaje brakiem rekordu.

## Next Development Package

Sandero Safety and Trim Availability Import.

Planowany przebieg:

1. Przeanalizować pozostałe pozycje bezpieczeństwa pasywnego i wyglądu.
2. Oddzielić funkcje wyposażenia od wariantów stylistycznych i wartości.
3. Rozstrzygnąć sprzeczne lub redundantne opisy kół i tapicerki.
4. Nie importować wewnętrznych kryteriów zamówieniowych jako wyposażenia.
5. Dodać tylko minimalne brakujące atrybuty kanoniczne.
6. Uzupełnić istniejącą relację bez zmiany znaczenia pierwszych 300 rekordów.
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

Completed:

- PR #18: dodano kontrolowany słownik czterech statusów,
- dodano pusty schemat relacji zgodny z D-015,
- zadeklarowano cztery referencje i walidację statusów,
- dodano testy schematu oraz automatyczne pokrycie SQLite,
- GitHub Actions Quality run #64 zakończył się powodzeniem.

### Sandero Core Equipment Availability

Current package:

- zweryfikowano siedem dokumentów PDF przez SHA-256,
- przygotowano 300 rekordów dostępności dla siedmiu konfiguracji,
- wykorzystano 27 istniejących i 25 nowych atrybutów kanonicznych,
- zachowano 277 statusów `standard` i 23 jawne `not_available`,
- nie wyprowadzono żadnego statusu z samego braku wzmianki,
- wygląd, tapicerka i pozostałe bezpieczeństwo pasywne pozostają poza zakresem.

Next priority:

Źródłowe uzupełnienie pozostałych jednoznacznych pozycji bezpieczeństwa
i wyglądu po rozstrzygnięciu wariantów stylistycznych.
