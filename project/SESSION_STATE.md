# Session State

## Repository Status

Repozytorium pozostaje jedynym źródłem prawdy.

Gałąź `main` zawiera pakiety Sandero i Sandero Stepway zintegrowane przez
Pull Requesty #3–#21. Aktualny punkt odniesienia to merge commit
`ba615ed0`.

PR #21 zaakceptował decyzję D-016, rozdzielił wartości kół i tapicerki oraz
udokumentował konserwatywną granicę konfliktu Stepway Essential.

Bieżący pakiet źródłowy jest rozwijany na gałęzi
`data/sandero-wheel-upholstery-values`.

## Verified Quality Baseline

Zweryfikowany lokalnie wynik docelowy bieżącego pakietu:

```bash
python tools/dkb.py quality
```

- 194 testy automatyczne zakończone powodzeniem,
- 34 pliki CSV w `data/master`,
- 1258 rekordów danych,
- 34 relacje między tabelami,
- 19 reguł statusów,
- walidator repozytorium w wersji 0.10,
- 197 obserwacji w `configuration_attribute_values.csv`,
- 419 rekordów w `configuration_attribute_availability.csv`,
- 389 rekordów `standard` i 30 rekordów `not_available`,
- 42 kanoniczne atrybuty boolean wyposażenia w dwóch pakietach,
- 2 nowe kanoniczne atrybuty string dla kół i tapicerki,
- baza SQLite obejmująca 34 tabele i 1258 rekordów,
- zgodność schematu i zawartości SQLite z plikami CSV,
- wszystkie źródłowe pliki CSV zapisane jako UTF-8.

## Current Sprint

Sandero Wheel and Upholstery Value Import.

Zakres:

- weryfikacja siedmiu źródeł PDF przez SHA-256,
- dodanie `wheel_design` i `upholstery_variant`,
- import 29 datowanych wartości dla siedmiu konfiguracji,
- 7 wartości rozmiaru, 7 materiału, 6 wzoru i 2 wykończenia kół,
- 7 nazwanych wariantów tapicerki,
- zachowanie strony, sekcji i źródłowego brzmienia w `notes`,
- brak wzoru i wykończenia dla Stepway Essential,
- brak zmian w relacji dostępności wyposażenia,
- wykluczenie wewnętrznych kryteriów zamówieniowych.

## Current Phase

Aktualna faza to **Data Expansion**.

Sześć pakietów wartości konfiguracji obejmuje 197 datowanych obserwacji dla
siedmiu konfiguracji Sandero i Sandero Stepway. Pierwsze 168 obserwacji
zachowuje dane techniczne, w tym jawny kontekst LPG i benzyny zgodnie z D-014.

Bieżący import dodaje 29 wartości kół i tapicerki zgodnie z D-016. Rozmiar,
materiał, wzór i wykończenie koła są osobnymi atrybutami, a tapicerka pozostaje
nazwanym wariantem. Dla Stepway Essential wspólną informacją źródłową jest
wyłącznie stalowy materiał obręczy; wzór i wykończenie pozostają bez rekordu.

Dwa pakiety dostępności wyposażenia pozostają bez zmian: 419 rekordów,
w tym 389 `standard` i 30 `not_available`, zgodnie z D-015. Brak rekordu nie
jest interpretowany jako niedostępność.

## Next Development Package

Sandero Packages and Options Gap Analysis.

Planowany przebieg:

1. Przejrzeć pakiety i opcje opisane w siedmiu źródłach PDF.
2. Oddzielić nazwę pakietu od dostępności elementów składowych.
3. Porównać znaczenie źródła z istniejącymi relacjami wartości i dostępności.
4. Wykazać potrzebę nowej relacji tylko wtedy, gdy obecny model jest
   niewystarczający.
5. Odrzucić kody konfiguratora i kryteria zamówieniowe.
6. Wybrać jeden kontrolowany pakiet wdrożeniowy bez zgadywania danych.

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

Completed:

- PR #19: zweryfikowano siedem dokumentów PDF przez SHA-256,
- zaimportowano 300 rekordów dostępności dla siedmiu konfiguracji,
- wykorzystano 27 istniejących i 25 nowych atrybutów kanonicznych,
- zachowano 277 statusów `standard` i 23 jawne `not_available`,
- GitHub Actions Quality run #66 zakończył się powodzeniem.

### Sandero Passive Safety Availability

Completed:

- potwierdzono 17 jednoznacznych funkcji we wszystkich siedmiu PDF-ach,
- PR #20 zaimportował 119 rekordów: 112 `standard` i 7 `not_available`,
- zachowano źródłowe brzmienie i numer strony,
- nie zmieniono znaczenia pierwszych 300 obserwacji,
- koła i tapicerka pozostają poza zakresem.

### Sandero Wheel and Upholstery Value Modeling

Completed:

- PR #21 zaakceptował decyzję D-016,
- wskazano `configuration_attribute_values.csv` jako właściwą relację,
- rozdzielono rozmiar, materiał, wzór i wykończenie koła,
- zachowano tapicerkę jako wartość wariantu,
- konflikt ERALIA/TAMIA sklasyfikowano jako nierozstrzygnięty,
- import danych pozostawiono do osobnego pakietu.

### Sandero Wheel and Upholstery Value Import

Current package:

- zweryfikowano siedem PDF przez SHA-256,
- dodano `wheel_design` i `upholstery_variant`,
- przygotowano 29 wartości dla siedmiu konfiguracji,
- zachowano proweniencję strony, sekcji i źródłowego brzmienia,
- Stepway Essential otrzymał wyłącznie wspólną wartość materiału `steel`,
- wzór ERALIA/TAMIA BI-TON i wykończenie pozostają celowo bez rekordu,
- wewnętrzne kryteria zamówieniowe nie zostały zaimportowane.

Next priority:

Analiza źródłowych pakietów i opcji oraz wybór następnego małego pakietu
zgodnego z istniejącym modelem.
